# Plano de voo

## Operação

Como preparar o banco, guardar as chaves e subir o serviço. Este texto não traz senha nem chave. Os valores ficam no ambiente de quem opera, no arquivo `.env`, fora do repositório.

## O que precisa estar instalado

- Python 3.10 ou mais novo
- PostgreSQL 16
- O ambiente virtual `.venv` na raiz do repositório
- Node.js 20 ou mais novo e npm, somente para compilar o CSS durante o desenvolvimento

Não instale essas bibliotecas no Python do sistema. Com o `.venv` ativo:

```bash
pip install -r requirements.txt
```

## CSS Tailwind

Na raiz do repositório, instale as ferramentas e gere a folha local antes de
publicar alterações de estilo:

```bash
npm ci
npm run css:build
```

Durante o desenvolvimento dos templates, use `npm run css:watch` em outro
terminal para recompilar a folha ao salvar. O watcher não é necessário para
subir o Flask: `static/css/tailwind.css` é versionado e servido localmente.

## Variáveis de ambiente

Configure os valores no ambiente do processo ou em `.env`, que fica fora do
versionamento. Não escreva os valores neste arquivo.

| Variável | Função |
| --- | --- |
| DATABASE_URL | Base PostgreSQL única de produto, usada pela aplicação, Alembic e comandos de carga |
| DATABASE_URL_TESTE | Base PostgreSQL isolada, usada exclusivamente pelos testes |
| DATABASE_URL_DEMO_ORIGEM | Base legada, somente para leitura durante a importação única dos perfis sintéticos existentes |
| SECRET_KEY | Assina a sessão do piloto |
| COOKIE_SECURE | Use 1 fora de acesso local |
| REDEMET_API_KEY | Vento de área, imagem de satélite, reserva do radar de chuva e prioridade do TAF REDEMET. A imagem de chuva do mapa usa RainViewer e não depende desta chave. Sem ela, vento, satélite e a reserva REDEMET ficam indisponíveis; o TAF usa AWC |
| AISWEB_API_KEY | Carta visual vigente, pôr do sol e emenda do ROTAER, junto com a senha da API |
| AISWEB_API_PASS | Senha da API do AISWEB. Sem o par, a carta e o catálogo nacional ficam indisponíveis |
| OPENAIP_API_KEY | Acesso à camada aeronáutica comunitária OpenAIP. Sem ela, a camada fica indisponível; exige atribuição e uso compatível com CC BY-NC 4.0, inclusive não comercial |
| RAB_EXTRATO | Caminho, fora do repositório, do extrato público vigente do Registro Aeronáutico Brasileiro. Use um nome que identifique a publicação e a data; não versione o arquivo bruto. Sem ele, a seleção de aeronaves fica indisponível e vazia |

Para desenvolvimento local, mantenha as credenciais do AISWEB fora do repositório em `~/.config/plano-de-voo/aisweb.env`, com as variáveis `AISWEB_API_KEY` e `AISWEB_API_PASS`. Restrinja as permissões do diretório ao usuário e do arquivo a `0600`. O aplicativo carrega esse arquivo antes do `.env` local; variáveis já exportadas no processo têm prioridade.

## Subir numa base vazia

Na raiz do repositório, com o ambiente virtual e o PostgreSQL em execução:

```bash
.venv/bin/alembic upgrade head
.venv/bin/python -m servidor.semente
.venv/bin/python -m servidor.catalogo
.venv/bin/flask --app app:criar_app run
```

Abra a página inicial. Cadastre um piloto com senha de pelo menos 8 caracteres e confirme o painel vazio.

## O que conferir depois de subir

- Senha com menos de 8 caracteres não cria acesso.
- Identificação errada, senha errada e identificação bloqueada mostram a mesma mensagem.
- Um piloto não vê o plano de outro.
- Sem chave de radar, carta ou OpenAIP, o plano abre e o item correspondente fica indisponível.
- A camada OpenAIP é comunitária, não é carta WAC nem fonte oficial; não a habilite para uso comercial sem uma licença compatível e mantenha a atribuição visível.
- A página antiga com conta de navegação no navegador foi retirada do repositório e não faz parte deste serviço.

