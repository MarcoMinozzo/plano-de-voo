# UI Contract: Formulário de novo plano

## Scope

This contract covers the four existing inputs in the new/edit plan form. It does not change submission, validation, names, values, or calculations.

## Layout

- At viewport widths of 640 px and above, date/time (`hora_partida`) and passenger count (`numero_passageiros`) appear side by side.
- At viewport widths of 640 px and above, people weight (`peso_pessoas_kg`) and baggage weight (`peso_bagagem_kg`) appear side by side.
- Below 640 px, each pair stacks vertically.
- The optional date-confirmation control remains associated with the date/time field.
- Existing labels, weight units, and control accessibility remain intact.
