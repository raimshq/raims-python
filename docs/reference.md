# Referência do SDK Python

Gerada do contrato público fixado em `contracts/source.json`.

Os mesmos serviços estão disponíveis em `RaimsClient` e `AsyncRaimsClient`. Os métodos do cliente assíncrono usam `await`.

| Serviço e método | Operação HTTP | Entrada | Resposta síncrona |
| --- | --- | --- | --- |
| `accounts.retrieve_fees` | `GET /v1/accounts/fees` | - | `AccountFees` |
| `accounts.retrieve_number` | `GET /v1/accounts/account_number` | - | `AccountNumber` |
| `accounts.retrieve_checkout_settings` | `GET /v1/accounts/checkout_settings` | - | `CheckoutSettings` |
| `accounts.update_checkout_settings` | `PATCH /v1/accounts/checkout_settings` | [`UpdateCheckoutSettingsParams`](#updatecheckoutsettingsparams) | `CheckoutSettings` |
| `accounts.create_checkout_logo_upload` | `POST /v1/accounts/checkout_settings/logo_uploads` | [`CreateCheckoutLogoUploadParams`](#createcheckoutlogouploadparams) | `CheckoutAssetUpload` |
| `accounts.create_checkout_favicon_upload` | `POST /v1/accounts/checkout_settings/favicon_uploads` | [`CreateCheckoutFaviconUploadParams`](#createcheckoutfaviconuploadparams) | `CheckoutAssetUpload` |
| `accounts.delete_checkout_asset_upload` | `DELETE /v1/accounts/checkout_settings/uploads/{id}` | - | `CheckoutAssetUploadDeleted` |
| `accounts.retrieve_context` | `GET /v1/accounts/context` | - | `AccountContext` |
| `balances.retrieve` | `GET /v1/balances` | - | `Balance` |
| `balances.forecast` | `GET /v1/balances/forecast` | [`GetBalanceForecastParams`](#getbalanceforecastparams) | `BalanceForecast` |
| `charges.create` | `POST /v1/charges` | [`CreateChargeParams`](#createchargeparams) | `ChargeCreated` |
| `charges.list` | `GET /v1/charges` | [`ListChargesParams`](#listchargesparams) | `ApiList[ChargeListItem]` |
| `charges.retrieve` | `GET /v1/charges/{id}` | - | `Charge` |
| `charges.update` | `PATCH /v1/charges/{id}` | [`UpdateChargeParams`](#updatechargeparams) | `Charge` |
| `charges.revoke` | `DELETE /v1/charges/{id}` | - | `ChargeRevoked ou ChargeRevocationPending` |
| `charges.retrieve_payment` | `GET /v1/charges/{id}/payment` | - | `PaymentReceipt` |
| `charges.retrieve_receipt` | `GET /v1/charges/{id}/receipt` | - | `FinancialDocument` |
| `charges.retrieve_boleto` | `GET /v1/charges/{id}/boleto` | - | `FinancialDocument` |
| `charges.create_refund` | `POST /v1/charges/{id}/refunds` | [`CreateRefundParams`](#createrefundparams) | `Refund` |
| `charges.list_refunds` | `GET /v1/charges/{id}/refunds` | [`ListChargeRefundsParams`](#listchargerefundsparams) | `ApiList[Refund]` |
| `charges.retrieve_refund_eligibility` | `GET /v1/charges/{id}/refund_eligibility` | - | `RefundEligibility` |
| `charges.statistics` | `GET /v1/charges/statistics` | [`GetChargeStatisticsParams`](#getchargestatisticsparams) | `ChargeStatistics` |
| `customers.create` | `POST /v1/customers` | [`CreateCustomerParams`](#createcustomerparams) | `CustomerCreated` |
| `customers.list` | `GET /v1/customers` | [`ListCustomersParams`](#listcustomersparams) | `ApiList[CustomerListItem]` |
| `customers.retrieve` | `GET /v1/customers/{id}` | - | `CustomerListItem` |
| `customers.update` | `PATCH /v1/customers/{id}` | [`UpdateCustomerParams`](#updatecustomerparams) | `CustomerListItem` |
| `customers.delete` | `DELETE /v1/customers/{id}` | - | `CustomerDeleted` |
| `customers.delete_batch` | `DELETE /v1/customers` | [`DeleteCustomersBatchParams`](#deletecustomersbatchparams) | `CustomerBatchDeleted` |
| `disputes.list` | `GET /v1/disputes` | [`ListDisputesParams`](#listdisputesparams) | `ApiList[DisputeListItem]` |
| `disputes.retrieve` | `GET /v1/disputes/{id}` | - | `Dispute` |
| `payment_links.create` | `POST /v1/payment_links` | [`CreatePaymentLinkParams`](#createpaymentlinkparams) | `PaymentLink` |
| `payment_links.list` | `GET /v1/payment_links` | [`ListPaymentLinksParams`](#listpaymentlinksparams) | `ApiList[PaymentLink]` |
| `payment_links.retrieve` | `GET /v1/payment_links/{id}` | - | `PaymentLinkDetails` |
| `payment_links.update` | `PATCH /v1/payment_links/{id}` | [`UpdatePaymentLinkParams`](#updatepaymentlinkparams) | `PaymentLink` |
| `payment_links.send_email` | `POST /v1/payment_links/{id}/send_email` | - | `PaymentLinkEmailRequestAccepted` |
| `refunds.list` | `GET /v1/refunds` | [`ListRefundsParams`](#listrefundsparams) | `ApiList[Refund]` |
| `refunds.retrieve` | `GET /v1/refunds/{id}` | - | `Refund` |
| `refunds.retrieve_receipt` | `GET /v1/refunds/{id}/receipt` | - | `FinancialDocument` |
| `statements.list` | `GET /v1/statements` | [`ListStatementsParams`](#liststatementsparams) | `ApiList[Statement]` |
| `statements.retrieve` | `GET /v1/statements/{id}` | - | `Statement` |
| `webhook_event_types.list` | `GET /v1/webhook_event_types` | - | `WebhookEventTypeListResponse` |
| `webhooks.create` | `POST /v1/webhooks` | [`CreateWebhookParams`](#createwebhookparams) | `WebhookCreated` |
| `webhooks.list` | `GET /v1/webhooks` | [`ListWebhooksParams`](#listwebhooksparams) | `ApiList[Webhook]` |
| `webhooks.retrieve` | `GET /v1/webhooks/{webhook_id}` | - | `Webhook` |
| `webhooks.update` | `PATCH /v1/webhooks/{webhook_id}` | [`UpdateWebhookParams`](#updatewebhookparams) | `Webhook` |
| `webhooks.delete` | `DELETE /v1/webhooks/{webhook_id}` | - | `None` |
| `webhooks.retrieve_health` | `GET /v1/webhooks/{webhook_id}/health` | - | `WebhookHealth` |
| `webhooks.set_pause` | `PATCH /v1/webhooks/{webhook_id}/pause` | [`SetWebhookPauseParams`](#setwebhookpauseparams) | `WebhookPause` |
| `webhooks.rotate_secret` | `POST /v1/webhooks/{webhook_id}/rotate_secret` | [`RotateWebhookSecretParams`](#rotatewebhooksecretparams) | `WebhookSecretRotation` |
| `webhooks.test` | `POST /v1/webhooks/{webhook_id}/test` | - | `WebhookTestAccepted` |
| `withdrawal_destinations.list` | `GET /v1/withdrawal_destinations` | [`ListWithdrawalDestinationsParams`](#listwithdrawaldestinationsparams) | `ApiList[WithdrawalDestination]` |
| `withdrawal_destinations.retrieve` | `GET /v1/withdrawal_destinations/{id}` | - | `WithdrawalDestination` |
| `withdrawals.create` | `POST /v1/withdrawals` | [`CreateWithdrawalParams`](#createwithdrawalparams) | `Withdrawal` |
| `withdrawals.list` | `GET /v1/withdrawals` | [`ListWithdrawalsParams`](#listwithdrawalsparams) | `ApiList[Withdrawal]` |
| `withdrawals.retrieve` | `GET /v1/withdrawals/{id}` | - | `Withdrawal` |
| `withdrawals.retrieve_limits` | `GET /v1/withdrawals/limits` | - | `WithdrawalLimits` |
| `withdrawals.retrieve_summary` | `GET /v1/withdrawals/summary` | - | `WithdrawalSummary` |
| `withdrawals.retrieve_automatic_settings` | `GET /v1/withdrawals/automatic_settings` | - | `AutomaticWithdrawalSettings` |
| `withdrawals.update_automatic_settings` | `PATCH /v1/withdrawals/automatic_settings` | [`UpdateAutomaticWithdrawalSettingsParams`](#updateautomaticwithdrawalsettingsparams) | `AutomaticWithdrawalSettings` |
| `simulations.charges.confirm_payment` | `POST /v1/simulations/charges/{id}/confirm_payment` | - | `ChargeSimulation` |
| `simulations.charges.fail_payment` | `POST /v1/simulations/charges/{id}/fail_payment` | - | `ChargeSimulation` |
| `simulations.charges.configure_scenario` | `POST /v1/simulations/charges/{id}/scenario` | [`ConfigureSimulationScenarioParams`](#configuresimulationscenarioparams) | `ChargeScenario` |
| `simulations.charges.resolve_scenario` | `POST /v1/simulations/charges/{id}/resolve` | [`ResolveSimulationScenarioParams`](#resolvesimulationscenarioparams) | `ChargeScenario` |
| `simulations.charges.issue_payment` | `POST /v1/simulations/charges/{id}/issue_payment` | [`IssueSimulationPaymentParams`](#issuesimulationpaymentparams) | `Charge` |
| `simulations.charges.compensate_boleto` | `POST /v1/simulations/charges/{id}/compensate_boleto` | - | `ChargeBoletoCompensation` |
| `simulations.charges.create_refund` | `POST /v1/simulations/charges/{id}/refunds` | [`CreateSimulationRefundParams`](#createsimulationrefundparams) | `Refund` |
| `simulations.refunds.complete` | `POST /v1/simulations/refunds/{id}/complete` | - | `Refund` |
| `simulations.refunds.fail` | `POST /v1/simulations/refunds/{id}/fail` | - | `Refund` |

Listagens paginadas retornam `ApiList[T]` no cliente síncrono e `AsyncApiList[T]` no assíncrono. Iterar a página não inicia outra requisição. Use `auto_paging_iter()` para percorrer as páginas seguintes. Os metadados de `page` usam o tipo gerado `PageInfo`.

Entradas usam os nomes JSON da API. Omitir um campo e enviar `None` são ações distintas. As respostas preservam campos e valores novos; os valores monetários continuam em centavos inteiros e as datas dos recursos em segundos Unix UTC.

## Parâmetros de entrada

Os campos e as descrições abaixo vêm do contrato público fixado. `None` corresponde a `null`; um campo opcional pode ser omitido. Objetos e listas aninhados têm tipos próprios em `raims.types`.

### UpdateChargeParams

Atualizar cobrança existente. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `title` | `str \| None` | Não | Título da cobrança. Omita para manter o título atual; envie null ou texto vazio para removê-lo. |
| `description` | `str \| None` | Não | Descrição da cobrança. Omita para manter a descrição atual; envie null ou texto vazio para removê-la. |
| `external_reference` | `str \| None` | Não | Referência do pedido ou da cobrança no seu sistema. Omita para manter o valor atual; envie null ou texto vazio para removê-lo. Pode ser repetida em outras cobranças e é independente da referência do cliente. |
| `metadata` | `dict[str, str \| None] \| None` | Não | Dados de integração associados ao recurso. Informe pares de chave e texto. Chaves diferenciam maiúsculas de minúsculas. Omitir ou enviar {} preserva os dados; null remove todos os pares, e null em uma chave remove somente essa chave. Texto vazio é um valor válido. |

### ListChargesParams

Listar cobranças. Argumento `params`: opcional.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `page_size` | `int` | Não | Quantidade de cobranças por página. Inteiros positivos acima do máximo usam o máximo. Valor omitido, vazio, zero, negativo ou inválido usa 10. |
| `after` | `str` | Não | Copie page.next_after da resposta anterior para avançar. Mantenha os mesmos filtros e a ordenação; não envie before junto. Deixe vazio para começar a listagem. |
| `before` | `str` | Não | Copie page.previous_before da resposta anterior para voltar. Mantenha os mesmos filtros e a ordenação; não envie after junto. Deixe vazio se não quiser voltar. |
| `identifier` | `str` | Não | Filtra pelo ID completo da cobrança. Se não houver correspondência, list será vazio. |
| `customer_id` | `str` | Não | Filtra pelo ID público completo do cliente, retornado no cadastro ou na consulta. O vínculo permanece o mesmo se nome ou e-mail mudar. Pode ser combinado com os demais filtros; mantenha o mesmo customer_id ao mudar de página. Um ID válido sem cobranças na empresa e no ambiente autenticado retorna list vazio. Vazio ou ausência não aplica o filtro. |
| `external_reference` | `str` | Não | Filtra pela referência atual da cobrança no seu sistema, com igualdade do valor completo, incluindo maiúsculas, minúsculas e acentos. Vazio ou ausência não aplica o filtro. Pode ser combinado com os demais filtros; preserve o valor ao navegar por cursor. Após criar ou editar uma cobrança, pode levar alguns segundos para a busca refletir a referência. |
| `email` | `str` | Não | Filtra pelo e-mail completo registrado na cobrança. Alterar o cadastro do cliente não altera esse e-mail. |
| `status` | `str` | Não | Filtra por um ou mais códigos separados por vírgula, como 0,1. 0 criado, 1 aguardando pagamento, 2 autorizado, 3 em processamento, 4 pago, 5 parcialmente devolvido, 6 devolvido, 7 cancelado, 8 expirado, 9 falha, 10 chargeback, 11 chargeback em análise, 12 chargeback perdido e 13 chargeback ganho. Pode levar alguns segundos para refletir alterações. |
| `payment_method` | `str` | Não | Filtra pelo meio de pagamento da cobrança: 1 para Pix e 2 para boleto. Para combinar, envie 1,2. Uma cobrança com meio indefinido pode passar a usar Pix ou boleto quando o código Pix ou boleto é gerado no checkout. A seleção na tela, por si só, não altera o filtro. |
| `created_gte` | `int` | Não | Filtra cobranças criadas a partir deste instante, inclusive, em segundos Unix UTC. Se informar created_lte, este valor deve ser menor ou igual a ele. |
| `created_lte` | `int` | Não | Filtra cobranças criadas até este instante, inclusive, em segundos Unix UTC. |
| `due_gte` | `int` | Não | Filtra cobranças com vencimento a partir deste instante, inclusive, em segundos Unix UTC. Pode ser combinado com due_lte e os demais filtros; mantenha o valor ao mudar de página. |
| `due_lte` | `int` | Não | Filtra cobranças com vencimento até este instante, inclusive, em segundos Unix UTC. Se informar due_gte, este valor deve ser maior ou igual a ele. Pode ser usado sozinho ou com os demais filtros. |
| `paid_gte` | `int` | Não | Filtra cobranças pagas a partir deste instante, inclusive, em segundos Unix UTC. Usa a data do pagamento confirmado, mesmo quando houver estorno posterior. Cobranças sem pagamento confirmado ficam fora do resultado. Mantenha o valor ao mudar de página. |
| `paid_lte` | `int` | Não | Filtra cobranças pagas até este instante, inclusive, em segundos Unix UTC. Se informar paid_gte, este valor deve ser maior ou igual a ele. Pode ser combinado com os demais filtros. |
| `sort_key` | `Literal['amount_cents', 'created_at']` | Não | Ordena por valor em centavos ou data de criação. Se omitido, usa a ordem de cadastro; com filtro de criação, usa created_at. Mantenha a mesma ordenação ao mudar de página. |
| `sort_order` | `Literal['asc', 'desc']` | Não | Define a direção da ordenação. Com desc, a ordem padrão mostra as cobranças mais recentes primeiro. |

### CreateChargeParams

Criar nova cobrança. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `customer_id` | `str` | Sim | ID de um cliente da empresa e do ambiente autenticado. Copie o id retornado no cadastro ou na consulta. Pix direto exige CPF/CNPJ válido. Boleto direto exige nome, e-mail válido, CPF/CNPJ e endereço, incluindo CEP e número; complete esses dados no cadastro do cliente. |
| `amount_cents` | `int` | Sim | Valor da cobrança em centavos de real. Por exemplo, 10000 representa R$ 100,00. |
| `payment_method` | `Literal[0, 1, 2]` | Não | Meio da cobrança. Omitir ou enviar 0 permite escolher no checkout. Sem payment_method_types, 1 solicita Pix e 2 solicita boleto na criação, conforme os meios habilitados. Boleto usa o endereço do cliente e completa campos ausentes pelo CEP quando disponíveis. Com lista própria, envie 0 ou omita este campo; a emissão acontece após a escolha no checkout. |
| `due_date` | `int` | Sim | Vencimento em segundos Unix UTC, pelo menos cinco minutos no futuro. A data máxima é hoje mais dez anos, no calendário de São Paulo. |
| `title` | `str \| None` | Não | Título da cobrança. Você pode deixar este campo vazio. |
| `description` | `str \| None` | Não | Descrição da cobrança. Você pode deixar este campo vazio. |
| `send_email` | `bool` | Não | Com true, solicita o envio da cobrança ao e-mail do cliente e gera checkout_url. Em contas pendentes, o cliente precisa ter o mesmo e-mail principal da conta. Fora dessa condição, um e-mail ausente ou inválido impede o envio, mas permite criar a cobrança quando não houver emissão direta de boleto. Boleto direto exige e-mail válido mesmo com false. A resposta não confirma a entrega da mensagem. |
| `create_checkout` | `bool` | Não | Com true, gera o link retornado em checkout_url, sem exigir uma URL de retorno nem solicitar envio de e-mail. Com false, o link ainda é gerado quando send_email é true ou uma URL de retorno é informada. |
| `success_redirect_url` | `str \| None` | Não | URL HTTPS do seu site para retorno após a confirmação do pagamento. O redirecionamento não comprova o pagamento; consulte a cobrança para confirmá-lo. Não aceita credenciais no endereço, IP literal, localhost ou domínio Raims. Quando preenchida, gera checkout_url mesmo com send_email false. Se omitida, vazia ou null, o retorno não é definido. |
| `cancel_redirect_url` | `str \| None` | Não | URL HTTPS do seu site para o pagador voltar pelo checkout. Voltar não cancela a cobrança, o Pix ou o boleto. Não aceita credenciais no endereço, IP literal, localhost ou domínio Raims. Quando preenchida, gera checkout_url mesmo com send_email false. Se omitida, vazia ou null, o retorno não é definido. |
| `payment_method_types` | `Sequence[Literal[1, 2]] \| None` | Não | Meios permitidos para a cobrança: 1 para Pix e 2 para boleto. Omitir ou enviar null usa a configuração de checkout herdada. Informe uma lista sem repetições. A configuração própria substitui o padrão da conta; uma configuração do link pode apenas restringir essa lista. Combine com payment_method omitido ou 0. |
| `external_reference` | `str \| None` | Não | Referência do pedido ou da cobrança no seu sistema. Null, vazio ou somente espaços deixam sem referência. Pode ser repetida e não evita cobranças duplicadas. É diferente da referência do cadastro do cliente. |
| `metadata` | `dict[str, str \| None] \| None` | Não | Dados de integração associados à cobrança, em pares de chave e texto. Chaves diferenciam maiúsculas de minúsculas. Omitir, enviar null ou {} cria a cobrança sem esses dados; pares com valor null não são incluídos. Texto vazio é um valor válido. |

### CreateCustomerParams

Criar cliente. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `full_name` | `str \| None` | Não | Nome completo do pagador. |
| `tax_id` | `str` | Sim | CPF ou CNPJ válido, com ou sem pontos, barra, hífen e espaços. |
| `email` | `str \| None` | Não | E-mail do pagador. Cadastrar o e-mail não envia uma mensagem. |
| `dial_code` | `str \| None` | Não | Código de discagem internacional. Pode ser informado sem phone_local. |
| `phone_local` | `str \| None` | Não | Número de telefone sem o código de discagem, com ou sem pontuação. Pode ser informado sem dial_code. |
| `zip_code` | `str \| None` | Não | CEP do endereço, com ou sem hífen. Se street, neigh, city, uf, street_number e complement estiverem vazios, o CEP pode preencher rua, bairro, cidade e estado. O preenchimento não inclui número nem complemento. |
| `street` | `str \| None` | Não | Logradouro do endereço. |
| `street_number` | `str \| None` | Não | Número do endereço. |
| `complement` | `str \| None` | Não | Complemento do endereço. |
| `neigh` | `str \| None` | Não | Bairro do endereço. |
| `city` | `str \| None` | Não | Cidade do endereço. |
| `uf` | `str \| None` | Não | Sigla do estado, como SP. |
| `external_reference` | `str \| None` | Não | Identificador do cliente no seu sistema. Para um cliente já cadastrado, omita para manter a referência ou envie null ou texto vazio para removê-la. Use external_reference na listagem de clientes para buscar esse valor. |
| `metadata` | `dict[str, str \| None] \| None` | Não | Dados de integração associados ao recurso. Informe pares de chave e texto. Chaves diferenciam maiúsculas de minúsculas. Omitir ou enviar {} preserva os dados; null remove todos os pares, e null em uma chave remove somente essa chave. Texto vazio é um valor válido. |

### ListCustomersParams

Listar clientes. Argumento `params`: opcional.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `page_size` | `int` | Não | Quantidade de clientes por página. Inteiros positivos acima do máximo usam o máximo. Valor omitido, vazio, zero, negativo ou inválido usa 10. |
| `after` | `str` | Não | Copie page.next_after da resposta anterior para avançar. Use o cursor sem alterações, mantenha os mesmos filtros e não envie before junto. |
| `before` | `str` | Não | Copie page.previous_before da resposta anterior para voltar uma página. Mantenha os mesmos filtros e não envie after junto. |
| `identifier` | `str` | Não | Identificador público do cliente, com prefixo cus_. |
| `name` | `str` | Não | Busca pelo nome do cliente, com os cadastros mais recentes primeiro. Deixe vazio para ignorar este filtro. |
| `email` | `str` | Não | Filtra pelo e-mail completo do cliente. |
| `document` | `str` | Não | Filtra pelo CPF ou CNPJ completo do cliente, com ou sem pontos, barra, hífen e espaços. |
| `external_reference` | `str` | Não | Filtra pela referência atual do cliente no seu sistema, com igualdade do valor completo, incluindo maiúsculas, minúsculas e acentos. Pode ser combinada com os demais filtros. Após criar ou editar o cliente, a busca pode levar alguns segundos para refletir a referência. Mantenha o valor ao navegar por cursor. |

### DeleteCustomersBatchParams

Remover clientes em lote. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `identifiers` | `Sequence[str \| None]` | Sim | IDs dos clientes que deseja remover. IDs repetidos não geram mais de uma remoção. IDs inválidos ou de clientes que a chave não pode acessar aparecem em invalid. |

### UpdateCustomerParams

Atualizar cliente existente. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `full_name` | `str \| None` | Não | Nome completo do pagador. Omita para manter o valor atual; envie null ou texto vazio para removê-lo. |
| `email` | `str \| None` | Não | E-mail do pagador. Atualizar o e-mail não envia uma mensagem. Omita para manter o valor atual; envie null ou texto vazio para removê-lo. |
| `dial_code` | `str \| None` | Não | Código de discagem internacional. Pode ser informado sem phone_local. Omita para manter o valor atual; envie null ou texto vazio para removê-lo. |
| `phone_local` | `str \| None` | Não | Número de telefone sem o código de discagem, com ou sem pontuação. Pode ser informado sem dial_code. Omita para manter o valor atual; envie null ou texto vazio para removê-lo. |
| `zip_code` | `str \| None` | Não | CEP do endereço, com ou sem hífen. Atualizar o CEP não preenche os outros campos de endereço. Omita para manter o valor atual; envie null ou texto vazio para removê-lo. |
| `street` | `str \| None` | Não | Logradouro do endereço. Omita para manter o valor atual; envie null ou texto vazio para removê-lo. |
| `street_number` | `str \| None` | Não | Número do endereço. Omita para manter o valor atual; envie null ou texto vazio para removê-lo. |
| `complement` | `str \| None` | Não | Complemento do endereço. Omita para manter o valor atual; envie null ou texto vazio para removê-lo. |
| `neigh` | `str \| None` | Não | Bairro do endereço. Omita para manter o valor atual; envie null ou texto vazio para removê-lo. |
| `city` | `str \| None` | Não | Cidade do endereço. Omita para manter o valor atual; envie null ou texto vazio para removê-lo. |
| `uf` | `str \| None` | Não | Sigla do estado, como SP. Omita para manter o valor atual; envie null ou texto vazio para removê-lo. |
| `external_reference` | `str \| None` | Não | Identificador do cliente no seu sistema. Omita para manter a referência atual; envie null ou texto vazio para removê-la. Use external_reference na listagem de clientes para buscar esse valor. |
| `metadata` | `dict[str, str \| None] \| None` | Não | Dados de integração associados ao recurso. Informe pares de chave e texto. Chaves diferenciam maiúsculas de minúsculas. Omitir ou enviar {} preserva os dados; null remove todos os pares, e null em uma chave remove somente essa chave. Texto vazio é um valor válido. |

### UpdateAutomaticWithdrawalSettingsParams

Atualizar saque automático. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `enabled` | `bool` | Não | Ativa ou desativa novas tentativas de saque. Desativar não cancela saques já solicitados. |
| `minimum_amount_cents` | `int` | Não | Saldo mínimo para tentar o saque, em centavos de real. O valor retirado depende do saldo disponível e do limite Pix restante. |
| `time` | `str` | Não | Horário diário no formato HH:mm, pelo fuso de São Paulo. |

### GetBalanceForecastParams

Consultar recebimentos previstos. Argumento `params`: opcional.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `period` | `Literal['today', 'last_7_days', 'last_15_days', 'last_30_days']` | Não | Período das datas previstas de recebimento, pelo calendário de São Paulo. Inclui hoje e os dias anteriores conforme a opção. Não consulta vencimentos nem projeta os próximos dias. |

### CreateRefundParams

Solicitar estorno. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `amount_cents` | `int` | Sim | Valor solicitado para devolução, em centavos de real. Para devolver tudo, informe o valor restante mostrado na consulta de elegibilidade. |
| `description` | `str \| None` | Não | Descrição da solicitação de devolução. Você pode deixar este campo vazio. |

### ListChargeRefundsParams

Listar estornos de uma cobrança. Argumento `params`: opcional.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `page_size` | `int` | Não | Quantidade de estornos por página. Valores acima do máximo usam o máximo; ausência, vazio, texto, zero ou valor negativo usa o padrão. |
| `after` | `str` | Não | Cursor recebido em page.next_after para avançar. Copie o valor completo e mantenha a mesma cobrança. Não envie junto de before. |
| `before` | `str` | Não | Cursor recebido em page.previous_before para voltar. Copie o valor completo e mantenha a mesma cobrança. Não envie junto de after. |
| `created_gte` | `int` | Não | Filtra estornos solicitados a partir deste instante, inclusive, em segundos Unix UTC. Usa a data de criação da solicitação, sem depender da conclusão. Mantenha o valor ao mudar de página. |
| `created_lte` | `int` | Não | Filtra estornos solicitados até este instante, inclusive, em segundos Unix UTC. Se informar created_gte, este valor deve ser maior ou igual a ele. |

### GetChargeStatisticsParams

Consultar estatísticas de cobranças. Argumento `params`: opcional.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `period` | `Literal['today', 'last_7_days', 'last_15_days', 'last_30_days']` | Não | Período da consulta, pelo calendário de São Paulo. today considera hoje; last_7_days, last_15_days e last_30_days incluem hoje e os dias anteriores. A consulta aceita somente esses períodos. start_at e end_at são campos da resposta, não filtros de datas personalizadas. |

### CreateCheckoutLogoUploadParams

Preparar envio da logo. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `content_type` | `Literal['image/png', 'image/jpeg']` | Sim | Tipo de conteúdo do arquivo: image/png ou image/jpeg. |
| `file_size` | `int` | Sim | Tamanho do arquivo em bytes. |
| `width` | `int` | Sim | Largura da imagem em pixels. |
| `height` | `int` | Sim | Altura da imagem em pixels. |

### CreateCheckoutFaviconUploadParams

Preparar envio do ícone. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `content_type` | `Literal['image/png', 'image/jpeg']` | Sim | Tipo de conteúdo do arquivo: image/png ou image/jpeg. |
| `file_size` | `int` | Sim | Tamanho do arquivo em bytes. |
| `width` | `int` | Sim | Largura do ícone em pixels. Deve ser igual à altura. |
| `height` | `int` | Sim | Altura do ícone em pixels. Deve ser igual à largura. |

### UpdateCheckoutSettingsParams

Atualizar personalização do checkout. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `support_email` | `str \| None` | Não | E-mail de suporte apresentado no checkout. Omitir preserva o valor; null ou texto vazio remove o contato. |
| `hex_primary_color` | `str` | Não | Cor principal do checkout no formato #RRGGBB. Omitir preserva o valor; null ou texto vazio não são aceitos. |
| `hex_secondary_color` | `str` | Não | Cor de fundo do checkout no formato #RRGGBB. Omitir preserva o valor; null ou texto vazio não são aceitos. |
| `logo_upload_id` | `str \| None` | Não | ID retornado ao preparar o envio da logo. Envie o arquivo antes de associá-lo. Omitir preserva a imagem atual; null a remove. |
| `favicon_upload_id` | `str \| None` | Não | ID retornado ao preparar o envio do ícone. Envie o arquivo antes de associá-lo. Omitir preserva a imagem atual; null a remove. |

### ListDisputesParams

Listar contestações. Argumento `params`: opcional.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `page_size` | `int` | Não | Quantidade de contestações por página. Valores inválidos usam o padrão; valores acima do máximo usam o limite. |
| `after` | `str` | Não | Cursor de page.next_after da resposta anterior. Preserve os filtros e a ordenação; não envie junto de before. |
| `before` | `str` | Não | Cursor de page.previous_before para voltar. Preserve os filtros e a ordenação; não envie junto de after. |
| `stage` | `str` | Não | Etapas do caso separadas por vírgula: open, in_analysis, refund_in_analysis, closed, cancelled, rejected ou failed. Closed informa análise encerrada, sem confirmar decisão favorável ou devolução. |
| `charge_id` | `str` | Não | Filtra pela cobrança vinculada, usando o identificador público completo. Um ID válido sem casos acessíveis retorna uma lista vazia. |
| `disputed_amount_cents` | `int` | Não | Filtra pelo valor contestado exato, em centavos de real. Não representa o valor atualmente bloqueado. |
| `created_gte` | `int` | Não | Inclui contestações criadas a partir deste instante, em segundos Unix UTC. O limite é inclusivo. |
| `created_lte` | `int` | Não | Inclui contestações criadas até este instante, em segundos Unix UTC. O limite é inclusivo e deve ser igual ou posterior a created_gte. |
| `sort_key` | `Literal['created_at', 'disputed_amount_cents']` | Não | Campo usado para ordenar a lista: criação ou valor contestado. |
| `sort_order` | `Literal['asc', 'desc']` | Não | Ordem crescente ou decrescente do campo selecionado. |

### CreatePaymentLinkParams

Criar ou recuperar um link de pagamento. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `charge_id` | `str` | Sim | Identificador da cobrança existente. O link utiliza o cliente, o valor e o vencimento dessa cobrança. |
| `success_redirect_url` | `str \| None` | Não | URL HTTPS de retorno após o pagamento confirmado. Omitir, enviar null ou texto vazio preserva a URL existente. |
| `cancel_redirect_url` | `str \| None` | Não | URL HTTPS para voltar ao seu site. Esse retorno não cancela a cobrança. Omitir, enviar null ou texto vazio preserva a URL existente. |
| `payment_method_types` | `Sequence[Literal[1, 2]] \| None` | Não | Meios permitidos no link. Omitir preserva a configuração; null remove a configuração própria. Uma lista limita os meios do checkout e não amplia os permitidos pela cobrança. |

### ListPaymentLinksParams

Listar links de pagamento. Argumento `params`: opcional.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `page_size` | `int` | Não | Quantidade de links por página. |
| `after` | `str` | Não | Cursor recebido em page.next_after. Mantenha o mesmo filtro charge_id. |
| `before` | `str` | Não | Cursor recebido em page.previous_before. Não envie junto com after. |
| `charge_id` | `str` | Não | Identificador da cobrança cujo link você quer consultar. |

### UpdatePaymentLinkParams

Atualizar um link de pagamento. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `is_active` | `bool` | Não | Envie false para pausar o checkout e true para reativar a mesma URL. Omitir preserva o estado atual. A pausa não cancela Pix ou boleto emitidos nem prorroga o vencimento. |
| `success_redirect_url` | `str \| None` | Não | URL HTTPS de retorno após o pagamento confirmado. Omitir, enviar null ou texto vazio preserva a URL existente. Para removê-la, use clear_success_redirect_url com true, sem informar uma URL preenchida. |
| `cancel_redirect_url` | `str \| None` | Não | URL HTTPS para voltar ao seu site. Esse retorno não cancela a cobrança. Omitir, enviar null ou texto vazio preserva a URL existente. Para removê-la, use clear_cancel_redirect_url com true, sem informar uma URL preenchida. |
| `clear_success_redirect_url` | `bool` | Não | Envie true para remover o destino de retorno após o pagamento. False ou omissão não solicita remoção. Não envie true junto de success_redirect_url preenchida. |
| `clear_cancel_redirect_url` | `bool` | Não | Envie true para remover o destino de voltar ao site. False ou omissão não solicita remoção. Não envie true junto de cancel_redirect_url preenchida. |
| `payment_method_types` | `Sequence[Literal[1, 2]] \| None` | Não | Meios permitidos no link. Omitir preserva a configuração; null remove a configuração própria. Uma lista limita os meios do checkout e não amplia os permitidos pela cobrança. |

### ListRefundsParams

Listar estornos. Argumento `params`: opcional.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `page_size` | `int` | Não | Quantidade de estornos por página. Valores acima do máximo usam o máximo; ausência, vazio, texto, zero ou valor negativo usa o padrão. |
| `after` | `str` | Não | Cursor recebido em page.next_after para avançar nesta lista. Copie o valor completo. Não use um cursor da lista de uma cobrança nem envie junto de before. |
| `before` | `str` | Não | Cursor recebido em page.previous_before para voltar nesta lista. Copie o valor completo. Não use um cursor da lista de uma cobrança nem envie junto de after. |
| `created_gte` | `int` | Não | Filtra estornos solicitados a partir deste instante, inclusive, em segundos Unix UTC. Usa a data de criação da solicitação, sem depender da conclusão. Mantenha o valor ao mudar de página. |
| `created_lte` | `int` | Não | Filtra estornos solicitados até este instante, inclusive, em segundos Unix UTC. Se informar created_gte, este valor deve ser maior ou igual a ele. |

### ConfigureSimulationScenarioParams

Preparar cenário. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `action` | `Literal['pix_issuance', 'boleto_issuance', 'cancellation']` | Sim | Ação a testar: pix_issuance para emissão Pix, boleto_issuance para emissão de boleto ou cancellation para cancelamento. Para cancellation, mantenha a cobrança aberta com Pix ou boleto já emitido, sem confirmar o pagamento. |
| `outcome` | `Literal['pending', 'failed']` | Sim | Resultado da ação: pending mantém a confirmação em aberto; failed apresenta uma falha. |

### ResolveSimulationScenarioParams

Resolver cenário pendente. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `action` | `Literal['pix_issuance', 'boleto_issuance', 'cancellation']` | Sim | Ação a testar: pix_issuance para emissão Pix, boleto_issuance para emissão de boleto ou cancellation para cancelamento. |
| `outcome` | `Literal['completed', 'failed']` | Sim | Resultado para a pendência: completed conclui a ação; failed confirma a falha. |

### IssueSimulationPaymentParams

Emitir pagamento de teste. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `payment_method` | `int` | Sim | Meio a emitir: 1 para Pix ou 2 para boleto. Deve estar habilitado na cobrança. |

### CreateSimulationRefundParams

Simular estorno pendente. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `amount_cents` | `int` | Sim | Valor solicitado para devolução, em centavos de real. Para devolver tudo, informe o valor restante mostrado na consulta de elegibilidade. |
| `description` | `str \| None` | Não | Descrição da solicitação de devolução. Você pode deixar este campo vazio. |

### ListStatementsParams

Recuperar extrato. Argumento `params`: opcional.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `page_size` | `int` | Não | Quantidade de lançamentos por página. |
| `after` | `str` | Não | Cursor recebido em page.next_after para avançar. Mantenha os mesmos filtros e a mesma ordem. Use somente after ou before. |
| `before` | `str` | Não | Cursor recebido em page.previous_before para voltar. Mantenha os mesmos filtros e a mesma ordem. Use somente after ou before. |
| `statement_type` | `str` | Não | Tipos de lançamento separados por vírgula: 1 recebimento; 2 tarifa; 3 tarifa de serviço; 4 saque; 5 devolução; 6 devolução parcial; 7 crédito por ajuste; 8 débito por ajuste; 9 bloqueio; 10 liberação. |
| `reference_id` | `str` | Não | Identificador da cobrança, contestação, saque ou ajuste relacionado ao lançamento. Use o ID completo retornado pela Raims. |
| `created_gte` | `int` | Não | Início inclusivo do período, em segundos Unix UTC. O filtro considera o instante do lançamento. |
| `created_lte` | `int` | Não | Fim inclusivo do período, em segundos Unix UTC. O instante informado é o limite exato; frações posteriores ao segundo informado ficam fora do período. |
| `sort_order` | `Literal['asc', 'desc']` | Não | Ordem dos lançamentos pela data: desc mostra os mais recentes primeiro; asc mostra os mais antigos primeiro. |

### SetWebhookPauseParams

Pausar ou retomar envios. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `is_paused` | `bool` | Sim | Envie true para pausar os envios ou false para retomá-los. Repetir o mesmo valor preserva o estado e a data de pausa. |

### ListWebhooksParams

Listar webhooks. Argumento `params`: opcional.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `page_size` | `int` | Não | Quantidade de registros por página. A resposta informa o tamanho efetivo em page.page_size. |
| `after` | `str` | Não | Para avançar, copie page.next_after da resposta anterior. Use apenas after ou before. |
| `before` | `str` | Não | Para voltar, copie page.previous_before da resposta anterior. Use apenas after ou before. |

### CreateWebhookParams

Criar um webhook. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `name` | `str` | Sim | Nome para identificar o destino. |
| `url` | `str` | Sim | URL HTTPS que recebe os eventos. Use a porta padrão 443 e um endereço público externo à Raims. |
| `events` | `Sequence[Literal['charge.created', 'charge.paid', 'charge.canceled', 'charge.failed', 'refund.requested', 'refund.completed', 'refund.failed']]` | Sim | Códigos dos eventos que este destino deve receber. Consulte o catálogo de eventos disponíveis. |
| `is_active` | `bool` | Não | Define se o destino pode receber eventos após o cadastro. |

### UpdateWebhookParams

Atualizar um webhook. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `name` | `str` | Não | Novo nome do webhook. |
| `url` | `str` | Não | Nova URL HTTPS que recebe os eventos, na porta padrão 443. |
| `events` | `Sequence[str]` | Não | Lista completa dos eventos que o destino deve receber. Ela substitui a seleção anterior. |
| `is_active` | `bool` | Não | Use true para permitir envios ou false para desativar o destino. |

### RotateWebhookSecretParams

Rotacionar o segredo de assinatura. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `grace_period_seconds` | `int` | Não | Período em que o segredo anterior pode continuar assinando envios. Zero gera uma nova assinatura e encerra a validade dos segredos anteriores, inclusive durante uma transição ativa. Requisições já autorizadas ou em andamento podem chegar com a assinatura anterior. |

### ListWithdrawalDestinationsParams

Listar destinos de saque. Argumento `params`: opcional.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `page_size` | `int` | Não | Quantidade de registros considerados para a página. A lista pode ter menos destinos e ainda indicar uma próxima página; continue enquanto page.has_next for true. |
| `after` | `str` | Não | Cursor recebido em page.next_after para avançar. Copie o valor inteiro e mantenha a mesma chave de API. Não envie junto de before. |
| `before` | `str` | Não | Cursor recebido em page.previous_before para voltar. Copie o valor inteiro e mantenha a mesma chave de API. Não envie junto de after. |

### CreateWithdrawalParams

Solicitar saque. Argumento `params`: obrigatório.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `amount_cents` | `int` | Sim | Valor total a retirar, em centavos de real, incluindo a tarifa. Consulte as condições de saque para conferir saldo, tarifa e limites antes de solicitar. |
| `expected_destination_id` | `str \| None` | Não | ID do destino próprio que deve continuar selecionado como padrão. Copie o id retornado na consulta dos destinos. Se o destino mudar ou deixar de ser válido, o saque é recusado. Omitir ou enviar null usa o destino padrão vigente. |

### ListWithdrawalsParams

Listar saques. Argumento `params`: opcional.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `page_size` | `int` | Não | Quantidade de saques por página. |
| `after` | `str` | Não | Cursor next_after retornado na página anterior. Mantenha os mesmos filtros e a mesma ordem da consulta. |
| `before` | `str` | Não | Cursor previous_before retornado na página seguinte. Mantenha os mesmos filtros e a mesma ordem da consulta. |
| `status` | `str` | Não | Filtre por um ou mais estados separados por vírgula: PENDING, PROCESSING, COMPLETED, FAILED ou CANCELED. |
| `requested_gte` | `int` | Não | Retorne saques solicitados a partir deste instante, inclusive. Informe segundos Unix UTC. |
| `requested_lte` | `int` | Não | Retorne saques solicitados até este instante, inclusive. Informe segundos Unix UTC. |
| `sort_order` | `Literal['asc', 'desc']` | Não | Ordenação pela data de solicitação: desc mostra os mais recentes primeiro; asc mostra os mais antigos primeiro. |

## Valores públicos nomeados

As constantes em `raims.enum_values` vêm dos enums do contrato público. Valores numéricos recebem nomes somente quando o contrato publica rótulos explícitos. As constantes usam `Final` para preservar seus tipos literais.

| Constante | Valor |
| --- | --- |
| `ACCOUNT_CONTEXT_AMOUNT_UNIT_CENTS` | `cents` |
| `ACCOUNT_CONTEXT_BUSINESS_TIMEZONE_AMERICA_SAO_PAULO` | `America/Sao_Paulo` |
| `ACCOUNT_CONTEXT_COMPANY_STATUS_ACTIVE` | `active` |
| `ACCOUNT_CONTEXT_COMPANY_STATUS_LIMITED` | `limited` |
| `ACCOUNT_CONTEXT_COMPANY_STATUS_PENDING` | `pending` |
| `ACCOUNT_CONTEXT_CURRENCY_BRL` | `BRL` |
| `ACCOUNT_CONTEXT_DATA_ENVIRONMENT_PRODUCTION` | `production` |
| `ACCOUNT_CONTEXT_DATA_ENVIRONMENT_SANDBOX` | `sandbox` |
| `ACCOUNT_CONTEXT_TIMESTAMP_UNIT_UNIX_SECONDS` | `unix_seconds` |
| `BALANCE_FORECAST_PERIOD_LAST_15_DAYS` | `last_15_days` |
| `BALANCE_FORECAST_PERIOD_LAST_30_DAYS` | `last_30_days` |
| `BALANCE_FORECAST_PERIOD_LAST_7_DAYS` | `last_7_days` |
| `BALANCE_FORECAST_PERIOD_TODAY` | `today` |
| `CHARGE_CREATED_PAYMENT_METHOD_TYPES_ITEM_BOLETO` | `2` |
| `CHARGE_CREATED_PAYMENT_METHOD_TYPES_ITEM_PIX` | `1` |
| `CHARGE_LIST_ITEM_PAYMENT_METHOD_TYPES_ITEM_BOLETO` | `2` |
| `CHARGE_LIST_ITEM_PAYMENT_METHOD_TYPES_ITEM_PIX` | `1` |
| `CHARGE_PAYMENT_INFORMATION_BOLETO_PAYMENT_STATUS_AWAITING_PAYMENT` | `awaiting_payment` |
| `CHARGE_PAYMENT_INFORMATION_BOLETO_PAYMENT_STATUS_COMPENSATED` | `compensated` |
| `CHARGE_PAYMENT_INFORMATION_BOLETO_PAYMENT_STATUS_SETTLED` | `settled` |
| `CHARGE_PAYMENT_INFORMATION_BOLETO_STATUS_AVAILABLE` | `available` |
| `CHARGE_PAYMENT_INFORMATION_BOLETO_STATUS_FAILED` | `failed` |
| `CHARGE_PAYMENT_INFORMATION_BOLETO_STATUS_NOT_GENERATED` | `not_generated` |
| `CHARGE_PAYMENT_INFORMATION_BOLETO_STATUS_PENDING` | `pending` |
| `CHARGE_PAYMENT_INFORMATION_PIX_STATUS_AVAILABLE` | `available` |
| `CHARGE_PAYMENT_INFORMATION_PIX_STATUS_FAILED` | `failed` |
| `CHARGE_PAYMENT_INFORMATION_PIX_STATUS_NOT_GENERATED` | `not_generated` |
| `CHARGE_PAYMENT_INFORMATION_PIX_STATUS_PENDING` | `pending` |
| `CHARGE_PAYMENT_METHOD_TYPES_ITEM_BOLETO` | `2` |
| `CHARGE_PAYMENT_METHOD_TYPES_ITEM_PIX` | `1` |
| `CHARGE_SCENARIO_ACTION_BOLETO_ISSUANCE` | `boleto_issuance` |
| `CHARGE_SCENARIO_ACTION_CANCELLATION` | `cancellation` |
| `CHARGE_SCENARIO_ACTION_PIX_ISSUANCE` | `pix_issuance` |
| `CHARGE_SCENARIO_OUTCOME_COMPLETED` | `completed` |
| `CHARGE_SCENARIO_OUTCOME_FAILED` | `failed` |
| `CHARGE_SCENARIO_OUTCOME_PENDING` | `pending` |
| `CHARGE_SCENARIO_REQUEST_ACTION_BOLETO_ISSUANCE` | `boleto_issuance` |
| `CHARGE_SCENARIO_REQUEST_ACTION_CANCELLATION` | `cancellation` |
| `CHARGE_SCENARIO_REQUEST_ACTION_PIX_ISSUANCE` | `pix_issuance` |
| `CHARGE_SCENARIO_REQUEST_OUTCOME_FAILED` | `failed` |
| `CHARGE_SCENARIO_REQUEST_OUTCOME_PENDING` | `pending` |
| `CHARGE_SCENARIO_STATE_COMPLETED` | `completed` |
| `CHARGE_SCENARIO_STATE_CONFIGURED` | `configured` |
| `CHARGE_SCENARIO_STATE_FAILED` | `failed` |
| `CHARGE_SCENARIO_STATE_PENDING` | `pending` |
| `CHARGE_STATISTICS_PERIOD_LAST_15_DAYS` | `last_15_days` |
| `CHARGE_STATISTICS_PERIOD_LAST_30_DAYS` | `last_30_days` |
| `CHARGE_STATISTICS_PERIOD_LAST_7_DAYS` | `last_7_days` |
| `CHARGE_STATISTICS_PERIOD_TODAY` | `today` |
| `CHECKOUT_ASSET_ERROR_CODE_CHECKOUT_ASSET_INVALID_IMAGE` | `CHECKOUT_ASSET_INVALID_IMAGE` |
| `CHECKOUT_ASSET_ERROR_CODE_CHECKOUT_ASSET_PROCESSING_FAILED` | `CHECKOUT_ASSET_PROCESSING_FAILED` |
| `CHECKOUT_ASSET_ERROR_CODE_CHECKOUT_ASSET_UPLOAD_NOT_FOUND` | `CHECKOUT_ASSET_UPLOAD_NOT_FOUND` |
| `CHECKOUT_ASSET_STATUS_ABSENT` | `absent` |
| `CHECKOUT_ASSET_STATUS_FAILED` | `failed` |
| `CHECKOUT_ASSET_STATUS_PENDING` | `pending` |
| `CHECKOUT_ASSET_STATUS_READY` | `ready` |
| `CHECKOUT_ASSET_UPLOAD_CONTENT_TYPE_IMAGE_JPEG` | `image/jpeg` |
| `CHECKOUT_ASSET_UPLOAD_CONTENT_TYPE_IMAGE_PNG` | `image/png` |
| `CREATE_CHARGE_REQUEST_PAYMENT_METHOD_BOLETO` | `2` |
| `CREATE_CHARGE_REQUEST_PAYMENT_METHOD_INDEFINIDO` | `0` |
| `CREATE_CHARGE_REQUEST_PAYMENT_METHOD_PIX` | `1` |
| `CREATE_CHARGE_REQUEST_PAYMENT_METHOD_TYPES_ITEM_BOLETO` | `2` |
| `CREATE_CHARGE_REQUEST_PAYMENT_METHOD_TYPES_ITEM_PIX` | `1` |
| `CREATE_CHECKOUT_FAVICON_UPLOAD_REQUEST_CONTENT_TYPE_IMAGE_JPEG` | `image/jpeg` |
| `CREATE_CHECKOUT_FAVICON_UPLOAD_REQUEST_CONTENT_TYPE_IMAGE_PNG` | `image/png` |
| `CREATE_CHECKOUT_LOGO_UPLOAD_REQUEST_CONTENT_TYPE_IMAGE_JPEG` | `image/jpeg` |
| `CREATE_CHECKOUT_LOGO_UPLOAD_REQUEST_CONTENT_TYPE_IMAGE_PNG` | `image/png` |
| `CREATE_PAYMENT_LINK_REQUEST_PAYMENT_METHOD_TYPES_ITEM_BOLETO` | `2` |
| `CREATE_PAYMENT_LINK_REQUEST_PAYMENT_METHOD_TYPES_ITEM_PIX` | `1` |
| `CREATE_WEBHOOK_REQUEST_EVENTS_ITEM_CHARGE_CANCELED` | `charge.canceled` |
| `CREATE_WEBHOOK_REQUEST_EVENTS_ITEM_CHARGE_CREATED` | `charge.created` |
| `CREATE_WEBHOOK_REQUEST_EVENTS_ITEM_CHARGE_FAILED` | `charge.failed` |
| `CREATE_WEBHOOK_REQUEST_EVENTS_ITEM_CHARGE_PAID` | `charge.paid` |
| `CREATE_WEBHOOK_REQUEST_EVENTS_ITEM_REFUND_COMPLETED` | `refund.completed` |
| `CREATE_WEBHOOK_REQUEST_EVENTS_ITEM_REFUND_FAILED` | `refund.failed` |
| `CREATE_WEBHOOK_REQUEST_EVENTS_ITEM_REFUND_REQUESTED` | `refund.requested` |
| `CUSTOMER_CREATED_TAX_ID_TYPE_CNPJ` | `cnpj` |
| `CUSTOMER_CREATED_TAX_ID_TYPE_CPF` | `cpf` |
| `CUSTOMER_LIST_ITEM_TAX_ID_TYPE_CNPJ` | `cnpj` |
| `CUSTOMER_LIST_ITEM_TAX_ID_TYPE_CPF` | `cpf` |
| `DISPUTE_INFRACTION_RESULT_AGREED` | `agreed` |
| `DISPUTE_INFRACTION_RESULT_DISAGREED` | `disagreed` |
| `DISPUTE_KIND_CHARGEBACK` | `chargeback` |
| `DISPUTE_KIND_MED` | `med` |
| `DISPUTE_LIST_ITEM_KIND_CHARGEBACK` | `chargeback` |
| `DISPUTE_LIST_ITEM_KIND_MED` | `med` |
| `DISPUTE_LIST_ITEM_STAGE_CANCELLED` | `cancelled` |
| `DISPUTE_LIST_ITEM_STAGE_CLOSED` | `closed` |
| `DISPUTE_LIST_ITEM_STAGE_FAILED` | `failed` |
| `DISPUTE_LIST_ITEM_STAGE_IN_ANALYSIS` | `in_analysis` |
| `DISPUTE_LIST_ITEM_STAGE_OPEN` | `open` |
| `DISPUTE_LIST_ITEM_STAGE_REFUND_IN_ANALYSIS` | `refund_in_analysis` |
| `DISPUTE_LIST_ITEM_STAGE_REJECTED` | `rejected` |
| `DISPUTE_REFUND_RESULT_PARTIALLY_ACCEPTED` | `partially_accepted` |
| `DISPUTE_REFUND_RESULT_REJECTED` | `rejected` |
| `DISPUTE_REFUND_RESULT_TOTALLY_ACCEPTED` | `totally_accepted` |
| `DISPUTE_STAGE_CANCELLED` | `cancelled` |
| `DISPUTE_STAGE_CLOSED` | `closed` |
| `DISPUTE_STAGE_FAILED` | `failed` |
| `DISPUTE_STAGE_IN_ANALYSIS` | `in_analysis` |
| `DISPUTE_STAGE_OPEN` | `open` |
| `DISPUTE_STAGE_REFUND_IN_ANALYSIS` | `refund_in_analysis` |
| `DISPUTE_STAGE_REJECTED` | `rejected` |
| `PAYMENT_LINK_DETAILS_EFFECTIVE_PAYMENT_METHOD_TYPES_ITEM_BOLETO` | `2` |
| `PAYMENT_LINK_DETAILS_EFFECTIVE_PAYMENT_METHOD_TYPES_ITEM_PIX` | `1` |
| `PAYMENT_LINK_DETAILS_PAYMENT_METHOD_TYPES_ITEM_BOLETO` | `2` |
| `PAYMENT_LINK_DETAILS_PAYMENT_METHOD_TYPES_ITEM_PIX` | `1` |
| `PAYMENT_LINK_PAYMENT_METHOD_TYPES_ITEM_BOLETO` | `2` |
| `PAYMENT_LINK_PAYMENT_METHOD_TYPES_ITEM_PIX` | `1` |
| `PAYMENT_LINK_UNAVAILABLE_REASON_CODE_BOLETO_AWAITING_SETTLEMENT` | `BOLETO_AWAITING_SETTLEMENT` |
| `PAYMENT_LINK_UNAVAILABLE_REASON_CODE_CHARGE_EXPIRED` | `CHARGE_EXPIRED` |
| `PAYMENT_LINK_UNAVAILABLE_REASON_CODE_CHARGE_NOT_OPEN` | `CHARGE_NOT_OPEN` |
| `PAYMENT_LINK_UNAVAILABLE_REASON_CODE_PAYMENT_LINK_PAUSED` | `PAYMENT_LINK_PAUSED` |
| `PAYMENT_LINK_UNAVAILABLE_REASON_CODE_PAYMENT_METHODS_UNAVAILABLE` | `PAYMENT_METHODS_UNAVAILABLE` |
| `PAYMENT_LINK_UNAVAILABLE_REASON_CODE_PIX_CANCELLATION_PENDING` | `PIX_CANCELLATION_PENDING` |
| `PAYMENT_LINK_UNAVAILABLE_REASON_CODE_PIX_CANCELLED` | `PIX_CANCELLED` |
| `REFUND_FAILURE_REASON_CODE_REFUND_FAILURE_REASON_UNAVAILABLE` | `REFUND_FAILURE_REASON_UNAVAILABLE` |
| `REFUND_FAILURE_REASON_CODE_REFUND_NOT_SUBMITTED` | `REFUND_NOT_SUBMITTED` |
| `REFUND_FAILURE_REASON_CODE_REFUND_PROCESSING_FAILED` | `REFUND_PROCESSING_FAILED` |
| `REFUND_FAILURE_REASON_CODE_REFUND_PROCESSING_UNAVAILABLE` | `REFUND_PROCESSING_UNAVAILABLE` |
| `REFUND_FAILURE_REASON_CODE_REFUND_REJECTED` | `REFUND_REJECTED` |
| `REFUND_STATUS_ACCEPTED` | `accepted` |
| `REFUND_STATUS_COMPLETED` | `completed` |
| `REFUND_STATUS_FAILED` | `failed` |
| `REFUND_STATUS_RESERVED` | `reserved` |
| `REFUND_STATUS_UNKNOWN` | `unknown` |
| `REFUND_UNAVAILABLE_REASON_CODE_PIX_REFUND_ALREADY_COMPLETED` | `PIX_REFUND_ALREADY_COMPLETED` |
| `REFUND_UNAVAILABLE_REASON_CODE_PIX_REFUND_CASHIN_NOT_FOUND` | `PIX_REFUND_CASHIN_NOT_FOUND` |
| `REFUND_UNAVAILABLE_REASON_CODE_PIX_REFUND_INSUFFICIENT_BALANCE` | `PIX_REFUND_INSUFFICIENT_BALANCE` |
| `REFUND_UNAVAILABLE_REASON_CODE_PIX_REFUND_IN_PROGRESS` | `PIX_REFUND_IN_PROGRESS` |
| `REFUND_UNAVAILABLE_REASON_CODE_PIX_REFUND_NOT_AVAILABLE` | `PIX_REFUND_NOT_AVAILABLE` |
| `REFUND_UNAVAILABLE_REASON_CODE_PIX_REFUND_PROVIDER_ACCOUNT_NOT_READY` | `PIX_REFUND_PROVIDER_ACCOUNT_NOT_READY` |
| `REFUND_UNAVAILABLE_REASON_CODE_PIX_REFUND_PROVIDER_UNAVAILABLE` | `PIX_REFUND_PROVIDER_UNAVAILABLE` |
| `RESOLVE_CHARGE_SCENARIO_REQUEST_ACTION_BOLETO_ISSUANCE` | `boleto_issuance` |
| `RESOLVE_CHARGE_SCENARIO_REQUEST_ACTION_CANCELLATION` | `cancellation` |
| `RESOLVE_CHARGE_SCENARIO_REQUEST_ACTION_PIX_ISSUANCE` | `pix_issuance` |
| `RESOLVE_CHARGE_SCENARIO_REQUEST_OUTCOME_COMPLETED` | `completed` |
| `RESOLVE_CHARGE_SCENARIO_REQUEST_OUTCOME_FAILED` | `failed` |
| `STATEMENT_REFERENCE_TYPE_AJUSTE` | `4` |
| `STATEMENT_REFERENCE_TYPE_COBRAN_A` | `1` |
| `STATEMENT_REFERENCE_TYPE_CONTESTA_O` | `2` |
| `STATEMENT_REFERENCE_TYPE_MANUAL` | `5` |
| `STATEMENT_REFERENCE_TYPE_SAQUE` | `3` |
| `STATEMENT_REFERENCE_TYPE_SEM_REFER_NCIA` | `None` |
| `STATEMENT_STATEMENT_TYPE_BLOQUEIO` | `9` |
| `STATEMENT_STATEMENT_TYPE_CR_DITO_POR_AJUSTE` | `7` |
| `STATEMENT_STATEMENT_TYPE_DEVOLU_O` | `5` |
| `STATEMENT_STATEMENT_TYPE_DEVOLU_O_PARCIAL` | `6` |
| `STATEMENT_STATEMENT_TYPE_D_BITO_POR_AJUSTE` | `8` |
| `STATEMENT_STATEMENT_TYPE_LIBERA_O` | `10` |
| `STATEMENT_STATEMENT_TYPE_RECEBIMENTO` | `1` |
| `STATEMENT_STATEMENT_TYPE_SAQUE` | `4` |
| `STATEMENT_STATEMENT_TYPE_TARIFA` | `2` |
| `STATEMENT_STATEMENT_TYPE_TARIFA_DE_SERVI_O` | `3` |
| `UPDATE_PAYMENT_LINK_REQUEST_PAYMENT_METHOD_TYPES_ITEM_BOLETO` | `2` |
| `UPDATE_PAYMENT_LINK_REQUEST_PAYMENT_METHOD_TYPES_ITEM_PIX` | `1` |
| `WEBHOOK_CREATED_DISABLED_REASON_CONTINUOUS_FAILURE` | `continuous_failure` |
| `WEBHOOK_CREATED_DISABLED_REASON_MANUAL` | `manual` |
| `WEBHOOK_DISABLED_REASON_CONTINUOUS_FAILURE` | `continuous_failure` |
| `WEBHOOK_DISABLED_REASON_MANUAL` | `manual` |
| `WEBHOOK_EVENT_TYPE_CODE_CHARGE_CANCELED` | `charge.canceled` |
| `WEBHOOK_EVENT_TYPE_CODE_CHARGE_CREATED` | `charge.created` |
| `WEBHOOK_EVENT_TYPE_CODE_CHARGE_FAILED` | `charge.failed` |
| `WEBHOOK_EVENT_TYPE_CODE_CHARGE_PAID` | `charge.paid` |
| `WEBHOOK_EVENT_TYPE_CODE_REFUND_COMPLETED` | `refund.completed` |
| `WEBHOOK_EVENT_TYPE_CODE_REFUND_FAILED` | `refund.failed` |
| `WEBHOOK_EVENT_TYPE_CODE_REFUND_REQUESTED` | `refund.requested` |
| `WEBHOOK_HEALTH_STATUS_DISABLED` | `disabled` |
| `WEBHOOK_HEALTH_STATUS_FAILING` | `failing` |
| `WEBHOOK_HEALTH_STATUS_HEALTHY` | `healthy` |
| `WEBHOOK_HEALTH_STATUS_UNKNOWN` | `unknown` |
| `WITHDRAWAL_DESTINATION_KEY_TYPE_CNPJ` | `CNPJ` |
| `WITHDRAWAL_DESTINATION_KEY_TYPE_EMAIL` | `EMAIL` |
| `WITHDRAWAL_DESTINATION_KEY_TYPE_EVP` | `EVP` |
| `WITHDRAWAL_DESTINATION_KEY_TYPE_PHONE` | `PHONE` |
| `WITHDRAWAL_FAILURE_REASON_CODE_ABOVE_MAXIMUM_WITHDRAWAL` | `ABOVE_MAXIMUM_WITHDRAWAL` |
| `WITHDRAWAL_FAILURE_REASON_CODE_BANK_ACCOUNT_UNAVAILABLE` | `BANK_ACCOUNT_UNAVAILABLE` |
| `WITHDRAWAL_FAILURE_REASON_CODE_BANK_PROCESSING_FAILURE` | `BANK_PROCESSING_FAILURE` |
| `WITHDRAWAL_FAILURE_REASON_CODE_BANK_TIMEOUT` | `BANK_TIMEOUT` |
| `WITHDRAWAL_FAILURE_REASON_CODE_BANK_UNSUPPORTED` | `BANK_UNSUPPORTED` |
| `WITHDRAWAL_FAILURE_REASON_CODE_BELOW_MINIMUM_WITHDRAWAL` | `BELOW_MINIMUM_WITHDRAWAL` |
| `WITHDRAWAL_FAILURE_REASON_CODE_BLOCKED_BALANCE` | `BLOCKED_BALANCE` |
| `WITHDRAWAL_FAILURE_REASON_CODE_DUPLICATED_REQUEST` | `DUPLICATED_REQUEST` |
| `WITHDRAWAL_FAILURE_REASON_CODE_INSUFFICIENT_BALANCE` | `INSUFFICIENT_BALANCE` |
| `WITHDRAWAL_FAILURE_REASON_CODE_INTERNAL_ERROR` | `INTERNAL_ERROR` |
| `WITHDRAWAL_FAILURE_REASON_CODE_INVALID_ACCOUNT_TYPE` | `INVALID_ACCOUNT_TYPE` |
| `WITHDRAWAL_FAILURE_REASON_CODE_INVALID_BANK_ACCOUNT` | `INVALID_BANK_ACCOUNT` |
| `WITHDRAWAL_FAILURE_REASON_CODE_RISK_POLICY_REJECTED` | `RISK_POLICY_REJECTED` |
| `WITHDRAWAL_FAILURE_REASON_CODE_WITHDRAWAL_FAILURE_REASON_UNAVAILABLE` | `WITHDRAWAL_FAILURE_REASON_UNAVAILABLE` |
| `WITHDRAWAL_FAILURE_REASON_CODE_WITHDRAWAL_LIMIT_REACHED` | `WITHDRAWAL_LIMIT_REACHED` |
| `WITHDRAWAL_FAILURE_REASON_CODE_WITHDRAWAL_TEMPORARILY_UNAVAILABLE` | `WITHDRAWAL_TEMPORARILY_UNAVAILABLE` |
| `WITHDRAWAL_PIX_DESTINATION_KEY_TYPE_CNPJ` | `CNPJ` |
| `WITHDRAWAL_PIX_DESTINATION_KEY_TYPE_EMAIL` | `EMAIL` |
| `WITHDRAWAL_PIX_DESTINATION_KEY_TYPE_EVP` | `EVP` |
| `WITHDRAWAL_PIX_DESTINATION_KEY_TYPE_PHONE` | `PHONE` |
| `WITHDRAWAL_STATUS_CANCELED` | `CANCELED` |
| `WITHDRAWAL_STATUS_COMPLETED` | `COMPLETED` |
| `WITHDRAWAL_STATUS_FAILED` | `FAILED` |
| `WITHDRAWAL_STATUS_PENDING` | `PENDING` |
| `WITHDRAWAL_STATUS_PROCESSING` | `PROCESSING` |
| `WITHDRAWAL_STATUS_UNKNOWN` | `UNKNOWN` |
