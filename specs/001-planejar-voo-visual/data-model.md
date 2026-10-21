# Data model: Planejar voo visual

Banco: PostgreSQL 16. Números do manual existem uma vez, na aeronave. Todo plano carrega `piloto_id`.

## Piloto

Pessoa com espaço próprio.

| Campo | Regra |
| --- | --- |
| id | Identificador interno |
| identificacao | Única, obrigatória |
| senha_hash | Obrigatória. Nunca a senha em claro. A senha original tem no mínimo 8 caracteres |
| criado_em | Obrigatório |

Não há compartilhamento de espaço nesta versão. Tentativas de entrada ficam à parte, por texto de identificação, exista o piloto ou não.

## TentativaEntrada

| Campo | Regra |
| --- | --- |
| identificacao | Texto informado, obrigatório |
| instante | Obrigatório |

Cinco registros da mesma identificação em 15 minutos bloqueiam novas tentativas até 15 minutos depois da quinta. A resposta é a mesma de senha errada e de identificação inexistente. Não se cria piloto para uma identificação desconhecida.

## Aeronave

Avião de pequeno porte ligado a um manual.

| Campo | Regra |
| --- | --- |
| id | Identificador interno |
| nome | Obrigatório. O primeiro registro é o Cessna 140 |
| fonte_manual | Citação do manual, obrigatória |
| peso_vazio_kg | Obrigatório |
| peso_max_decolagem_kg | Obrigatório, maior que o peso vazio |
| bagagem_max_kg | Obrigatória |
| braco_bagagem_m | Obrigatório |
| combustivel_planejamento | Valor e unidade vindos do manual, obrigatórios |
| velocidade_planejamento | Valor e unidade vindos do manual, obrigatórios |
| itens_manutencao | Lista do que o manual manda verificar antes do voo |

Semente do Cessna 140: vazio 404 kg, máximo de decolagem 658 kg, bagagem máxima 36 kg, braço da bagagem 2,03 m. Esses números não se repetem no HTML.

## Aerodromo

| Campo | Regra |
| --- | --- |
| icao | Quatro letras, chave |
| nome | Obrigatório |
| lat, lon | Obrigatórios, com a fonte |
| elev_m | Obrigatória |
| fonte | Publicação de onde saíram coordenada e elevação |

Semente: SBJD, SBAU, SBBU, SBML, SBDN, SBKP, SBRP. Origem ou destino fora dessa lista, sem alta posterior com fonte, impede o cálculo.

## PlanoDeVoo

Um voo visual de um piloto.

| Campo | Regra |
| --- | --- |
| id | Identificador interno |
| piloto_id | Obrigatório. Dono do plano |
| aeronave_id | Obrigatório. Manual precisa existir |
| origem_icao, destino_icao | Obrigatórios, diferentes, existentes |
| hora_partida | Obrigatória. Hora no passado exige confirmação do piloto e fica registrada |
| dados_particulares | Ocupantes, pesos deste voo e combustível a bordo, cada um com unidade |
| resultado | Navegação, combustível necessário, limites e se o plano está aceitável |
| meteorologia | METAR e TAF de origem e destino, ou estado `indisponivel` |
| vento | Perfil com direção, velocidade, efeito na proa e na velocidade em relação ao solo, ou `indisponivel` |
| carta | Identificação da WAC, emenda e endereço, ou `indisponivel` |
| radar | Hora da imagem, retângulo geográfico e endereço, ou `indisponivel` |
| aviso | Texto fixo de que o plano não substitui o manual, o treinamento nem a norma, e não autoriza o voo |
| criado_em, atualizado_em | Obrigatórios |

### Estado

- **calculado**: manual, origem, destino e hora bastaram para a conta. Itens externos podem estar indisponíveis.
- **inaceitavel**: a conta rodou e um limite do manual foi ultrapassado (peso, bagagem, combustível ou centro de gravidade). O plano mostra o excesso e não é aceitável.
- **removido**: o piloto confirmou a exclusão. O registro deixa de ser listado e aberto.

Transições: criar passa a `calculado` ou `inaceitavel`. Editar busca de novo tempo, vento, carta e radar e volta a um desses dois estados. Apagar, depois da confirmação, vai a `removido`.

### Validação

- Origem igual ao destino, ou indicativo desconhecido: não grava e aponta o campo.
- Aeronave sem manual completo: não calcula e diz qual dado do manual falta.
- Dado particular obrigatório vazio: não calcula.
- Leitura, edição, PDF e exclusão exigem o `piloto_id` da sessão. Outro piloto recebe recusa, sem dizer se o plano existe.

## ItemChecklist

| Campo | Regra |
| --- | --- |
| id | Identificador interno |
| plano_id | Obrigatório |
| ordem | Obrigatória |
| texto | Obrigatório |
| fonte | Manual ou preparação de voo visual |
| marcado | Começa desmarcado. O piloto pode marcar |

A lista é sugerida na criação e refeita na edição a partir do manual da aeronave. Marca do piloto só permanece se o texto do item continuar o mesmo.

## Relações

- Um piloto tem vários planos.
- Uma aeronave entra em vários planos.
- Um aeródromo é origem ou destino de vários planos.
- Um plano tem vários itens de checklist.
- Apagar o piloto não está nesta versão. Apagar o plano apaga os itens dele.
