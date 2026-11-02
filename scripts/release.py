"""Verify approved Python distributions before publishing or checking PyPI."""

import argparse
import ast
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
REPOSITORY = 'raimshq/raims-python'
PACKAGE = 'raims'
WORKFLOW = '.github/workflows/validate.yml'
JOBS = {'validatePython (3.10.22)': ('python-sdk-check-3.10.22', 'Run the canonical Python SDK checks'),
        'validatePython (3.14.10)': ('python-sdk-check-3.14.10', 'Run the canonical Python SDK checks'),
        'securityLinux': ('python-sdk-security', 'Run the canonical SDK security checks')}
SHA = re.compile(r'[a-f0-9]{40}')
VERSION = re.compile(r'(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)')
MAX_DOWNLOAD = 20 * 1024 * 1024
PYPI_MINT = 'https://pypi.org/_/oidc/mint-token'
PYPI_UPLOAD = 'https://upload.pypi.org/legacy/'
PUBLISHER_VERSION = '7.0.0'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(source, *args):
    result = subprocess.run(['git', '-C', str(source), *args], check=False, capture_output=True, text=True, timeout=60)
    require(result.returncode == 0, 'Release source identity could not be verified.')
    return result.stdout.strip()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None


def public_download(url):
    parsed = urllib.parse.urlsplit(url)
    require(parsed.scheme == 'https' and parsed.hostname in {'github.com', 'files.pythonhosted.org'},
            'Unexpected public distribution origin.')
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Raims-Python-Release'}), timeout=60) as response:
        data = response.read(MAX_DOWNLOAD + 1)
    require(len(data) <= MAX_DOWNLOAD, 'Distribution exceeds the allowed size.')
    return data


def github(endpoint, binary=False):
    token = os.environ.get('GITHUB_TOKEN')
    require(token, 'A read-only GitHub token is required for release verification.')
    headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
               'User-Agent': 'Raims-Python-Release', 'X-GitHub-Api-Version': '2022-11-28'}
    request = urllib.request.Request('https://api.github.com/repos/' + REPOSITORY + '/' + endpoint, headers=headers)
    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(request, timeout=60) as response:
            raw = response.read(MAX_DOWNLOAD + 1)
    except urllib.error.HTTPError as error:
        require(binary and error.code in {301, 302, 303, 307, 308}, 'GitHub release metadata could not be read.')
        destination = error.headers.get('Location', '')
        url = urllib.parse.urlsplit(destination)
        require(url.scheme == 'https' and url.hostname and
                (url.hostname.endswith('.blob.core.windows.net') or url.hostname.endswith('.githubusercontent.com')
                 or url.hostname.endswith('.actions.githubusercontent.com')),
                'Unexpected artifact download origin.')
        # The signed asset URL does not receive the repository token.
        with urllib.request.urlopen(urllib.request.Request(destination, headers={'User-Agent': 'Raims-Python-Release'}), timeout=60) as response:
            raw = response.read(MAX_DOWNLOAD + 1)
    require(len(raw) <= MAX_DOWNLOAD, 'GitHub artifact exceeds the allowed size.')
    return raw if binary else json.loads(raw)


