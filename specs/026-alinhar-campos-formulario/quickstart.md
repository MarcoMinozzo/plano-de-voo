# Quickstart: Alinhar campos do formulário

## Automated validation

```bash
uv run pytest -q tests/test_tela_piloto.py
git diff --check
```

## Responsive check

1. Open `/planos/novo` at a viewport at least 640 px wide and confirm each requested pair shares a row.
2. Resize below 640 px and confirm the pairs stack without horizontal scrolling or clipped labels.
3. Submit the form and confirm the current field values and validation behavior are unchanged.
