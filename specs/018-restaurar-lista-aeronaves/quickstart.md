# Quickstart: Restore Synthetic Aircraft Selection

## Prerequisites

- Use the repository `.venv` and the existing pytest setup.
- Automated tests must use `DATABASE_URL_TESTE` or isolated SQLite fixtures, never the product or legacy database.
- Do not run the one-time production import until the existing product database backup has been verified.

## Automated Validation

Run the focused checks:

```bash
uv run pytest tests/test_importar_perfis_sinteticos.py tests/test_perfis_sinteticos.py tests/test_tela_piloto.py tests/test_rota_pdf.py
```

Expected outcomes:

- Legacy-schema fixtures import exactly twenty profiles and 120 selected source rows, preserving all six values and units for each profile.
- A repeated import creates no duplicates; incomplete input and divergent conflicts create no partial writes.
- The source snapshot remains unchanged.
- The selector shows the twenty correct model names without generic source labels, and its single disclosure appears at the end of the input card.
- A synthetic plan retains per-field synthetic labels and units; its PDF ends with the complete synthetic educational disclaimer after the pilot guidance.

## Manual Interface Check

1. Start the application against the normal configured product database with the test profiles present.
2. Open `/planos/novo`; verify that each synthetic option is only the correct model name.
3. Check that the input-card disclaimer is the final content inside the card.
4. Create a test plan and open its result and PDF. Verify the associated model name, synthetic field labels, units, and that the final PDF disclaimer follows the pilot guidance and says the calculations do not authorize flight or replace the manual, training, or current regulations.

## Production Import Check

1. Confirm `DATABASE_URL` selects the canonical product database and `DATABASE_URL_DEMO_ORIGEM` selects the separate legacy source.
2. Create and verify a restorable backup of the product database using the established operations procedure.
3. Run the existing one-time import command documented in [documentacao/operacao.md](../../../documentacao/operacao.md).
4. Confirm the command reports twenty imported or already-present profiles and verify the source was not modified.
5. Confirm `/aeronaves` and `/planos/novo` expose the twenty models without duplicates.
