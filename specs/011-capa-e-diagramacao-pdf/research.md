# Research — Capa e diagramação do PDF de voo

## Decisões

- Reutilizar ReportLab 4.0.7, já listado em `requirements.txt`; não introduzir
  conversão HTML, serviço externo ou dependência nova.
- Usar `static/casca/emblema-plano-de-voo.png` e a identidade visual aprovada:
  navy `#001030`, sky `#0090F0`, gold `#F0A000`, paper `#F4F7FB` e sans-serif.
- Separar a capa do relatório e organizar as páginas seguintes por resumo,
  trechos, fontes/procedência, meteorologia/vento, checklist sugerido e
  orientação do piloto. Preservar os dados do documento atual.
- Adicionar nome de exibição ao perfil. Contas existentes recebem
  `identificacao` como valor inicial; cadastro novo exige nome e o titular
  pode alterá-lo numa página autenticada.
- Migrar a partir da única revisão existente `d1e2f3a4b5c6`. O downgrade
  removerá a coluna e, portanto, nomes editados após o backfill.
- Continuar entregando o PDF em memória e checar o dono do plano antes de
  incluir o nome do piloto da sessão.

## Evidência do repositório

- `servidor/pdf_plano.py` desenha texto corrido em A4 e quebra por número de
  caracteres; atualmente reúne trechos, resultado, fontes, vento, meteorologia,
  checklist e texto integral de `documentacao/piloto.md`.
- `app.py` já autentica e confere propriedade do plano na rota `/pdf`; o piloto
  atual está disponível para fornecer o nome de exibição.
- `Piloto` guarda somente identificação e hash de senha. O cadastro está em
  `/cadastro`; não há edição de perfil. A revisão Alembic atual é única.
- A experiência UX existente exige relatório técnico do voo inteiro e
  checklist apenas no PDF, sem estado marcado/desmarcado. A constituição exige
  conteúdo em português, fontes rastreáveis e avisos didáticos.

## Alternativas rejeitadas

- **Mostrar a identificação de acesso como nome permanente**: rejeitada após
  decisão do usuário por um nome de exibição próprio.
- **Remover a orientação do piloto para encurtar o PDF**: rejeitada porque a
  constituição exige que ela também apareça no documento.
- **Renderizar a página HTML para PDF**: rejeitada; o relatório deve manter
  conteúdo técnico imprimível e seu contrato atual, sem acoplar o layout à tela.
- **Adicionar biblioteca de layout ou fontes**: rejeitada; ReportLab e a
  tipografia aprovada já atendem ao escopo.
