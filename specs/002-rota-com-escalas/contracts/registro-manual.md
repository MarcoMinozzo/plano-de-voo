# Contrato: registro do manual

Um arquivo JSON por modelo em `servidor/manuais/`, com nome `<modelo_rab em minúsculas, com hífen>.json`. O arquivo é a origem revisada do manual. O cálculo lê o banco, não o arquivo.

## Formato

```json
{
  "modelo_rab": "182P",
  "fabricante": "<fabricante, como no manual>",
  "experimental": false,
  "documento": {
    "titulo": "<título do manual, como na capa>",
    "numero": "<número do documento>",
    "revisao": "<revisão ou data>",
    "copia_publica": "https://..."
  },
  "peso_vazio": {"valor": 0, "unidade": "lb", "pagina": "6-5"},
  "peso_max_decolagem": {"valor": 0, "unidade": "lb", "pagina": "2-5"},
  "bagagem_max": {"valor": 0, "unidade": "lb", "pagina": "2-6"},
  "braco_bagagem": {"valor": 0, "unidade": "in", "pagina": "6-9"},
  "combustivel_utilizavel": {"valor": 0, "unidade": "gal", "pagina": "2-7"},
  "massa_por_galao": {"valor": 0, "unidade": "lb/gal", "pagina": "6-9"},
  "cruzeiro": {
    "condicao": "75% de potência, 6.000 ft, atmosfera padrão",
    "velocidade": {"valor": 0, "unidade": "kt", "pagina": "5-17"},
    "consumo": {"valor": 0, "unidade": "gal/h", "pagina": "5-17"}
  },
  "itens_checklist": [{"texto": "...", "pagina": "4-5"}]
}
```

Os zeros e as páginas acima mostram só a forma. Nenhum número deste exemplo é de manual.

## Unidades aceitas

| Grandeza | No arquivo | No banco |
| --- | --- | --- |
| Peso | kg, lb | kg |
| Braço | m, in | m |
| Combustível | gal, L | gal |
| Massa por galão | kg/gal, lb/gal | kg/gal |
| Velocidade | kt, mph, km/h | kt |
| Consumo | gal/h, L/h, lb/h | gal/h |

## Comando

`python -m servidor.manuais`, com `DATABASE_URL` no ambiente.

- Lê todos os arquivos de `servidor/manuais/`.
- Grava cada arquivo válido e imprime `gravado: <modelo_rab>`.
- Recusa cada arquivo inválido e imprime `recusado: <arquivo>: <campo>`. Não para nos outros.
- Termina com código 0 quando todos passam e 1 quando algum foi recusado.
- Não lê chave, não acessa a internet e não altera o Cessna 140 da semente.
