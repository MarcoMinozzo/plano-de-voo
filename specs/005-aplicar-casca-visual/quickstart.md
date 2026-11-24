# Quickstart: Aplicar a casca visual

1. Subir o serviço como em `documentacao/operacao.md`.
2. Abrir a entrada numa janela abaixo de 720 px e numa janela mais larga. A planta da pista e o emblema aparecem. O card fica centrado na larga. O menu de voo não aparece.
3. Abrir o cadastro e conferir o mesmo fundo, o mesmo emblema e o mesmo card.
4. Entrar. O menu mostra Novo voo, Voos planejados, Imprimir voo e Sair. O plano novo pede os sete campos, sem combustível a bordo. A frase de que o resultado não autoriza o voo está visível.
5. Escolher Imprimir voo nessa tela. A página permanece e mostra "Não há voo para imprimir."
6. Calcular um plano válido. No envio, o card some e a frase "Em processamento" aparece. A resposta abre o plano, com o resumo acima dos trechos.
7. Calcular um plano recusado. O card volta com os valores e o motivo.
8. Num plano com dois trechos, trocar a aba. O resumo fica com as mesmas linhas. Imprimir voo entrega o PDF desse plano.
9. Sair. A próxima tela é a entrada, sem o menu de voo.
10. A validação automática desta casca é `pytest tests/test_casca_visual.py`, quando as tarefas o criarem. O contrato conferido está em [contracts/casca-visual.md](./contracts/casca-visual.md).
