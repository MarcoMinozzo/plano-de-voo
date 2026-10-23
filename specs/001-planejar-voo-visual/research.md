# Research: Planejar voo visual

A pesquisa do catálogo nacional, do registro de aviões e do critério da rota está em `specs/002-rota-com-escalas/research.md`. O que segue vale para o plano direto.

## Banco de dados

- **Decision**: PostgreSQL 16 é o único banco de piloto, manual, aeródromo e plano.
- **Rationale**: Vários pilotos gravam e editam planos ao mesmo tempo, e cada plano pertence a um piloto. O PostgreSQL garante a relação e a escrita concorrente. Boletim, vento, carta e radar variam de formato e ficam em colunas JSON ao lado dos campos fixos do plano.
- **Alternatives considered**: SQLite em `cessna140.db` serve à calculadora de um piloto nesta máquina. Com espaço privado e mais de um piloto no mesmo serviço, o arquivo único deixa de ser a melhor opção. Banco de documentos foi descartado porque dono, aeronave e plano são relações estáveis.

## Acesso aos dados

- **Decision**: SQLAlchemy 2, driver psycopg 3 e migrações Alembic.
- **Rationale**: O modelo tem piloto, aeronave, aeródromo, plano e item de checklist. O ORM e a migração evitam SQL espalhado e permitem evoluir o esquema sem editar o banco à mão.
- **Alternatives considered**: SQL direto com psycopg é menos uma dependência, e fica frágil quando o plano ganha relações e migrações. Flask-SQLAlchemy repete o que o SQLAlchemy 2 já faz.

## Acesso do piloto

- **Decision**: Identificação e senha. A senha é guardada só como hash do Werkzeug. A sessão é a sessão do Flask. Não há segundo fator nem recuperação de senha nesta versão.
- **Rationale**: A spec pede autenticação simples, sem segundo fator, e um espaço só do piloto. Isso já vem com o Flask, sem um serviço de identidade novo.
- **Alternatives considered**: Provedor externo de login acrescenta conta, rede e um fluxo que a spec não pediu.

## Meteorologia de aeródromo

- **Decision**: METAR e TAF continuam no Aviation Weather Center (`/api/data/metar` e `/api/data/taf`), com tempo limite de 8 segundos.
- **Rationale**: A calculadora atual já usa essa fonte, sem chave, e ela responde para indicativo ICAO brasileiro. Falha ou corpo vazio vira item indisponível.
- **Alternatives considered**: A REDEMET também entrega METAR e TAF, e exige chave e cota. Fica de reserva oficial se o Aviation Weather Center deixar de cobrir o indicativo. Não se completa um buraco com valor inventado.

## Radar de chuva

- **Decision**: Imagem MaxCappi da REDEMET, `GET https://api-redemet.decea.mil.br/produtos/radar/maxcappi`, com `api_key` e a área do radar que cobre a rota. A imagem é posicionada no mapa pelos limites geográficos que a resposta traz.
- **Rationale**: É o radar meteorológico oficial do DECEA, com data e retângulo da imagem. A chave fica em variável de ambiente, fora do repositório. Sem chave, sem resposta ou sem radar sobre a rota, o radar fica indisponível.
- **Alternatives considered**: Desenhar chuva a partir do METAR não é radar. Carta SIGWX não substitui o eco de precipitação.

## Carta de navegação visual

- **Decision**: Carta WAC vigente do AISWEB (`area=cartas`, `especie=VFR`, `tipo=WAC`), com a emenda corrente. Chave e senha da API ficam fora do repositório.
- **Rationale**: A WAC é a carta de navegação visual de área. O AISWEB devolve a carta da emenda vigente. Sem credencial ou sem carta para a região, a carta fica indisponível.
- **Alternatives considered**: Mapa comum de ruas não cumpre a prática de navegação visual pedida na spec.

## Perfil de vento

- **Decision**: O vento da rota sai do produto de área da REDEMET que trouxer vento (GAMET ou mensagem equivalente de vento). O servidor calcula o efeito na proa e na velocidade em relação ao solo na altitude de planejamento. Se o produto não cobrir a rota, o perfil fica indisponível.
- **Rationale**: O vento de altitude do Aviation Weather Center está publicado por região dos Estados Unidos e não serve a uma rota no Brasil. O efeito no voo é conta do servidor, para o piloto não refazer o triângulo.
- **Alternatives considered**: Usar só o vento do METAR de superfície descreve o aeródromo, não o perfil da rota. Inventar vento entre dois METAR é proibido.

## Mapa no navegador

- **Decision**: Leaflet 1.9, pelo CDN, mostra a rota, os aeródromos e a imagem de radar quando ela existir. Não calcula navegação nem combustível.
- **Rationale**: A constituição mantém o mapa no navegador e o cálculo no servidor. O Leaflet já está na página atual.
- **Alternatives considered**: Um framework de interface novo contraria a pilha pequena e não é necessário para este plano.

## Acesso

- **Decision**: Senha com no mínimo 8 caracteres, guardada só como hash do Werkzeug. A mensagem de recusa é única. Cinco recusas em 15 minutos bloqueiam aquela identificação por 15 minutos, exista a conta ou não. A sessão do Flask expira ao sair e após 8 horas sem uso. O cookie é HttpOnly, SameSite=Lax e Secure fora de acesso local.
- **Rationale**: A spec pede acesso simples, sem segundo fator, e sem dizer se a identificação existe. O bloqueio e o fim da sessão limitam o uso de uma senha vazada ou de uma sessão esquecida, sem um serviço de identidade novo.
- **Alternatives considered**: Segundo fator e recuperação de senha ficam fora desta versão. Bloquear só contas que existem revelaria quem está cadastrado.

## Documentação

- **Decision**: `documentacao/piloto.md` é o texto da tela e do PDF. `documentacao/operacao.md` é o texto para subir o sistema, sem segredo.
- **Rationale**: O piloto precisa entender indisponível e o limite do plano sem outro manual. Quem opera precisa subir o banco e as chaves sem ler o código e sem achar senha no repositório.
- **Alternatives considered**: Um agente ou um site de documentação à parte duplicaria a spec. Os dois textos ficam no projeto e a spec manda a tela e o PDF usarem o do piloto.

## Verificação

- **Decision**: pytest cobre cálculo, limite do manual ultrapassado, isolamento entre dois pilotos, senha curta, bloqueio na sexta tentativa e sessão encerrada. O caminho do piloto no navegador continua conferido à mão, pelo `quickstart.md`.
- **Rationale**: Isolamento, conta errada e acesso recusado não podem depender só de uma olhada na tela. A constituição 2.1.1 pede os dois.
- **Alternatives considered**: Só teste manual deixa passar um plano de outro piloto ou um bloqueio que revela se a conta existe.
