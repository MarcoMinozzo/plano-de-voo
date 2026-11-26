# Quickstart — Capa e diagramação do PDF

## Pré-requisitos

- Ambiente e PostgreSQL configurados conforme
  [documentacao/operacao.md](../../documentacao/operacao.md).
- Executar a nova migração antes de iniciar a aplicação.
- Estar autenticado com um perfil de piloto.

## Testes automatizados

```sh
uv run pytest --no-cov tests/test_acesso.py tests/test_casca_visual.py tests/test_rota_pdf.py tests/test_migracao_perfil.py
```

Os testes devem cobrir cadastro com nome, rejeição de espaços/limites,
backfill de conta anterior, edição apenas pelo próprio piloto, nome atualizado
na capa, emblema, rota com escalas, data/hora, paginação, avisos e procedência
DEMO. Não consultar serviço externo.

## Verificação manual

1. Migrar uma base com contas existentes e confirmar que login e senha continuam
   funcionando; o nome inicial deve corresponder à identificação.
2. Cadastrar uma conta com nome de exibição e alterá-lo em Perfil.
3. Baixar PDFs de plano direto, plano com escalas e plano DEMO/indisponível.
4. Conferir a capa e páginas seguintes em leitor PDF e impressão A4: emblema,
   nome atual, rota ordenada, data/hora e fuso; seções, margens, cabeçalhos,
   numeração e texto sem corte.
5. Confirmar que fontes, avisos, orientação integral e checklist sem marcação
   permanecem no documento.
6. Usar outra conta para tentar editar o perfil ou baixar PDF alheio; a ação
   deve ser recusada.

## Resultado esperado

Relatório em português, com capa identificável e páginas técnicas organizadas,
sem mudança no cálculo ou nos dados do plano.