def context(source):
    require(os.environ.get('GITHUB_REPOSITORY') == REPOSITORY and os.environ.get('GITHUB_EVENT_NAME') == 'release',
            'This publication accepts only the official repository release event.')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
    release = event.get('release', {})
    require(event.get('action') == 'published' and release.get('draft') is False and release.get('prerelease') is False,
            'Only a published stable release can be uploaded.')
    tree = ast.parse((source / 'src/raims/_version.py').read_text(encoding='utf-8'))
    versions = [node.value.value for node in tree.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == '__version__' for target in node.targets)
                and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)]
    require(len(versions) == 1 and VERSION.fullmatch(versions[0]), 'The SDK must have one stable version.')
    version = versions[0]
    tag = 'v' + version
    require(release.get('tag_name') == tag and os.environ.get('GITHUB_REF') == 'refs/tags/' + tag,
            'The release tag and SDK version differ.')
    head = git(source, 'rev-parse', 'HEAD')
    require(SHA.fullmatch(head) and head == os.environ.get('GITHUB_SHA')
            and git(source, 'rev-parse', 'refs/tags/' + tag + '^{commit}') == head,
            'The checked-out release commit differs.')
    require(not git(source, 'status', '--porcelain', '--untracked-files=all'), 'Release sources must be clean.')
    repo = github('')
    require(repo.get('full_name') == REPOSITORY and repo.get('private') is False and repo.get('default_branch') == 'main',
            'The repository visibility or default branch differs.')
    git(source, 'merge-base', '--is-ancestor', head, 'origin/main')
    current = github('releases/' + str(release.get('id')))
    require(current.get('id') == release.get('id') and current.get('tag_name') == tag
            and current.get('draft') is False and current.get('prerelease') is False,
            'The public release changed.')
    return {'sourceRevision': head, 'version': version, 'tag': tag, 'releaseId': current['id'],
            'publishedAt': current['published_at'], 'release': current}


def validation(head, _published, wait_seconds=600):
    deadline = time.monotonic() + wait_seconds
    while True:
        value = github('actions/workflows/validate.yml/runs?head_sha=' + head + '&per_page=100&page=1')
        rows = value.get('workflow_runs', [])
        require(isinstance(rows, list) and type(value.get('total_count')) is int, 'Validation history is incomplete.')
        if rows and rows[0].get('status') == 'completed':
            run = rows[0]
            break
        require(time.monotonic() < deadline, 'Validation of this exact commit did not finish within the allowed wait.')
        print('Waiting for validation of the release commit.', flush=True)
        time.sleep(15)
    require(run.get('head_sha') == head and run.get('path') == WORKFLOW and run.get('name') == 'Validate Python SDK'
            and run.get('status') == 'completed' and run.get('conclusion') == 'success'
            and run.get('event') in {'push', 'workflow_dispatch'}
            and run.get('repository', {}).get('full_name') == REPOSITORY
            and run.get('head_repository', {}).get('full_name') == REPOSITORY,
            'Successful validation of this exact commit is required.')
    identifier, attempt = run.get('id'), run.get('run_attempt')
    require(type(identifier) is int and identifier > 0 and type(attempt) is int and attempt > 0,
            'Validation attempt identity is incomplete.')
    result = github(f'actions/runs/{identifier}/attempts/{attempt}/jobs?per_page=100&page=1')
    jobs = result.get('jobs', [])
    require(result.get('total_count') == len(jobs) == 3 and {job.get('name') for job in jobs} == set(JOBS),
            'The complete Python validation matrix is required.')
    for job in jobs:
        suffix, step_name = JOBS[job['name']]
        require(job.get('status') == 'completed' and job.get('conclusion') == 'success'
                and job.get('labels') and set(job['labels']) == {f'codebuild-raims-github-actions-{identifier}-{attempt}', suffix}
                and len(job['labels']) == 2 and isinstance(job.get('runner_name'), str)
                and re.fullmatch(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}', job['runner_name'])
                and job.get('runner_group_name'), 'A required AWS validation job did not pass.')
        canonical = [step for step in job.get('steps', []) if step.get('name') == step_name]
        require(len(canonical) == 1 and canonical[0].get('status') == 'completed'
                and canonical[0].get('conclusion') == 'success', 'The canonical validation step did not pass.')
    return {'validationRunId': identifier, 'validationRunAttempt': attempt}


