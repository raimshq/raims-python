# Raims Python

SDK Python para integrar aplicações de servidor com a API pública da Raims.
Oferece clientes síncrono e assíncrono, parâmetros tipados, respostas somente
leitura, paginação por cursor e verificação de assinaturas de webhook.

## Instalação pelo GitHub

Requer Python 3.10 ou superior. Os fontes e as notas de versão estão no
[GitHub](https://github.com/raimshq/raims-python/releases). A distribuição no
PyPI ainda não está disponível.

Com Git instalado, execute no ambiente da sua aplicação:

```text
python -m pip install "git+https://github.com/raimshq/raims-python.git"
```

Para atualizar essa instalação, execute novamente com atualização forçada e
teste sua integração:

```text
python -m pip install --upgrade --force-reinstall "git+https://github.com/raimshq/raims-python.git"
```

Você também pode baixar os fontes da
[release atual](https://github.com/raimshq/raims-python/releases/latest),
extrair o arquivo e instalar o diretório no ambiente da aplicação:

```text
python -m pip install /caminho/para/Raims-Python
```

O pacote importa como `raims` e utiliza HTTPX para transporte HTTP.
Atualizações futuras não são aplicadas automaticamente.

## Primeiro uso

```python
import os

from raims import RaimsClient

with RaimsClient(os.environ["RAIMS_API_KEY"]) as raims:
    page = raims.customers.list({"page_size": 20})
    for customer in page:
        process_customer(customer.id)
```

`process_customer` representa o processamento da sua aplicação. A URL-base é
`https://api.raims.com` para Sandbox e Produção. A chave define a empresa,
o ambiente e as permissões. Mantenha-a no servidor, fora do controle de versão.

## Criar uma cobrança

`customer_id`, `due_date` e `order_idempotency_key` são valores já definidos e
persistidos pela aplicação para o pedido. O vencimento usa segundos Unix UTC
e o valor usa centavos inteiros: `15000` representa R$ 150,00.

```python
from raims import RequestOptions

with RaimsClient(os.environ["RAIMS_API_KEY"]) as raims:
    charge = raims.charges.create(
        {
            "customer_id": customer_id,
            "amount_cents": 15000,
            "due_date": due_date,
            "title": "Pedido 1234",
        },
        options=RequestOptions(idempotency_key=order_idempotency_key),
    )
    response = charge.last_response
    assert response is not None
    request_id = response.request_id
```

O SDK não gera chaves de idempotência nem repete escritas automaticamente.
Se perder a resposta, conserve a mesma chave e os mesmos parâmetros e siga
as regras do endpoint para consultar ou repetir a operação. Uma resposta `202`
significa processamento pendente; consulte o recurso para acompanhar o resultado.

## Uso assíncrono

```python
from raims import AsyncRaimsClient

async def load_customers(api_key: str) -> None:
    async with AsyncRaimsClient(api_key) as raims:
        page = await raims.customers.list({"page_size": 50})
        async for customer in page.auto_paging_iter():
            await process_customer_async(customer.id)
```

`process_customer_async` representa o processamento assíncrono da aplicação.
A iteração normal de uma página acessa apenas os itens já recebidos.
`auto_paging_iter()` consulta as próximas páginas conforme o consumo.

## Serviços

| Propriedade | Recursos |
| --- | --- |
| `accounts` | Contexto da conta, número, tarifas e checkout |
| `balances` | Saldo e previsão |
| `customers` | Cadastro, consulta e exclusão de clientes |
| `charges` | Cobranças, pagamento, documentos e estornos por cobrança |
| `payment_links` | Links de pagamento e solicitação de envio por e-mail |
| `refunds` | Estornos e recibos |
| `disputes` | Contestações |
| `statements` | Extratos |
| `withdrawals` | Saques, limites, resumo e configuração automática |
| `withdrawal_destinations` | Destinos de saque |
| `webhooks` | Cadastro, saúde, pausa, teste e rotação de segredo |
| `webhook_event_types` | Tipos de evento disponíveis |
| `simulations.charges` | Simulações de cobrança com chave Sandbox |
| `simulations.refunds` | Simulações de estorno com chave Sandbox |

Os serviços oferecem `create`, `retrieve`, `update`, `delete` e `list` conforme
as operações disponíveis. A [referência](docs/reference.md) detalha cada método.

## Documentação

- [Configuração, respostas e documentos](docs/usage.md)
- [Paginação](docs/pagination.md)
- [Erros, idempotência e retries](docs/errors-and-retries.md)
- [Recebimento de webhooks](docs/webhooks.md)
- [Manutenção e contrato](docs/maintenance.md)
- [Contribuição](CONTRIBUTING.md) e [segurança](SECURITY.md)
- [API pública](https://docs.raims.com/br/api)

Distribuído sob a licença [MIT](LICENSE).
