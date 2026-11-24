# Plano de voo

## Operação

Como preparar o banco, guardar as chaves e subir o serviço. Este texto não traz senha nem chave. Os valores ficam no ambiente de quem opera, no arquivo `.env`, fora do repositório.

## O que precisa estar instalado

- Python 3.10 ou mais novo
- PostgreSQL 16
- O ambiente virtual `.venv` na raiz do repositório

Não instale essas bibliotecas no Python do sistema. Com o `.venv` ativo:

```bash
pip install -r requirements.txt
```

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha lá. Não escreva os valores neste arquivo.

| Variável | Função |
| --- | --- |
| DATABASE_URL | Onde está a base PostgreSQL deste projeto |
| DATABASE_URL_TESTE | Base usada só pelos testes. Não é a base de desenvolvimento |
| SECRET_KEY | Assina a sessão do piloto |
| COOKIE_SECURE | Use 1 fora de acesso local |
| REDEMET_API_KEY | Radar e vento de área. Sem ela, esses itens ficam indisponíveis |
| AISWEB_API_KEY | Carta visual vigente, pôr do sol e emenda do ROTAER, junto com a senha da API |
| AISWEB_API_PASS | Senha da API do AISWEB. Sem o par, a carta e o catálogo nacional ficam indisponíveis |
| RAB_EXTRATO | Caminho, fora do repositório, do extrato público do Registro Aeronáutico Brasileiro. Sem ele, o registro de modelos fica indisponível |

## Subir numa base vazia

Na raiz do repositório, com o `.venv` ativo e o PostgreSQL em execução:

```bash
alembic upgrade head
python -m servidor.semente
python -m servidor.catalogo
flask --app app:criar_app run
```

Abra a página inicial. Cadastre um piloto com senha de pelo menos 8 caracteres e confirme o painel vazio.

## O que conferir depois de subir

- Senha com menos de 8 caracteres não cria acesso.
- Identificação errada, senha errada e identificação bloqueada mostram a mesma mensagem.
- Um piloto não vê o plano de outro.
- Sem chave de radar ou de carta, o plano abre e esse item fica indisponível.
- A página antiga com conta de navegação no navegador foi retirada do repositório e não faz parte deste serviço.

Nesta máquina o PostgreSQL do sistema é o 14 e não aceita o usuário do projeto. A base de desenvolvimento está num PostgreSQL 16 à parte. O endereço dela fica só no `.env`.

## Catálogo nacional

A especificação da carga está em `specs/002-rota-com-escalas/`. A emenda vigente dos aeródromos vem da área rotaer do AISWEB. Os modelos de avião pequeno vêm do extrato público do Registro Aeronáutico Brasileiro. Sem a chave do AISWEB, o catálogo nacional fica indisponível. A semente atual de sete aeródromos não é essa lista.

## Carga do catálogo nacional

Com o `.venv` ativo, a migração já aplicada e as variáveis no ambiente:

```bash
python -m servidor.catalogo
```

O comando lê a área rotaer do AISWEB e o arquivo indicado por `RAB_EXTRATO`. Ele grava a emenda vigente e os modelos de avião pequeno. Não escreva chave, senha nem número de manual neste arquivo.

Depois da carga, conte os aeródromos de avião oferecidos e confira que um heliponto conhecido da emenda não entra nessa lista. Na lista de modelos, a ordem é a da frota. Os modelos que somam a maior parte da frota precisam estar com o manual gravado. Um modelo sem manual aparece e o cálculo é recusado pelo nome.
