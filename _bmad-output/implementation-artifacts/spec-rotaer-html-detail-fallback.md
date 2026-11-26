---
title: 'Fallback HTML para detalhe ROTAER vazio'
type: 'bugfix'
created: '2026-11-25'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/specs/014-corrigir-carga-rotaer/spec.md'
  - '{project-root}/specs/014-corrigir-carga-rotaer/contracts/aisweb-rotaer.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A lista AISWEB vigente inclui aeródromos como SI5J, mas a resposta XML de detalhe pode vir vazia, fazendo a carga rejeitar a publicação inteira apesar de a API disponibilizar os dados detalhados em seu formato HTML oficial.

**Approach:** Quando o XML não identificar o ICAO solicitado, tentar o formato HTML oficial da mesma consulta. Só aceitar os dados se ICAO, tipo, data, coordenadas e elevação puderem ser validados; caso contrário, manter a publicação indisponível.

</frozen-after-approval>

## Implementation Notes

- Diagnóstico AISWEB com a configuração local, sem revelar credenciais: SI5J consta na lista vigente; a consulta XML de detalhe retorna `<aisweb/>`, enquanto `force=html` retorna a página ROTAER oficial com o ICAO, a data da emenda, coordenadas e elevação.
- Implementado fallback somente quando o XML não identifica o ICAO solicitado. O HTML só é aceito após validar ICAO, tipo AD, data, coordenadas dentro dos limites geográficos e altitude; respostas incompletas continuam falhando sem publicar catálogo parcial.
- Arquivos atualizados: `servidor/catalogo.py`, `tests/test_catalogo_aerodromos.py`, `specs/014-corrigir-carga-rotaer/contracts/aisweb-rotaer.md`, `documentacao/operacao.md` e `specs/014-corrigir-carga-rotaer/tasks.md`.
- Revisão direta focada na condição real SI5J; sem achados adicionais. Blind Hunter foi pulado para evitar delegar uma revisão pequena/contínua contra as regras de delegação do repositório.
- Verificação: teste real isolado de detalhe SI5J passou pelo fallback; suíte ROTAER focada passou (15 testes) e `git diff --check` passou. A carga nacional completa não foi repetida.
