<!--
Sync Impact Report
- Version change: 2.1.1 → 2.2.0
- Modified principles: none
- Added sections: Catálogo nacional e rota
- Removed sections: none
- Follow-up TODOs: none
-->

# Plano de voo

## Core Principles

### I. Especificação antes do código

Toda mudança de comportamento que o piloto vê MUST começar em `specs/` com
`spec.md`, depois `plan.md` e `tasks.md`, antes de alterar o servidor, os
modelos, `templates/` ou `static/`. Correção que não muda comportamento
observável MAY ir direto ao código. O agente Cursor MUST usar as skills em
`.cursor/skills/` (`speckit-specify`, `speckit-plan`, `speckit-tasks`,
`speckit-implement`) nessa ordem, e MUST fechar com `speckit-converge`.

### II. Limite educacional

O nome do projeto é Plano de voo. O produto é planejamento de voo visual
para avião de pequeno porte. O primeiro manual disponível é o do Cessna 140. A interface e o PDF MUST deixar
claro que o resultado não substitui o manual da aeronave, o treinamento de
voo nem a norma vigente. Nenhuma feature MAY apresentar um número calculado
como autorização de voo, nem protocolar o plano numa autoridade.

### III. Cálculo no servidor

Navegação, combustível, limites do manual, vento, checklist, meteorologia e
PDF MUST ser calculados ou montados no servidor. `templates/` e `static/`
MUST só coletar entrada, chamar o servidor e apresentar o retorno. Duplicar
fórmula no JavaScript é proibido.

### IV. Unidades e fonte explícitas

Cada grandeza exibida, gravada ou impressa MUST nomear a unidade e a fonte
(manual da aeronave ou norma). Texto de interface e PDF MUST permanecer em
português. Falha de meteorologia, vento, carta ou radar MUST aparecer como
indisponível. É proibido inventar boletim, vento, carta ou radar.

### V. Pilha pequena e banco relacional

O runtime MUST ser um processo Flask, com PostgreSQL como único banco de
dados de piloto, manual, aeródromo e plano. O acesso MUST usar SQLAlchemy 2,
psycopg e migrações Alembic. Senha MUST ser armazenada só como hash do
Werkzeug, em sessão do Flask, sem segundo fator. Nova dependência MUST ser
justificada no plano e MUST atualizar `requirements.txt` quando for Python.
Chave de serviço externo MUST ficar fora do repositório.

## Segurança do acesso e documentação

A senha MUST ter no mínimo 8 caracteres. A mensagem de entrada recusada MUST
ser a mesma quando a identificação não existe e quando a senha está errada.
Cinco recusas em 15 minutos para a mesma identificação MUST impedir novas
tentativas por 15 minutos, também com a mesma mensagem. A sessão MUST
encerrar ao sair e após 8 horas sem uso. O cookie de sessão MUST ser
HttpOnly e SameSite=Lax, e Secure fora de acesso local. Depois de sair, a
sessão anterior MUST NOT abrir planos.

A documentação do piloto MUST estar na tela e no PDF: o que informar, o que
significa indisponível, e o aviso de que o resultado não autoriza o voo. A
documentação de operação MUST dizer como preparar o banco, onde ficam as
chaves e como subir o serviço, sem incluir segredo. Os textos ficam em
`documentacao/piloto.md` e `documentacao/operacao.md`.

## Restrições de domínio e pilha

O piloto informa origem, destino e hora. O sistema reconhece o aeródromo
pelo identificador publicado na emenda vigente do ROTAER.

## Catálogo nacional e rota

O banco MUST conter os aeródromos de avião da emenda vigente do ROTAER,
obtidos pela área `rotaer` do AISWEB. Coordenada, elevação e situação vêm
só dessa publicação. Heliponto fica de fora. Sem a emenda vigente, o
catálogo nacional MUST aparecer indisponível. É proibido completar a lista
com coordenada estimada ou tratar a semente antiga de sete indicativos como
se fosse o Brasil inteiro.

O banco MUST conter os modelos de avião pequeno usados no Brasil. Avião
pequeno é o definido no RBAC nº 01: peso máximo de decolagem aprovado igual
ou inferior a 5.670 kg. Helicóptero, planador, balão e avião grande ficam de
fora. A ordem de prioridade é a quantidade de aeronaves daquele modelo no
extrato público do Registro Aeronáutico Brasileiro. Número técnico MUST vir
do manual de voo oficial daquele modelo, uma vez, no registro do manual.
Modelo sem esse manual MUST aparecer como sem manual e MUST NOT ser usado
no cálculo. É proibido inventar peso, velocidade ou consumo.