def artifact_files(context_value, validation_value):
    run, attempt = validation_value['validationRunId'], validation_value['validationRunAttempt']
    response = github(f'actions/runs/{run}/artifacts?per_page=100&page=1')
    require(response.get('total_count', 1001) <= 100 and isinstance(response.get('artifacts'), list),
            'Validation artifact inventory is incomplete.')
    name = f'raims-python-validation-{run}-{attempt}-3.14.10'
    found = [artifact for artifact in response['artifacts'] if artifact.get('name') == name]
    require(len(found) == 1 and found[0].get('expired') is False
            and found[0].get('workflow_run', {}).get('id') == run
            and found[0].get('workflow_run', {}).get('head_sha') == context_value['sourceRevision'],
            'The approved distribution artifact is missing.')
    artifact = found[0]
    raw = github('actions/artifacts/' + str(artifact['id']) + '/zip', binary=True)
    require(artifact.get('digest') == 'sha256:' + digest(raw), 'The GitHub Actions artifact digest differs.')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        version = context_value['version']
        wheel, sdist = f'raims-{version}-py3-none-any.whl', f'raims-{version}.tar.gz'
        expected = {'distribution-manifest.json', 'dist/' + wheel, 'dist/' + sdist}
        require(set(names) == expected and len(names) == 3
                and sum(item.file_size for item in archive.infolist()) <= MAX_DOWNLOAD,
                'The canonical artifact contains unexpected entries.')
        manifest = json.loads(archive.read('distribution-manifest.json'))
        files = {wheel: archive.read('dist/' + wheel), sdist: archive.read('dist/' + sdist)}
        require(set(manifest) == {'package', 'sourceRevision', 'toolkitRevision', 'pythonVersion', 'files'}
                and manifest.get('package') == PACKAGE and manifest.get('sourceRevision') == context_value['sourceRevision']
                and manifest.get('toolkitRevision') == os.environ.get('RAIMS_PYTHON_TOOLKIT_REF')
                and manifest.get('pythonVersion') == '3.14.10'
                and manifest.get('files') == {name: digest(raw) for name, raw in files.items()},
                'The canonical report and distribution bytes differ.')
    return files, artifact['id']


def upload_release_asset(identifier, name, raw):
    token = os.environ.get('GITHUB_TOKEN')
    require(token and type(identifier) is int and identifier > 0 and Path(name).name == name,
            'A release asset upload could not be authorized.')
    endpoint = 'https://uploads.github.com/repos/' + REPOSITORY + '/releases/' + str(identifier) + '/assets?name=' + urllib.parse.quote(name, safe='')
    request = urllib.request.Request(endpoint, data=raw, method='POST', headers={
        'Authorization': 'Bearer ' + token, 'Content-Type': 'application/octet-stream',
        'User-Agent': 'Raims-Python-Release', 'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'})
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=60) as response:
            require(response.status == 201, 'Release asset creation failed.')
            response.read(65536)
    except (OSError, RuntimeError):
        # An uncertain write is read back before another upload can be attempted.
        current = github('releases/' + str(identifier))
        existing = [asset for asset in current.get('assets', []) if asset.get('name') == name]
        require(len(existing) == 1 and public_download(existing[0]['browser_download_url']) == raw,
                'Release asset creation was not confirmed; inspect the release before retrying.')


def release_files(value, files, create_missing=False):
    release = github('releases/' + str(value['releaseId']))
    rows = release.get('assets', [])
    assets = {asset['name']: asset for asset in rows}
    expected = set(files) | {'SHA256SUMS'}
    require(len(assets) == len(rows) and set(assets).issubset(expected),
            'The GitHub release contains unexpected or duplicate assets.')
    checksum_expected = ''.join(digest(files[name]) + '  ' + name + '\n' for name in sorted(files)).encode('utf-8')
    complete = dict(files, SHA256SUMS=checksum_expected)
    for name, raw in complete.items():
        if name in assets:
            require(public_download(assets[name]['browser_download_url']) == raw,
                    'An existing release asset differs from the approved CI bytes.')
    missing = set(complete) - set(assets)
    require(not missing or create_missing, 'The approved distributions are missing from the GitHub release.')
    for name in sorted(missing):
        upload_release_asset(value['releaseId'], name, complete[name])
    if missing:
        current = github('releases/' + str(value['releaseId']))
        rows = current.get('assets', [])
        assets = {asset['name']: asset for asset in rows}
    require(len(assets) == len(rows) and set(assets) == expected,
            'The GitHub release must contain exactly wheel, sdist, and SHA256SUMS.')
    checksum_raw = public_download(assets['SHA256SUMS']['browser_download_url'])
    checksums = {}
    for line in checksum_raw.decode('utf-8').splitlines():
        match = re.fullmatch(r'([a-f0-9]{64})  ([A-Za-z0-9_.-]+)', line)
        require(match and match[2] not in checksums, 'Release checksums are malformed.')
        checksums[match[2]] = match[1]
    require(set(checksums) == set(files), 'Release checksum inventory differs.')
    for name, expected_bytes in files.items():
        raw = public_download(assets[name]['browser_download_url'])
        require(raw == expected_bytes and checksums[name] == digest(raw),
                'A release distribution differs from the approved CI bytes.')


