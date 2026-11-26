# Pesquisa: Auditoria de funções, botões e camadas

## Decisões

### Confirmar salvamento do nome

- **Decisão**: Manter o fluxo HTML POST/Redirect/GET e emitir uma mensagem de sucesso de uso único somente depois de `g.db.commit()`. Manter resposta JSON e mensagem de validação atuais.
- **Evidência**: `app.py::perfil` grava e redireciona no fluxo HTML; `templates/perfil.html` exibe erro, mas não sucesso. `tests/test_acesso.py::test_edicao_html_de_perfil_salva_nome_e_redireciona` já verifica persistência, sem confirmar feedback.
- **Alternativas consideradas**: Trocar por renderização direta após POST (altera o padrão de redirecionamento); sinalizar sucesso por query string (pode ser forjada sem persistência). O feedback transitório no ciclo existente evita ambos.

### Comunicar indisponibilidade do radar

- **Decisão**: Acrescentar ao resultado JSON de radar um motivo seguro e estável para chave ausente, resposta sem dados geográficos válidos e fonte indisponível. O template usa esse motivo e mantém fallback genérico verdadeiro para planos antigos sem o campo.
- **Evidência**: `servidor/tempo.py::radar` retorna apenas `{"estado": "indisponivel"}` em todos os casos. `templates/plano.html` transforma qualquer caso, inclusive chave ausente, em “URL ou limites geográficos inválidos”.
- **Alternativas consideradas**: Apenas mudar o texto no navegador (não distingue causas); expor a exceção do provedor (pode vazar detalhe interno). O motivo categorizado na origem é verificável sem divulgar exceções.

### Preservar camadas bloqueadas

- **Decisão**: Não alterar a disponibilidade da WAC nem os requisitos de chave/licença da OpenAIP e REDEMET. Corrigir só o motivo apresentado quando ele é enganoso.
- **Evidência**: `specs/009-mapa-interativo-carta-radar/tasks.md` bloqueia a WAC até validar edição, georreferenciamento, cobertura, autorização e geração reproduzível; `templates/plano.html` já informa que a OpenAIP exige chave. No navegador, 9/9 tiles de ruas carregaram e a seleção de trechos manteve uma aba ativa.
- **Alternativas consideradas**: Habilitar camadas para testar (viola gates e pode sugerir dado válido); usar outra fonte como fallback (proibido pela constituição e pela feature 009).

### Conter tabela larga

- **Decisão**: Colocar rolagem horizontal apenas ao redor da tabela de procedência, preservando todas as colunas e a largura da página.
- **Evidência**: Em viewport de 390 px, o documento mediu 1261 px de largura; a tabela possui 11 colunas e não está contida por uma área rolável.
- **Alternativas consideradas**: Ocultar colunas (remove informação exigida) ou reduzir fonte indefinidamente (prejudica leitura).

## Resultado de verificação inicial

`uv run pytest -q`: 137 testes passaram; `tests/review/test_module_shape.py::test_modules_stay_within_complexity_and_size` falhou porque `servidor/pdf_plano.py::_conteudo_relatorio` excede o limite de complexidade. A causa não foi atribuída e o item permanece fora do escopo atual.
