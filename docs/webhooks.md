# Receber webhooks

Autentique o corpo original antes de interpretar o evento:

```python
from raims import SignatureVerificationError, Webhook

try:
    event = Webhook.construct_event(raw_body, received_headers, webhook_secret)
except SignatureVerificationError:
    reject_request()
else:
    persist_event_atomically(event)
```

`raw_body` contém os bytes recebidos pelo servidor; `received_headers` é um
mapa com `webhook-id`, `webhook-timestamp` e `webhook-signature`.
`reject_request` e `persist_event_atomically` pertencem à aplicação. Não
reserialize o JSON: espaços, Unicode e quebras de linha fazem parte da assinatura.

Use o `secret_key` recebido ao criar ou rotacionar o webhook, guardado em cofre.
Ele é diferente da chave Bearer da API e não é retornado por consultas posteriores.

`construct_event` autentica os headers, o timestamp e a assinatura antes de
decodificar um objeto JSON. `verify_signature` faz a autenticação sem interpretar
o corpo. Nenhum deles valida as regras de negócio do evento.

O protocolo usa HMAC-SHA256 com o segredo Base62 da Raims. Headers não diferenciam
maiúsculas de minúsculas. Valores únicos em listas são aceitos; duplicatas ou
headers ambíguos são recusados. Durante uma rotação, o header pode conter várias
assinaturas `v1=` separadas por vírgula; uma assinatura válida para o segredo
configurado autentica a entrega.

O padrão de tolerância é 300 segundos para passado e futuro. Mantenha o relógio
sincronizado. `tolerance=0` exige o mesmo segundo; não desativa a proteção.
`now` permite injetar um timestamp inteiro em verificações locais.

A assinatura não impede duplicação de uma entrega válida. Antes do aceite HTTP,
confira tipo, ambiente e recurso e grave o trabalho de forma durável, atômica e
deduplicada. O `id` do corpo identifica o evento; `webhook-id` identifica a entrega.
Se a gravação falhar, retorne falha HTTP. Processe os efeitos de negócio com
idempotência. O campo `created_at` do evento usa ISO 8601 e não é o timestamp
Unix do header da tentativa.

Consulte o [guia de recebimento](https://docs.raims.com/br/integracoes/webhooks/receber-eventos)
para os eventos e as condições de entrega.
