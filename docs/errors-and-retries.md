# Erros, idempotência e retries

## Tratar falhas

```python
from raims import ApiError, ConnectionError, RateLimitError

try:
    customer = raims.customers.retrieve(customer_id)
except RateLimitError as error:
    retry_after = error.retry_after
    request_id = error.request_id
except ConnectionError:
    handle_uncertain_response()
except ApiError as error:
    status = error.status_code
    code = error.code
```

Os handlers representam o tratamento da aplicação. Decida pelo status e por
`error.code`; mensagens de diagnóstico da API podem mudar. Detalhes completos
estão em `api_error` e na resposta explícita em `last_response`. Eles podem
conter dados sensíveis; `str` e `repr` das falhas emitidas pelo SDK não incluem
o texto nem o corpo recebido.

| Exceção | Condição |
| --- | --- |
| `InvalidRequestError` | HTTP 400, 405, 413, 415 ou 422 |
| `AuthenticationError` | HTTP 401 |
| `PermissionError` | HTTP 403 |
| `NotFoundError` | HTTP 404 |
| `ConflictError` | HTTP 409 |
| `RateLimitError` | HTTP 429 |
| `ApiError` | Demais falhas HTTP, inclusive 5xx |
| `ConnectionError` | Timeout ou falha HTTPX de transporte |
| `UnexpectedResponseError` | Redirect, sucesso não documentado, JSON ou estrutura inválidos |
| `SignatureVerificationError` | Falha na autenticação de webhook |

Todas derivam de `RaimsError`. Argumentos inválidos usam `ValueError` ou
`TypeError` do Python. Uma borda pode retornar HTML sem envelope; nesse caso,
`api_error` e `code` são `None`. A resposta HTTP permanece acessível.

## Idempotência

Forneça `RequestOptions(idempotency_key=...)` somente nos endpoints que
declaram suporte. A chave aceita de 1 a 255 caracteres ASCII visíveis, sem
espaços. O SDK a envia exatamente como recebida e não a gera automaticamente.
Uma chave em operação sem suporte é recusada antes do envio HTTP.

Gere e persista a identidade da intenção antes de executar a operação. Após
perder a resposta, conserve a chave e os parâmetros, incluindo datas e valores.
Consulte o recurso e a [política da API](https://docs.raims.com/br/api/idempotencia)
para decidir por outra tentativa. Uma falha de conexão não confirma que a
escrita deixou de ser processada. `IDEMPOTENCY_RESULT_UNKNOWN` exige
reconciliação; não troque a chave para repetir a intenção financeira.

## Retries de leitura

O padrão é zero. `max_network_retries` aceita até cinco tentativas adicionais
para GET/HEAD, em falhas de conexão ou HTTP 408, 429, 500, 502, 503 e 504.
O intervalo usa backoff exponencial com jitter entre 250 ms e 2 s.
`Retry-After` pode ampliar a espera até 30 s; acima disso, a falha é devolvida
para que a aplicação reagende a leitura. O header aceita segundos ou data HTTP.

POST, PATCH, PUT e DELETE não são repetidos automaticamente, mesmo com
idempotência e retries configurados. `202` também não inicia outra tentativa
nem uma consulta automática do resultado.
