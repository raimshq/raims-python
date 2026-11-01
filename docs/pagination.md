# Pagination

`list()` retrieves one page. Normal iteration visits only the items already
received. The webhook event type list is not paginated and returns a model
with a `list` property.

```python
page = raims.customers.list({"page_size": 50})
for customer in page:
    process_customer(customer.id)

next_page = page.next_page()
previous_page = page.previous_page()
```

`len(page)` counts the current items. `page.list` contains the tuple of items,
and `page.page` contains the API metadata. `next_page()` and `previous_page()`
return `None` when there is no continuation in that direction. They preserve
filters and options and remove the cursor for the opposite direction.

## Iterate through all pages

```python
page = raims.charges.list({"customer_id": customer_id, "page_size": 100})
for charge in page.auto_paging_iter():
    process_charge(charge.id)
```

The iterator retrieves the next page only when needed. Stopping consumption
prevents further requests. With the asynchronous client, use `await` to obtain
or navigate a page and `async for` with the automatic iterator.

An empty page may have a continuation. The SDK follows `has_next` and
`next_after` even in that case; missing or repeated cursors raise
`UnexpectedResponseError`. The automatic iterator moves forward; use
`previous_page()` to go backward.

Requests do not form a snapshot of the result set. Each page may fail, reach
rate limits, or reflect concurrent changes according to the API's guarantees.
Use the cursors returned, preserve the filters, and do not send `after` and
`before` together.