def indexed_files(version, files):
    try:
        with urllib.request.urlopen('https://pypi.org/pypi/' + PACKAGE + '/' + version + '/json', timeout=30) as response:
            published = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return set()
        raise
    require(published.get('info', {}).get('name') == PACKAGE and published.get('info', {}).get('version') == version,
            'PyPI package identity differs.')
    rows = published.get('urls', [])
    urls = {item['filename']: item for item in rows}
    require(len(urls) == len(rows) and set(urls).issubset(files), 'PyPI distribution inventory differs.')
    for name, item in urls.items():
        require(item.get('digests', {}).get('sha256') == digest(files[name])
                and public_download(item['url']) == files[name], 'PyPI distribution bytes differ.')
    return set(urls)


def publisher_environment():
    allowed = {'PATH', 'HOME', 'USERPROFILE', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'TMPDIR',
               'APPDATA', 'LOCALAPPDATA', 'LD_LIBRARY_PATH', 'LANG', 'LC_ALL'}
    environment = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    environment.update(PYTHONDONTWRITEBYTECODE='1', PYTHONOPTIMIZE='0', PIP_CONFIG_FILE=os.devnull,
                       PIP_DISABLE_PIP_VERSION_CHECK='1', PYTHON_KEYRING_BACKEND='keyring.backends.null.Keyring')
    return environment


