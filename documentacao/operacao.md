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
| AISWEB_API_KEY | Carta visual vigente, junto com a senha da API |
| AISWEB_API_PASS | Senha da API do AISWEB. Sem o par, a carta fica indisponível |

## Subir numa base vazia

Na raiz do repositório, com o `.venv` ativo e o PostgreSQL em execução:

```bash
alembic upgrade head
python -m servidor.semente
flask --app app:criar_app run
```

Abra a página inicial. Cadastre um piloto com senha de pelo menos 8 caracteres e confirme o painel vazio.

## O que conferir depois de subir

- Senha com menos de 8 caracteres não cria acesso.
- Identificação errada, senha errada e identificação bloqueada mostram a mesma mensagem.
- Um piloto não vê o plano de outro.
- Sem chave de radar ou de carta, o plano abre e esse item fica indisponível.
- A página antiga `templates/index.html` não faz parte deste serviço e não deve ser publicada. Ela guarda conta de navegação e um número do manual.

Nesta máquina o PostgreSQL do sistema é o 14 e não aceita o usuário do projeto. A base de desenvolvimento está num PostgreSQL 16 à parte. O endereço dela fica só no `.env`.
