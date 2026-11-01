# Contribuir

Leia `AGENTS.md`, o README e o [guia de manutenção](docs/maintenance.md).
Preserve nomes JSON, assinaturas públicas, precisão dos valores, isolamento de
credenciais e a distinção entre resultado aceito e operação concluída.

## Validação completa

Na raiz do SDK, usando Python 3.10 ou superior, prepare as ferramentas na
primeira execução e depois execute o mesmo gate sem a opção de preparo:

```text
python scripts/check.py --prepare-tools
python scripts/check.py
```

O comando usa o validador canônico do checkout vizinho do Developer Toolkit.
Ele recria as suítes e os consumidores em `.tmp`, confere geração,
compatibilidade, lint, tipos e regressões, constrói wheel e sdist e valida uma
instalação limpa do wheel. A auditoria pip-audit confere as dependências runtime
efetivamente instaladas, incluindo transitivas. As ferramentas têm versões e
hashes fixados. O cache é separado por versão menor do Python.

A instalação do wheel ocorre em um ambiente virtual novo, sem herdar os
pacotes das ferramentas. Primeiro, o gate instala somente o wheel e suas
dependências declaradas e exercita as operações e os webhooks. Depois,
acrescenta apenas as ferramentas da suíte, fixadas por versão e hash, e
repete os testes nesse ambiente. Um pacote de prova sem a dependência HTTPX
precisa ser recusado para que a validação seja aprovada.

A execução da suíte usa configuração e plugins controlados pelo gate e
descarta variáveis `PYTEST_*` herdadas da estação. O relatório precisa
confirmar setup, execução e teardown de cada teste, sem seleção parcial,
skip ou xfail. O código de saída zero, sozinho, não aprova a rodada.
Os testes dos fontes e do wheel devem executar o mesmo conjunto de casos.

O gate exige o interpretador com nível de otimização zero e asserções
habilitadas. Execute sem `-O` ou `-OO`; se `PYTHONOPTIMIZE` habilitar otimização,
remova essa configuração do processo antes de iniciar a validação. Os
subprocessos controlados usam `PYTHONOPTIMIZE=0`, e os scripts materializados
recusam execução otimizada antes de seus checks. O relatório registra esse
estado. Essa exigência pertence à validação de engenharia.

Sem o Toolkit ou as ferramentas preparadas, a execução falha e informa a
dependência ausente. Um check parcial não aprova o SDK. Para escolher um
diretório novo de resultados, use `--output` com um caminho dentro de
`C:\server\raims\.tmp\raims-python-sdk`. A rodada exige fontes estáveis até
terminar. Os relatórios e artefatos permanecem nesse diretório.

## Geração e compatibilidade

Na raiz do SDK, usando Python 3.10 ou superior:

```text
python scripts/generate.py --check
python scripts/check-compatibility.py
python -m ruff check --config pyproject.toml --no-cache .
python -m mypy --cache-dir ../.tmp/raims-python-sdk/mypy-cache src/raims
```

O gerador usa apenas o contrato fixado e não acessa a rede. Ao atualizar a
fonte, rode `python scripts/generate.py` e revise os arquivos gerados. Não
edite serviços, modelos, entradas, constantes ou metadados gerados à mão.

`contracts/python-api.json` é a base independente dos símbolos públicos da
biblioteca. A geração do OpenAPI não a altera. O check permite símbolos novos
e recusa mudanças nas definições já registradas. Mudanças de assinaturas,
anotações ou valores exigem revisão, inclusive quando a intenção for compatível.
A base também registra obrigatoriedade herdada dos campos `TypedDict`,
opções de dataclasses, vínculo de métodos, acessores de propriedades e bases.
Os símbolos são resolvidos por módulo e imports, preservando classes homônimas.
Para aceitar deliberadamente uma nova base, execute
`python scripts/check-compatibility.py --write` e revise o diff.

Os ambientes virtuais, ferramentas, testes, simuladores e relatórios devem
ficar exclusivamente em `C:\server\raims\.tmp\raims-python-sdk`, fora do
repositório. Mantenha a suíte de validação nesse diretório e execute-a com
o código do SDK no PYTHONPATH. Durante a validação, configure
`PYTHONDONTWRITEBYTECODE=1` ou direcione `PYTHONPYCACHEPREFIX` para esse mesmo
diretório temporário. Não use a API real: até chamadas Sandbox podem
acionar comunicações e integrações externas.

A validação deve abranger cada operação e status de sucesso do contrato,
clientes síncrono e assíncrono, tipos vistos pelo integrador, precisão,
null e omissão, erros, opções por requisição, paginação vazia e cíclica,
idempotência, retries de leitura, ausência de retries de escrita, webhooks,
TLS, redirects, timeouts, limites de resposta e fechamento dos recursos.
Teste a versão mínima do Python e a versão mais recente suportada.
Use transporte falso e receptores locais com limpeza em `finally`.

## Distribuição

```text
python -m build --no-isolation --outdir ../.tmp/raims-python-sdk/dist
python -m twine check ../.tmp/raims-python-sdk/dist/*
```

Confira o wheel e o sdist. Instale o wheel em um ambiente limpo, fora do
checkout, e valide imports, tipos, transporte e o contrato embarcado. O wheel
deve conter somente o pacote, os metadados de distribuição e a licença.
O sdist inclui também as fontes públicas necessárias para manutenção e geração.
Nenhum deles deve conter testes, caches, ambientes, evidências ou configurações
privadas. Não grave artefatos de build na raiz do repositório.

## Revisão

Revise todos os arquivos alterados e novos, `git diff --check`, `git diff`
e `git diff --cached`. Deixe o trabalho sem commit e sem conteúdo em staging.
Não acrescente credenciais, URLs temporárias, dados de clientes ou referências
de outras marcas como inspiração. Preserve atribuições e licenças obrigatórias.
Textos destinados a pessoas seguem a skill humanizer do workspace.

Publicação no PyPI, criação de remoto, push, releases e documentação publicada
têm autorização independente. Uma validação local aprovada não publica o SDK.

O template `templates/ci/validate.yml` prepara `Validate Python SDK` para o repositório
`raimshq/raims-python`, nos runners CodeBuild autorizados, em Python 3.10 e
3.14. Ele valida pushes do próprio repositório e execuções manuais e não publica
pacotes quando ativado. A primeira publicação no GitHub não inclui workflow
executável. A ativação depende da disponibilização dos checkouts revisados,
do acesso do GitHub App, da allowlist dos runners e de
`RAIMS_PYTHON_TOOLKIT_REF` com o SHA imutável do Toolkit que contém o gate.
Nenhuma dessas configurações remotas é aplicada pelo comando local.

Antes do commit de entrega, execute o estágio Commit do preflight do workspace
com o perfil `Raims-Python`. Execute Deploy antes de push, tag ou release.
O perfil de fontes do GitHub exige SAST completo, auditoria de dependências,
destino público correto e ausência de workflows executáveis.