def publisher_tools(source, artifact):
    lock = source / 'scripts/publish-requirements.txt'
    text = lock.read_text(encoding='utf-8')
    pins = dict(re.findall(r'^([A-Za-z0-9_.-]+)==([^\s\\;]+)', text, re.MULTILINE))
    require(pins.get('twine') == PUBLISHER_VERSION and len(pins) == 27,
            'Publisher dependency lock differs.')
    for line in text.splitlines():
        require(not line or line.startswith('#') or re.fullmatch(r'[A-Za-z0-9_.-]+==[^\s\\;]+ \\', line)
                or re.fullmatch(r'    --hash=sha256:[a-f0-9]{64}(?: \\)?', line),
                'Publisher requirements contain an unsupported directive.')
    audited = []
    for name, version in sorted(pins.items()):
        url = 'https://pypi.org/pypi/' + urllib.parse.quote(name, safe='') + '/' + urllib.parse.quote(version, safe='') + '/json'
        try:
            with urllib.request.build_opener(NoRedirect).open(url, timeout=30) as response:
                metadata = json.loads(response.read(2 * 1024 * 1024))
        except (OSError, ValueError) as error:
            raise RuntimeError('Publisher dependency advisory lookup failed.') from error
        findings = metadata.get('vulnerabilities')
        require(isinstance(findings, list) and not any(not item.get('withdrawn') for item in findings),
                'A publisher dependency has an unresolved advisory: ' + name)
        audited.append({'name': name, 'version': version, 'vulnerabilities': 0})
    environment = publisher_environment()
    temporary = artifact / 'publisher-temp'
    temporary.mkdir()
    environment.update(PIP_CACHE_DIR=str(artifact / 'publisher-pip-cache'),
                       TEMP=str(temporary), TMP=str(temporary), TMPDIR=str(temporary))
    venv = artifact / 'publisher-venv'
    require(not venv.exists(), 'Use a fresh isolated publisher environment.')
    commands = [[sys.executable, '-I', '-m', 'venv', str(venv)]]
    python = venv / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    commands.extend([
        [str(python), '-I', '-m', 'pip', 'install', '--disable-pip-version-check', '--no-input', '--only-binary=:all:',
         '--require-hashes', '--index-url', 'https://pypi.org/simple', '-r', str(lock)],
        [str(python), '-I', '-m', 'pip', 'check'],
    ])
    for command in commands:
        result = subprocess.run(command, check=False, cwd=str(artifact), env=environment,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
        require(result.returncode == 0, 'Pinned publisher environment preparation failed.')
    probe = subprocess.run([str(python), '-I', '-c',
                            'import importlib.metadata,json; print(json.dumps({d.metadata["Name"]:d.version for d in importlib.metadata.distributions()}))'],
                           check=False, cwd=str(artifact), env=environment, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=30)
    require(probe.returncode == 0, 'Publisher installation identity is incomplete.')
    def normalize(name):
        return re.sub(r'[-_.]+', '-', name).lower()
    installed = {normalize(name): version for name, version in json.loads(probe.stdout).items() if normalize(name) not in {'pip', 'setuptools'}}
    require(installed == {normalize(name): version for name, version in pins.items()},
            'Publisher installation differs from the reviewed dependency closure.')
    (artifact / 'publisher-tool-audit.json').write_text(json.dumps({'status': 'pass', 'requirementsSha256': digest(lock.read_bytes()),
                   'packages': audited, 'publisher': 'twine', 'version': PUBLISHER_VERSION}, indent=2) + '\n', encoding='utf-8')
    return python, environment


def mask_secret(value):
    require(isinstance(value, str) and 20 <= len(value) <= 20000
            and re.fullmatch(r'[A-Za-z0-9._~+/=-]+', value), 'Registry credential format is invalid.')
    print('::add-mask::' + value, flush=True)
    return value


def credential_json(request, label):
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
            require(response.status == 200, label + ' request failed.')
            raw = response.read(65537)
        require(len(raw) <= 65536, label + ' response is too large.')
        return json.loads(raw)
    except (OSError, ValueError, RuntimeError):
        # Authentication responses and URLs must never reach the release log.
        raise RuntimeError(label + ' exchange failed.') from None


def pypi_credential():
    require(os.environ.get('GITHUB_ACTIONS') == 'true', 'Trusted publication requires GitHub Actions.')
    raw_url = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL', '')
    try:
        url = urllib.parse.urlsplit(raw_url)
        port = url.port
    except ValueError:
        raise RuntimeError('Unexpected GitHub OIDC request origin.') from None
    require(url.scheme == 'https' and url.hostname == 'vstoken.actions.githubusercontent.com'
            and port in (None, 443) and url.username is None and url.password is None
            and not url.fragment and url.path.endswith('/idtoken'), 'Unexpected GitHub OIDC request origin.')
    query = urllib.parse.parse_qsl(url.query, keep_blank_values=True)
    require(not any(key == 'audience' for key, _ in query), 'GitHub OIDC audience must be set by the publisher.')
    query.append(('audience', 'pypi'))
    endpoint = urllib.parse.urlunsplit((url.scheme, url.netloc, url.path, urllib.parse.urlencode(query), ''))
    request_token = mask_secret(os.environ.get('ACTIONS_ID_TOKEN_REQUEST_TOKEN'))
    response = credential_json(urllib.request.Request(endpoint, headers={'Authorization': 'Bearer ' + request_token,
                               'User-Agent': 'Raims-Python-Release'}), 'GitHub OIDC')
    oidc = mask_secret(response.get('value'))
    require(oidc.count('.') == 2, 'GitHub OIDC token format is invalid.')
    minted = credential_json(urllib.request.Request(PYPI_MINT, data=json.dumps({'token': oidc}).encode('utf-8'),
                             headers={'Content-Type': 'application/json', 'User-Agent': 'Raims-Python-Release'},
                             method='POST'), 'PyPI')
    token = mask_secret(minted.get('token'))
    require(token.startswith('pypi-'), 'PyPI credential format is invalid.')
    return token


def publish(source, artifact, version, files):
    indexed = indexed_files(version, files)
    pending = set(files) - indexed
    if not pending:
        return
    # Package bytes and the full dependency closure are checked before OIDC.
    python, environment = publisher_tools(source, artifact)
    pending = set(files) - indexed_files(version, files)
    destination = artifact / 'to-publish'
    require({path.name for path in destination.iterdir()} == pending
            and all((destination / name).read_bytes() == files[name] for name in pending),
            'Pending distribution bytes changed before authentication.')
    if not pending:
        return
    require(git(source, 'rev-parse', 'HEAD') == os.environ.get('GITHUB_SHA')
            and not git(source, 'status', '--porcelain', '--untracked-files=all'),
            'Release sources changed during publisher preparation.')
    credential = pypi_credential()
    environment.update(TWINE_USERNAME='__token__', TWINE_PASSWORD=credential, TWINE_NON_INTERACTIVE='1')
    try:
        result = subprocess.run([str(python), '-I', '-m', 'twine', 'upload', '--non-interactive', '--disable-progress-bar',
                                 '--repository-url', PYPI_UPLOAD, *[str(destination / name) for name in sorted(pending)]],
                                check=False, cwd=str(artifact), env=environment, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=300)
    finally:
        environment.pop('TWINE_PASSWORD', None)
    require(result.returncode == 0, 'PyPI upload did not complete; verify registry state before retrying.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'verify', 'publish', 'confirm'])
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--artifact', type=Path, required=True)
    args = parser.parse_args()
    source, artifact = args.source.resolve(), args.artifact.resolve()
    workspace = Path(os.environ['GITHUB_WORKSPACE']).resolve()
    artifact.relative_to(workspace / '.tmp/raims-python-sdk')
    value = context(source)
    previous = validation(value['sourceRevision'], value['publishedAt'])
    files, identifier = artifact_files(value, previous)
    release_files(value, files, create_missing=args.command == 'prepare')
    manifest = {key: value[key] for key in ['sourceRevision', 'version', 'tag', 'releaseId', 'publishedAt']}
    manifest.update(repository=REPOSITORY, package=PACKAGE, **previous, validationArtifactId=identifier,
                    files={name: digest(raw) for name, raw in files.items()})
    if args.command == 'prepare':
        require(not artifact.exists(), 'Use a fresh publication artifact directory.')
        (artifact / 'dist').mkdir(parents=True)
        for name, raw in files.items():
            (artifact / 'dist' / name).write_bytes(raw)
        (artifact / 'release-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    else:
        saved = json.loads((artifact / 'release-manifest.json').read_text(encoding='utf-8'))
        require(saved == manifest and {path.name for path in (artifact / 'dist').iterdir()} == set(files),
                'The publication manifest changed.')
        require(all((artifact / 'dist' / name).read_bytes() == raw for name, raw in files.items()),
                'The publication distributions changed.')
    if args.command == 'verify':
        indexed = indexed_files(value['version'], files)
        pending = set(files) - indexed
        destination = artifact / 'to-publish'
        require(not destination.exists(), 'Use a fresh verified publication directory.')
        destination.mkdir()
        for name in sorted(pending):
            (destination / name).write_bytes(files[name])
        if os.environ.get('GITHUB_OUTPUT'):
            with Path(os.environ['GITHUB_OUTPUT']).open('a', encoding='utf-8') as output:
                output.write('publishRequired=' + ('true' if pending else 'false') + '\n')
    if args.command == 'confirm':
        for attempt in range(6):
            if indexed_files(value['version'], files) == set(files):
                break
            if attempt == 5:
                raise RuntimeError('The complete approved PyPI release was not indexed.')
            time.sleep(5)
    if args.command == 'publish':
        publish(source, artifact, value['version'], files)
    print(json.dumps({'status': 'pass', 'command': args.command, **manifest}))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
