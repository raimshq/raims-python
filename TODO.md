# TODO

- [ ] Ativar o CI preparado em `templates/ci/validate.yml` após a publicação
  autorizada dos checkouts revisados. Conferir repositório, acesso do GitHub
  App, allowlist do runner CodeBuild existente e `RAIMS_PYTHON_TOOLKIT_REF`
  com o SHA completo do Toolkit que contém o gate Python. Confirmar os jobs
  de Python 3.10 e 3.14 para o mesmo commit antes de disponibilizar o pacote.
  A primeira entrega no GitHub publica os fontes sem workflow executável.
  PyPI e configuração remota de runners continuam sendo etapas separadas.

- [ ] Disponibilização do SDK Python: após confirmar nome, versão e distribuição
  no PyPI, atualizar README e criar o guia BR/EN em
  `raims-developer-docs/content/docs/integracoes/sdk-python`. Explicar finalidade,
  quando sugerir Python, acesso pela seção de integrações, instalação, Python
  3.10+, uso no servidor, chave e permissões, ambiente definido pela credencial,
  clientes síncrono/assíncrono, paginação, idempotência, ausência de retries de
  escrita, respostas pendentes, documentos e webhooks. Regenerar o catálogo
  público consumido pelo `Raims-Chat` e validar a recuperação e orientação da
  IA em português e inglês. Não anunciar instalação pelo PyPI antes de confirmar
  a distribuição nesse registro. A instalação pelo GitHub está no README.
  A biblioteca atual não exige novo contrato de contexto nem ferramentas de
  consulta; conferir novamente essa conclusão ao preparar os guias. Marcar
  concluído somente após fontes, catálogos e respostas validados.
- [ ] Changelog da primeira distribuição do SDK Python: publicar nota em
  `raims-developer-docs/content/docs/changelog/post` com a data real de
  disponibilização, requisitos, instalação e link para o guia atualizado.
  Incluir a tipagem, a paginação, o tratamento de erros, a idempotência e os
  limites de retry efetivamente disponibilizados. A implementação local não
  autoriza anúncio público.
