# Data Model: Redesenho da página do plano

## Aeródromo oficial

`Aerodromo` já armazena ICAO, nome, tipo, latitude, longitude, elevação, fonte e edição/data do ROTAER.

| Campo opcional | Origem | Regra |
|---|---|---|
| Telefone | AISWEB/ROTAER | Normalizar espaços; mostrar somente quando publicado. |
| E-mail | AISWEB/ROTAER | Preservar o valor publicado e mostrar somente quando publicado. |
| Contatos verificados | Detalhe da emenda AISWEB/ROTAER | Marcador interno para distinguir ausência publicada de contatos ainda não carregados; registros anteriores devem ter contatos buscados uma vez. |

Telefone e e-mail são nullable para compatibilidade com registros existentes. Uma atualização da publicação oficial substitui os contatos pelo conteúdo da versão atual; campo ausente fica nulo e é mostrado como indisponível, sem reaproveitar valor antigo. O marcador de verificação permite reutilizar o cache mesmo quando a publicação não contém contatos. Registros existentes começam como não verificados para que seus detalhes oficiais sejam carregados uma vez. A migração é aditiva e não altera planos existentes.

## Rota e camadas

- `Trecho` continua referenciando ICAO de origem/destino e valores calculados no servidor; nenhuma entidade ou cálculo novo.
- O template recebe os objetos `Aerodromo` já resolvidos para os trechos, além das coordenadas atuais.
- Estados de REDEMET, RainViewer, WAC e Google são estados de apresentação existentes ou derivados da configuração; não são persistidos no plano nem combinados entre fontes.
- A máscara de cobertura RainViewer deixa de ser desenhada como camada. O aviso conciso de cobertura continua junto ao crédito e horário quando RainViewer estiver ativo.
