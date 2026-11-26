# Contrato de interface: seleção de aeródromo

Cada campo de origem e destino apresenta um único controle visível, identificado por rótulo. Digitar um trecho do código ou do nome filtra as opções do catálogo localmente, sem distinguir maiúsculas, minúsculas ou acentos.

Quando JavaScript não estiver disponível, o formulário mantém os seletores nativos funcionais. Com JavaScript ativo, esses seletores ficam ocultos e são sincronizados pelo único campo de pesquisa visível.

## Estados e ações

| Estado/ação | Comportamento |
|---|---|
| Campo focado sem edição | A seleção atual permanece visível; as opções podem ser abertas para consulta. |
| Texto digitado | A seleção anterior é invalidada e as opções correspondentes aparecem na lista do mesmo campo. |
| Nenhuma correspondência | A lista informa que nenhum aeródromo foi encontrado; texto livre não pode ser enviado como opção. |
| Opção escolhida | O campo mostra o código e o nome; o formulário envia o identificador escolhido. |
| Seta para cima/baixo | Move a opção ativa sem perder o foco do campo. |
| Enter | Confirma a opção ativa. |
| Escape | Fecha as opções sem confirmar um texto não selecionado. |
| Foco sai do campo e da lista | Fecha as opções e atualiza `aria-expanded`. |
| Clique/toque | Escolhe a opção apontada. |
| Resposta de validação | Restaura os identificadores e rótulos enviados anteriormente. |

Origem e destino permanecem independentes. Nenhum endpoint, payload de cálculo ou regra de catálogo muda.
