# Modelo de dados — Capa e diagramação do PDF de voo

## Perfil do piloto

- `nome_exibicao`: nome apresentado na tela de perfil e na capa do PDF.
- Obrigatório, aparado e com limite de 160 caracteres.
- A identificação de acesso e a senha continuam campos independentes.
- Cadastro novo exige nome; somente o piloto autenticado pode alterar o próprio.
- Migração preenche perfis existentes a partir da identificação já gravada.

## Plano de voo

Sem mudança de persistência. O PDF usa o plano próprio já autorizado, sua
data/hora de partida, sequência ordenada de trechos e os dados/resultados já
gravados. A rota completa da capa é formada pelos códigos na ordem dos trechos.

## Relatório PDF

Documento efêmero gerado a partir do plano e do perfil atual do piloto. Não é
persistido no banco nem altera o plano, o checklist ou qualquer cálculo.

## Invariantes

- Um piloto não pode consultar nem editar o nome de outra conta.
- A rota do PDF deve corresponder exatamente aos trechos salvos.
- Fontes, unidades, avisos DEMO/sintéticos, indisponibilidades e orientação do
  piloto permanecem presentes.
