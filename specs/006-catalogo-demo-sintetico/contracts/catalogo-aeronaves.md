# Contrato: Catálogo de aeronaves DEMO

## `GET /aeronaves`

Mantém os campos atuais `estado` e `modelos`. No modo DEMO, cada um dos vinte modelos inclui:

- `nome`: identificador genérico DEMO, sem fabricante ou modelo real;
- `estimativa_didatica: true`;
- `procedencia`: seis campos técnicos, cada um com `tipo_fonte: "sintetica"`, valor, unidade, referência e aplicabilidade sintética;
- `data_publicacao: null`; `data_consulta` identifica a geração/carga.

O modo normal continua sem oferecer fontes sintéticas. Nenhum campo da resposta indica aprovação, certificação ou aptidão operacional.

## `POST /planos`

- O modo DEMO aceita somente um perfil sintético selecionável e aeródromos pertencentes à emenda oficial vigente carregada no banco DEMO.
- Sem essa emenda, recusa a criação com erro explícito de catálogo indisponível; não usa aeródromos locais como fallback.
- O cálculo mantém os mesmos campos, fórmula no servidor, reserva VFR e estados de vento/pôr do sol atuais. Serviço externo ausente continua indisponível; não há dado de voo sintético.
- Sucesso identifica a procedência sintética e mantém o aviso não operacional no resultado e PDF.
