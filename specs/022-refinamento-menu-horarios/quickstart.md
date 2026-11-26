# Validação rápida: refinamento do menu e horários

## Validação focada

```bash
npm run css:build
.venv/bin/pytest -q --no-cov tests/test_casca_visual.py
git diff --check
```

## Inspeção visual

- Em 1440 px, confirmar logo de aproximadamente 140 px, centro vertical compartilhado com o card e menu central com largura ajustada ao conteúdo.
- Em 390 px, confirmar o botão sanduíche, operação por teclado/toque e ausência de rolagem horizontal.
- No painel, confirmar formato de data/hora até minutos, sem segundos, com sufixo “TL”.
- Confirmar que sair mantém o POST e nome acessível e que os avisos e ações existentes não mudaram.
