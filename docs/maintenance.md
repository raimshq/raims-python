# Contrato e manutenção

## Fonte e organização

O SDK consome somente o OpenAPI público publicado em
[raimshq/openapi](https://github.com/raimshq/openapi). `contracts/source.json`
fixa revisão imutável, URL, SHA-256, versão HTTP, identidade da implantação e
quantidade de operações. O snapshot inicial cobre 68 operações. Não use o
contrato privado do Dashboard nem endpoints com publicação não confirmada.

| Fonte | Responsabilidade |
| --- | --- |
| `contracts/openapi.json` | Snapshot público imutável |
| `contracts/service-map.json` | Nomes de serviços e métodos Python |
| `scripts/generate.py` | Geração offline e conferência dos outputs |
| `scripts/check.py` | Entrada para a validação canônica de engenharia |
| `scripts/check-compatibility.py` | Conferência independente dos símbolos públicos |
| `contracts/python-api.json` | Base revisável de compatibilidade da biblioteca |
| `src/raims/_generated/contract.json` | Metadados HTTP e schemas gerados |
| `src/raims/services.py` | Métodos síncronos e assíncronos gerados |
| `src/raims/types.py` | Parâmetros TypedDict gerados |
| `src/raims/models.py` | Modelos de resposta gerados |
| `src/raims/enum_values.py` | Constantes de enums públicos geradas |
| `src/raims/_client.py` | Configuração, transporte, retries e interpretação |
| `src/raims/_validation.py` | JSON exato, validação estrutural e hidratação |
| `src/raims/_resource.py` | Respostas somente leitura |
| `src/raims/_pagination.py` | Navegação e consumo de páginas |
| `src/raims/_webhook.py` | Autenticação de entregas |
| `src/raims/_version.py` | Fonte única da versão do pacote e do cliente |

A geração confere a origem, revisão e hash, exige autenticação com chave e
cobre cada operação exatamente uma vez. Schemas não representáveis, referências
externas e operações não publicadas interrompem a geração. `--check` não grava
arquivos e recusa outputs ausentes, divergentes ou obsoletos.

## Atualizar o contrato

1. Escolha uma revisão pública aprovada e confira o manifesto de publicação.
2. Baixe o snapshot pela URL imutável e confirme o SHA-256 dos bytes.
3. Atualize `contracts/source.json` e o mapa de métodos quando necessário.
4. Execute o gerador, revise as mudanças de contrato, tipos e referência e
   valide os clientes e a distribuição conforme `CONTRIBUTING.md`.
5. Avalie compatibilidade de assinaturas, defaults, autenticação, ambiente,
   paginação, erros, idempotência, datas, valores e resultados pendentes.

O contrato HTTP `/v1` e a versão do pacote têm ciclos independentes. Uma
atualização do gerador não autoriza aceitar mudanças incompatíveis nem
substituir o snapshot por operações locais ainda não publicadas. O gerador
recusa composições que a hidratação não representa fielmente. Para aceitar
uma forma nova de schema, implemente e valide os dois lados na mesma entrega.

## Compatibilidade da biblioteca

`contracts/python-api.json` registra exports, serviços, assinaturas, campos,
propriedades somente leitura, tipos e constantes. O arquivo é independente do
snapshot HTTP e não é regravado pelo gerador.

O formato 2 também registra bases e opções de classes, obrigatoriedade de
campos herdados de `TypedDict`, opções de dataclasses e a distinção entre
métodos de instância, estáticos e de classe. Getters, setters e deleters
fazem parte da definição das propriedades. Imports e aliases são resolvidos
por módulo, sem misturar classes que tenham o mesmo nome.

Execute `python scripts/check-compatibility.py` para conferir a implementação.
Novos símbolos são admitidos; uma alteração nas definições existentes exige
revisão explícita. A comparação é conservadora para mudanças de anotações e
assinaturas. Após avaliar o impacto, use o modo `--write` para atualizar a base
deliberadamente e revise o diff. Atualizar essa base não elimina o impacto de
uma mudança incompatível para o integrador.

Edite a versão somente em `src/raims/_version.py`. O build e o User-Agent do
cliente consomem essa fonte. A base protege a existência do export da versão,
sem impedir a mudança de seu valor entre releases.

## Validação e CI

`python scripts/check.py` usa o adapter
`Developer-Toolkit/scripts/release-preflight/python_sdk.py` no workspace.
As definições mantidas pelo Toolkit materializam os arquivos executáveis
somente em `.tmp`; a validação não depende de testes deixados por outra execução.
O lock de ferramentas fixa versões e hashes, e o relatório registra a fonte
validada, as ferramentas e os resultados do pacote. Use `--prepare-tools`
somente quando precisar preparar ou restaurar o cache isolado.

A distribuição é instalada em um ambiente virtual novo, sem pacotes do
ambiente de engenharia nem acesso ao checkout pelo `PYTHONPATH`. O pip resolve
as dependências declaradas pelo wheel. Antes de instalar as ferramentas dos
testes, uma verificação exercita os status de sucesso dos clientes síncrono
e assíncrono e a assinatura de webhook usando apenas esse ambiente.
Em seguida, o gate instala o conjunto mínimo da suíte a partir do lock e
repete os testes no pacote instalado.

As regressões incluem cópias temporárias com alterações incompatíveis nos
tipos públicos e um pacote sem a dependência HTTPX. A aprovação exige que
essas alterações sejam detectadas pelo verificador correspondente. A base
revisada e os fontes do SDK permanecem inalterados durante essas provas.

As duas execuções do pytest usam configuração própria, plugins explícitos
e um ambiente sem opções `PYTEST_*` herdadas. Cada teste coletado precisa
concluir setup, execução e teardown com sucesso; coleta sem execução,
deseleção, skip e xfail impedem aprovação. O relatório registra os casos
executados, e a validação exige a mesma cobertura nos fontes e no wheel.
Regressões específicas comprovam esse controle com configurações externas
e opções que tentariam filtrar ou somente coletar os testes.

O launcher, o adapter e os scripts materializados exigem asserções ativas e
nível de otimização zero. As execuções com `-O`, `-OO` ou otimização habilitada
por `PYTHONOPTIMIZE` são recusadas. O ambiente dos subprocessos é normalizado
para `PYTHONOPTIMIZE=0`, e o relatório registra o modo do interpretador.
Uma regressão com um checker propositalmente quebrado comprova que a
otimização não pode transformar a falha do canário em aprovação.

O template `templates/ci/validate.yml` prepara esse mesmo gate em Python 3.10
e 3.14, em jobs Linux do CodeBuild existente. A variável `RAIMS_PYTHON_TOOLKIT_REF`
deve identificar o commit revisado do Toolkit por SHA completo. A validação
recusa uma referência ausente ou móvel antes de solicitar acesso ao checkout
privado. Os eventos não incluem código de pull requests de forks.

A ativação remota está pendente: exige repositório, checkouts publicados,
acessos, variável e allowlist conferidos pelo ciclo autorizado de engenharia.
O template não é um workflow executável nesta primeira distribuição de fontes.
Ele não altera infraestrutura nem publica no PyPI.

## Impacto da implementação inicial

| Comportamento | Fonte e consumidores | Verificação |
| --- | --- | --- |
| Integração Python | SDK consome o contrato público fixado | Todas as operações, tipos e instalação |
| Transporte e paginação | Clientes síncrono e assíncrono | HTTP isolado, opções, retries e cursores |
| Recebimento de webhook | Helper local do integrador | Protocolo publicado e bytes originais |
| API, CLI e SDKs existentes | Nenhuma alteração de contrato ou implementação | Snapshot consumido sem modificar os produtores |
| Persistência e migrations | Sem alteração | Nenhuma gravação em banco ou provedor |
| Atendimento e changelog | Guias do SDK e pendências em TODO | Disponibilidade pública deve ser confirmada antes de anunciar |

## Conhecimento do atendimento

A fonte responsável por orientar instalação e uso será o guia BR/EN de
integrações em `raims-developer-docs`. Ele deve explicar finalidade, uso no
servidor, requisitos, instalação confirmada, chave, permissões, ambiente,
paginação, idempotência, respostas pendentes, documentos e webhooks.
O atendimento consome esse guia pelo catálogo existente, conforme
`Raims-Chat/docs/knowledge-sources.md` no workspace.

As fontes e as instruções de instalação pelo GitHub ficam neste repositório.
A distribuição no PyPI permanece pendente. Não publique um comando de
instalação por esse registro antes de confirmar sua disponibilidade.
`TODO.md` registra as etapas de
guia público, regeneração do catálogo, validação das respostas da IA e changelog.
Não são necessários novos campos de contexto, permissões ou ferramentas de
consulta para a biblioteca; reavalie isso se o escopo público mudar.

## Publicação

A primeira entrega é restrita ao GitHub, em `raimshq/raims-python`, com versão
da biblioteca, tag e release correspondentes. O perfil `public-sdk-source`
do preflight valida Commit e Deploy, incluindo SAST, auditoria de dependências,
integridade dos fontes e o destino remoto. Não exige configuração de runners
quando a publicação não contém workflows executáveis.

A publicação no PyPI ainda não está configurada. Antes de disponibilizar uma versão,
confirme nome do pacote, titularidade, versão, commit autorizado, validações
e conteúdo do wheel/sdist. Configure a distribuição pelo fluxo de engenharia
autorizado, sem armazenar tokens nos fontes ou logs. Publicação, criação do
repositório remoto, push e releases exigem pedidos explícitos.

Após publicar, confira a versão no destino e uma instalação limpa. Atualize
o README e os guias com a disponibilidade real. Publique a nota de changelog
com a data efetiva, pelo ciclo autorizado da documentação.