Nesta máquina o PostgreSQL do sistema é o 14 e não aceita o usuário do projeto. A base de desenvolvimento está num PostgreSQL 16 à parte. O endereço dela fica só no `.env`.

## Catálogo nacional

A especificação da carga está em `specs/002-rota-com-escalas/`. A emenda vigente dos aeródromos vem da área rotaer do AISWEB. Os modelos factuais de avião pequeno vêm do extrato público do Registro Aeronáutico Brasileiro e usam fontes técnicas rastreáveis oficiais ou secundárias. Sem a chave do AISWEB, o catálogo nacional fica indisponível. A semente atual de sete aeródromos não é essa lista.

## Carga do catálogo nacional

Com o `.venv` ativo, a migração já aplicada e as variáveis no ambiente:

```bash
python -m servidor.catalogo
```

O comando lê a lista ROTAER vigente em páginas de 100 registros e consulta os detalhes de cada aeródromo de avião para obter posição e elevação. Se a resposta XML de um detalhe não identificar o ICAO solicitado, tenta novamente no formato HTML oficial do AISWEB e valida o mesmo código, tipo, data, coordenadas e elevação. Na primeira carga, isso pode gerar milhares de consultas individuais, limitadas a quatro simultâneas; o terminal informa o progresso da lista e dos detalhes. Em execuções seguintes, os detalhes são reutilizados quando a versão e a data AISWEB do registro não mudaram. Uma falha antes da validação completa deixa o ROTAER indisponível e não publica um catálogo parcial; a carga do RAB continua independente. O comando também lê o arquivo indicado por `RAB_EXTRATO`. Não escreva chave, senha nem número de manual neste arquivo.

Depois da carga, conte os aeródromos de avião oferecidos e confira que um heliponto conhecido da emenda não entra nessa lista. A seleção factual filtra primeiro os modelos completos, ordena por frota decrescente com desempate pelo nome e oferece no máximo os 30 primeiros. A completude exige combustível utilizável, velocidade e consumo do mesmo perfil nominal, peso vazio, peso máximo de decolagem e limite de bagagem, todos com unidade e fonte rastreável. Modelos incompletos ou além do limite ficam ocultos; sem RAB vigente, o catálogo factual fica indisponível. Os perfis sintéticos didáticos são exibidos separadamente e não substituem o catálogo factual. Não preencha dados técnicos factuais sem fonte rastreável.

## Importação única dos perfis sintéticos existentes

Execute esta importação uma única vez, somente após confirmar as bases e fazer
backup da base de produto. Aplique primeiro as migrações em `DATABASE_URL` e
configure `DATABASE_URL_DEMO_ORIGEM` para a base legada. Confirme que as URLs
identificam bases PostgreSQL distintas. Então, na raiz do repositório, execute:

```bash
.venv/bin/python -m servidor.importar_perfis_sinteticos
```

O comando lê a origem em modo somente leitura e grava os vinte perfis
existentes na base canônica em uma transação. Pode ser repetido sem duplicar
registros; origem incompleta ou conflito de valores interrompe a operação sem
sobrescrita. Pilotos, planos, perfis genéricos, extrato RAB e aeródromos não
são copiados. Não execute a importação em bases reais sem confirmação das
URLs e backup do destino.

A origem legada permanece no esquema em que foi encontrada; não a migre nem
altere antes da importação. O importador lê as colunas disponíveis nesse
esquema e associa `Aeronave DEMO 01` ao primeiro modelo da lista definida em
`servidor/perfis_sinteticos.py`, seguindo a ordem até o perfil 20. Na base de
produto, cada registro recebe somente o nome do modelo-alvo; os seis valores
e unidades sintéticos existentes são preservados e continuam identificados
como didáticos.
