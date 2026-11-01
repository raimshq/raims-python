# Configuração e respostas

## Clientes

```python
from raims import RaimsClient, RequestOptions

with RaimsClient(
    api_key,
    timeout=80.0,
    connect_timeout=10.0,
    max_network_retries=0,
) as raims:
    customer = raims.customers.retrieve(
        customer_id,
        options=RequestOptions(timeout=60.0),
    )
```

Cada instância mantém sua própria credencial e reutiliza conexões. Use `with`
para fechar o cliente síncrono ou `async with` para o assíncrono. Também é
possível chamar `close()` explicitamente; no cliente assíncrono, use `await`.
Os contextos também iniciam e encerram o contexto do transporte personalizado,
preservando a exceção da aplicação quando ela ocorre. `close()` encerra o
transporte fornecido ao cliente.
Use uma instância assíncrona por ciclo de vida do event loop.

| Opção | Padrão | Efeito |
| --- | --- | --- |
| `api_key` | Obrigatória | Credencial Bearer |
| `api_base` | `https://api.raims.com` | Origem HTTPS, sem caminho, query ou credenciais |
| `timeout` | `80.0` | Timeout de rede por etapa da tentativa, em segundos |
| `connect_timeout` | `10.0` | Timeout de conexão, limitado por `timeout` |
| `max_network_retries` | `0` | De zero a cinco retries adicionais somente de leitura |
| `transport` | Transporte HTTPX | `BaseTransport` síncrono ou `AsyncBaseTransport` assíncrono |
| `request_observer` | Desativado | Callback síncrono com metadados de cada tentativa |

Os timeouts devem ser maiores que zero e no máximo 300 segundos. O timeout
HTTPX limita conexão, espera por uma conexão do pool, envio e inatividade de
leitura. Não representa um prazo total para receber uma resposta em partes.
Retries somam os prazos de cada tentativa e os intervalos de espera.

HTTP é aceito somente em loopback para desenvolvimento. A origem recebe a
credencial: configure apenas destinos controlados pela sua organização.
O transporte padrão verifica TLS, não segue redirects e não utiliza proxies
definidos implicitamente pelas variáveis do processo. Para configurações
específicas de rede, forneça um transporte HTTPX configurado pela aplicação.

As opções por requisição são `api_key`, `idempotency_key`, `timeout` e
`max_network_retries`, em `RequestOptions`. Uma chave específica não altera
a credencial do cliente para chamadas posteriores. Headers arbitrários,
seleção de ambiente e OAuth não fazem parte desta versão do SDK.
Um transporte personalizado deve preservar verificação TLS e não repetir
escritas. Exceções HTTPX de transporte são convertidas em `ConnectionError`;
exceções da aplicação mantêm seu tipo.

## Respostas e tipos

```python
charge = raims.charges.retrieve(charge_id)
amount = charge.amount_cents
same_amount = charge["amount_cents"]
data = charge.to_dict()
response = charge.last_response
assert response is not None
status = response.status_code
request_id = response.request_id
```

Os modelos em `raims.models` oferecem propriedades anotadas para o editor.
As entradas em `raims.types` são `TypedDict`; dicionários comuns também podem
ser usados nas chamadas. Os valores nomeados de enums públicos ficam em
`raims.enum_values`, são gerados do contrato e têm tipos compatíveis com os
parâmetros literais das operações.

Recursos e objetos aninhados são somente leitura; listas recebidas são tuplas.
`to_dict()` retorna uma cópia com dicionários e listas. Campos futuros e novos
valores de enum são preservados. Campos opcionais ausentes continuam ausentes:
use `"campo" in resource` ou `resource.get("campo")` quando necessário.
A análise estática confere os atributos conhecidos e recusa atribuições nas
propriedades dos modelos. Para consumir um campo novo ainda não descrito pela
versão instalada, use o acesso de mapa e valide seu tipo na aplicação.
Os metadados de paginação também têm tipos gerados do contrato.

Inteiros são lidos sem arredondamento, inclusive representações JSON integrais
como `1.0` e `1e0`. Frações são preservadas como `decimal.Decimal` e recusadas
em campos declarados inteiros. O SDK não converte centavos para reais nem
altera datas, estados ou regras de negócio.

O SDK confere campos obrigatórios, tipos e nulabilidade antes de construir
o modelo. Uma estrutura incompatível gera `UnexpectedResponseError`. O corpo
da resposta é limitado a 16 MiB. `202` não inicia polling automático; `204`
sem corpo retorna `None`.

Respostas excessivamente aninhadas também são recusadas com
`UnexpectedResponseError`, inclusive quando o aninhamento estiver em um campo
novo ainda não descrito pelos modelos.

`last_response` contém status, headers, bytes originais decodificados pelo
transporte, Request-Id, `idempotency_replayed` e `retry_after`. Request-Id tem
prioridade sobre o alias X-Request-Id. Objetos aninhados não representam outra
requisição e não têm metadados próprios de resposta.

O debug padrão oculta os dados. `to_dict()`, `last_response.body`, headers e
campos acessados explicitamente podem conter dados pessoais, segredos ou URLs
temporárias. Controle o acesso e os registros desses valores na aplicação.

## Omissão e null

```python
raims.charges.update(charge_id, {"title": "Pedido atualizado"})
raims.charges.update(charge_id, {"description": None})
raims.customers.update(customer_id, {"metadata": {}})
```

Omitir um campo e enviar `None` produzem requisições diferentes. O SDK preserva
`None`, `False`, zero, texto e mapas vazios no JSON. O significado depende do
endpoint: na cobrança, `description=None` limpa a descrição; um mapa vazio de
metadata não significa apagar tudo. Para remover URLs de redirecionamento de
links de pagamento, use os respectivos campos `clear_*` definidos no contrato.

## Diagnósticos

`request_observer` recebe `RequestDiagnostics` com operação, método, caminho
parametrizado, número da tentativa, duração, status, Request-Id e decisão de
retry. O caminho não contém IDs de recursos nem query. Credenciais, corpos e
parâmetros não são enviados ao callback. O SDK não emite telemetria própria.
Exceções do observer são isoladas; uma chamada feita por ele não dispara outra
notificação recursiva ao mesmo observer.

## Documentos e imagens

`charges.retrieve_receipt`, `charges.retrieve_boleto` e
`refunds.retrieve_receipt` retornam `FinancialDocument`, com `url` e
`expires_at`. Baixe a URL temporária em um GET separado, sem Authorization,
cookies ou chave de API e sem alterar seus parâmetros. Não registre a URL.
Se ela expirar, consulte o endpoint autenticado novamente.

As operações `accounts.create_checkout_logo_upload` e
`accounts.create_checkout_favicon_upload` preparam o upload. Faça o PUT dos
bytes separadamente para `upload_url`, usando Content-Type e Content-Length
exatos, sem credencial Bearer, cookies ou redirects. Depois, aplique o ID com
`accounts.update_checkout_settings`. O SDK não envia o arquivo nem baixa URLs
externas pelo transporte autenticado.
