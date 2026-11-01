# Paginação

`list()` consulta uma página. Sua iteração normal percorre somente os itens
recebidos. A lista de tipos de evento de webhook não é paginada e retorna
um modelo com a propriedade `list`.

```python
page = raims.customers.list({"page_size": 50})
for customer in page:
    process_customer(customer.id)

next_page = page.next_page()
previous_page = page.previous_page()
```

`len(page)` conta os itens atuais. `page.list` contém a tupla de itens e
`page.page` contém os metadados da API. `next_page()` e `previous_page()`
retornam `None` quando não há continuação naquela direção. Eles conservam
filtros e opções e removem o cursor da direção oposta.

## Percorrer todas as páginas

```python
page = raims.charges.list({"customer_id": customer_id, "page_size": 100})
for charge in page.auto_paging_iter():
    process_charge(charge.id)
```

O iterador consulta a próxima página somente quando necessário. Interromper
o consumo impede novas buscas. No cliente assíncrono, use `await` ao obter
ou navegar uma página e `async for` no iterador automático.

Uma página vazia pode ter continuação. O SDK segue `has_next` e `next_after`
mesmo nesse caso; cursores ausentes ou repetidos geram `UnexpectedResponseError`.
O iterador automático avança; para voltar, use `previous_page()`.

As consultas não formam um snapshot do conjunto. Cada página pode falhar,
atingir rate limits ou refletir alterações concorrentes conforme as garantias
da API. Use os cursores retornados, conserve os filtros e não envie `after`
e `before` juntos.
