# Raims Python SDK

Leia README, CONTRIBUTING e docs/maintenance.md antes de alterar o SDK.

- Python 3.10 ou superior; pacote `raims`, clientes `RaimsClient` e
  `AsyncRaimsClient`, serviços e métodos em snake_case.
- Consuma somente o contrato público fixado em contracts, com revisão e
  SHA-256 conferidos. Não importe contratos privados nem código dos hosts.
- scripts/generate.py gera os serviços, modelos, entradas, constantes,
  metadados HTTP e docs/reference.md. Não edite esses outputs manualmente.
- Preserve nomes JSON, inteiros em centavos, datas Unix, omissão e null,
  campos futuros e resultados pendentes. Não gerar idempotência nem repetir
  escritas automaticamente. Retries configuráveis são exclusivos de leitura.
- Chave de API determina empresa e ambiente. Não oferecer seleção de ambiente,
  OAuth ou headers arbitrários. Transporte não segue redirects, não baixa
  URLs externas nem faz uploads. TLS permanece verificado.
- Diagnósticos contêm somente metadados sem IDs de recurso, query, credencial
  ou payload. Representações padrão dos objetos não expõem dados.
- Testes, simuladores, ferramentas, ambientes virtuais, builds e evidências
  ficam exclusivamente em C:\server\raims\.tmp\raims-python-sdk.
  Nunca versioná-los nem incluí-los na distribuição.
- Confira geração offline, tipos, contrato completo, transporte síncrono e
  assíncrono, webhooks e wheel/sdist antes de concluir. Use dependências
  isoladas; não chame a API real durante a validação.
- A primeira distribuição publica fontes e release no GitHub. O CI fica em
  `templates/ci/validate.yml`, sem workflow executável nesta etapa.
- Antes de commit e publicação, use os estágios Commit e Deploy do preflight
  com o perfil Raims-Python. Preserve SAST e auditoria das dependências runtime.
- Deixe alterações sem commit e sem conteúdo em staging. Criação de remoto,
  push, release, PyPI e publicação de documentação exigem autorização própria.
- Descreva os recursos da Raims diretamente e preserve licenças e atribuições
  obrigatórias de código incorporado. Aplique a skill humanizer aos textos.
