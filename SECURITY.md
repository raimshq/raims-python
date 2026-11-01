# Segurança

Relate vulnerabilidades de forma privada para `security@raims.com`. Não abra
uma discussão pública com credenciais, dados pessoais, corpos reais, segredos
de webhook ou URLs temporárias. Descreva o comportamento, a versão afetada
e uma reprodução mínima com dados fictícios.

O SDK é destinado ao servidor do integrador. Guarde chaves e segredos em cofre,
use as permissões necessárias à integração e mantenha Python e dependências
atualizados. Confira empresa, ambiente, autorização e idempotência na aplicação.

A verificação de webhook autentica a entrega; o integrador continua responsável
por validar o evento, deduplicar e persistir o trabalho antes do aceite HTTP.
