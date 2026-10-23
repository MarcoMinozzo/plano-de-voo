# Quickstart: Planejar voo visual

A conferência do catálogo nacional e das escalas está em `specs/002-rota-com-escalas/quickstart.md`. Os passos abaixo conferem o plano direto.

Conferência do plano depois da implementação. Não substitui `tasks.md`. Detalhe de campo está em [data-model.md](./data-model.md) e o contrato em [contracts/api-plano.md](./contracts/api-plano.md).

## Pré-requisitos

- Python 3.10 ou mais novo, no `.venv` da raiz
- PostgreSQL 16 em execução e uma base vazia para este projeto
- Variáveis de ambiente da aplicação: endereço do PostgreSQL, segredo de sessão, e, se for ver radar e carta, as chaves da REDEMET e do AISWEB
- Dependências do plano instaladas no `.venv`: Flask, SQLAlchemy 2, psycopg, Alembic, requests, reportlab, pytest

Sem a chave da REDEMET, o radar e o vento ficam indisponíveis. Sem a chave do AISWEB, a carta fica indisponível. Isso é o resultado esperado, não um boletim inventado.

## Subir

Na raiz do repositório, com o `.venv` ativo:

1. Aplicar as migrações Alembic na base vazia.
2. Carregar a semente: Cessna 140 e os aeródromos SBJD, SBAU, SBBU, SBML, SBDN, SBKP, SBRP.
3. Subir o Flask e abrir a página inicial.

## Pytest

Rodar pytest. Precisa passar:

- cálculo de navegação e combustível com unidade e fonte
- plano inaceitável quando o peso passa de 658 kg no Cessna 140
- dois pilotos, e um não lê o plano do outro
- senha com menos de 8 caracteres não cria acesso
- a sexta tentativa dentro do bloqueio continua recusada, com a mesma mensagem de identificação inexistente
- sessão encerrada não abre plano

Conferir também, lendo os arquivos:

- `documentacao/operacao.md` não contém senha nem chave
- `documentacao/piloto.md` diz o que informar, o que é indisponível e que o plano não autoriza o voo

## Caminho no navegador

1. Cadastrar o piloto A com senha de pelo menos 8 caracteres e ver o painel vazio. Uma senha mais curta é recusada.
2. Errar a senha cinco vezes e, na sexta, usar a senha certa antes de 15 minutos. A entrada continua recusada, com a mesma mensagem de uma identificação que não existe. Esperar o bloqueio passar e entrar.
3. Abrir um plano SBJD → SBAU, com hora futura, Cessna 140 e pesos dentro do manual. A tela mostra navegação, combustível, unidade, fonte, o que significa indisponível e o aviso de que não autoriza o voo.
4. Ver o checklist sugerido e marcar um item.
5. Gerar o PDF e conferir rota, horários, combustível, vento ou a marca de indisponível, resumo do tempo, checklist, a explicação e o aviso.
6. Cadastrar o piloto B em outro navegador. O plano do A não aparece. Abrir o endereço do plano do A com a sessão do B é recusado.
7. No piloto A, editar a hora do plano. A lista mostra a versão nova na mesma visita.
8. Apagar esse plano e cancelar a confirmação: o plano continua. Confirmar: ele some do painel.
9. Tentar origem igual ao destino: o plano não é gravado e o campo é apontado.
10. Desligar a rede ou omitir a chave do radar: o restante do plano aparece, o radar fica indisponível, e a tela explica o que isso significa.
11. Sair e tentar reabrir o plano com a sessão anterior: nenhum plano abre.