Os números já gravados do Cessna 140 permanecem esse registro: vazio 404 kg,
máximo de decolagem 658 kg, bagagem máxima 36 kg, braço da bagagem 2,03 m.
É proibido copiá-los para o HTML ou para uma segunda constante.

Dada a origem e o destino, o servidor MUST escolher a rota e as escalas
necessárias. Cada trecho MUST cumprir o manual da aeronave e a reserva do
voo visual diurno do RBAC nº 91.151: combustível para o pouso previsto e
mais 30 minutos em cruzeiro, com o vento só quando a fonte oficial cobrir o
trecho. A rota escolhida é a de menor tempo total de voo; em empate, a de
menos escalas; em novo empate, a de menor distância. Escala só pode ser
aeródromo de avião da emenda vigente. Sem rota que cumpra a regra, o plano
MUST mostrar o motivo e MUST NOT ser apresentado como aceitável. A conta
MUST ficar no servidor.

## Pilha e acesso

Cada plano pertence a um piloto. A consulta de plano MUST filtrar pelo piloto
da sessão. Meteorologia de aeródromo vem do Aviation Weather Center.
Radar vem da REDEMET e carta visual vigente vem do AISWEB. Sem a chave
correspondente, aquele item fica indisponível. Vento de rota vem do produto
oficial de vento de área da REDEMET; se o produto não cobrir a rota, o perfil
fica indisponível.

| Camada | Escolha |
| --- | --- |
| Linguagem | Python 3.10 ou mais novo |
| Aplicação web | Flask 3.0.0 |
| Banco | PostgreSQL 16 |
| Acesso e migração | SQLAlchemy 2, psycopg 3, Alembic |
| Acesso do piloto | Hash de senha do Werkzeug e sessão Flask, sem segundo fator |
| Meteorologia de aeródromo | requests 2.31.0, Aviation Weather Center |
| Radar e vento de área | REDEMET, com chave fora do repositório |
| Carta visual | AISWEB, carta WAC vigente, com chave fora do repositório |
| PDF | reportlab 4.0.7 |
| Mapa no navegador | Leaflet 1.9, carregado pelo CDN |
| Execução | `.venv` na raiz |
| Processo | GitHub Spec Kit 1.2.2, integração `cursor-agent` |
| Verificação | pytest para cálculo, limite do manual e isolamento entre pilotos; conferência manual no navegador |

O ambiente Python do projeto é o `.venv` na raiz. Não instalar essas
bibliotecas no Python do sistema.

## Fluxo Spec Kit

O projeto usa GitHub Spec Kit 1.2.2 com a integração `cursor-agent`.
O caminho de cada mudança é este, um passo por vez:

1. `/speckit-constitution` define os princípios do projeto. Roda uma vez, e de novo só quando um princípio mudar.
2. `/speckit-specify` escreve a especificação em `specs/<feature>/spec.md`.
3. `/speckit-plan` monta o plano técnico.
4. `/speckit-tasks` quebra o plano em tarefas.
5. `/speckit-implement` executa as tarefas.
6. `/speckit-converge` confere o que ainda falta.

A spec ativa está em `specs/002-rota-com-escalas/`. A spec anterior,
`specs/001-planejar-voo-visual/`, descreve o plano direto já construído. Templates ficam em
`.specify/templates/`. Scripts ficam em `.specify/scripts/bash/`. Skills
ficam em `.cursor/skills/`. Não editar esses arquivos para descrever uma
feature. Comportamento novo MUST abrir outra pasta em `specs/` por
`/speckit-specify`.

## Governance

Esta constituição prevalece sobre conveniência de implementação. Emenda MUST
passar por `/speckit-constitution`, incrementar a versão semântica e registrar
a data. MAJOR remove ou redefine princípio. MINOR acrescenta princípio ou
seção. PATCH só esclarece texto.

Revisão de uma mudança MUST verificar: spec existente para comportamento novo,
cálculo no servidor, unidade e fonte visíveis, aviso educacional preservado,
falha de tempo, vento, carta e radar explícita, plano visível só para o piloto
dono, senha mínima, bloqueio de tentativas, sessão encerrada ao sair,
catálogo de aeródromos só da emenda vigente, número de avião só do manual,
rota e escalas calculadas no servidor, e nenhuma dependência nova sem
justificativa no plano.

**Version**: 2.2.0 | **Ratified**: 2026-10-21 | **Last Amended**: 2026-10-21
