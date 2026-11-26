<!--
Sync Impact Report
- Version change: 5.2.0 → 6.0.0
- Modified principles: IV. Unidades e fonte explícitas (exceção para proxies sintéticos didáticos)
- Modified sections: Restrições adicionais; Governance
- Added sections: Perfis sintéticos didáticos de aeronaves
- Removed sections: Dados sintéticos de demonstração isolada
- Follow-up TODOs: atualizar a especificação de banco único e detalhar a transição antes de implementar
-->

# Plano de voo Constitution

## Core Principles

### I. Especificação antes do código

Toda mudança de comportamento que o piloto vê MUST começar em `specs/` com
`spec.md`, depois `plan.md` e `tasks.md`, antes de alterar o servidor, os
modelos, `templates/` ou `static/`. Correção que não muda comportamento
observável MAY ir direto ao código. O agente Cursor MUST usar as skills em
`.cursor/skills/` (`speckit-specify`, `speckit-plan`, `speckit-tasks`,
`speckit-implement`) nessa ordem, e MUST fechar com `speckit-converge`.

### II. Limite educacional

O nome do projeto é Plano de voo. O produto é planejamento de voo visual para
avião de pequeno porte, exclusivamente para fins didáticos e de desenvolvimento
de software; não é ferramenta operacional de despacho de voo. O primeiro
manual disponível é o do Cessna 140. A interface e o PDF MUST identificar
resultados baseados em fonte secundária como estimativas didáticas e MUST dizer
que não são adequados para planejamento de voo real, não substituem o manual,
o treinamento ou a norma vigente e não autorizam o voo. Nenhuma feature MAY
protocolar o plano numa autoridade ou apresentar o resultado como aprovação
operacional.

### III. Cálculo no servidor

Navegação, combustível, limites do manual, vento, checklist, meteorologia e
PDF MUST ser calculados ou montados no servidor. `templates/` e `static/`
MUST só coletar entrada, chamar o servidor e apresentar o retorno. Duplicar
fórmula no JavaScript é proibido.

### IV. Unidades e fonte explícitas

Cada grandeza exibida, gravada ou impressa MUST nomear unidade, fonte,
publicador, data e modelo/variante a que se aplica. A fonte pode ser manual
ou norma oficial, ou fonte técnica secundária rastreável; fonte oficial não é
obrigatória para valores usados exclusivamente no produto didático. Todo valor
secundário MUST ser marcado visivelmente como estimativa didática, sem
aparência de dado oficial ou validado. Valores conflitantes MUST NOT ser
combinados ou promediados silenciosamente; a escolha e a incerteza devem ficar
registradas, ou o campo deve aparecer indisponível. É proibido inventar valores
para aeronaves com dados factuais ou copiar dados de outro modelo. A exceção
são os perfis sintéticos didáticos de aeronaves definidos em “Perfis sintéticos
didáticos de aeronaves”: seus valores podem não ter validação nem
compatibilidade com o modelo usado como alvo e MUST NOT ser apresentados como
dados factuais daquele modelo. Esses valores MUST ser identificados como
sintéticos em toda seleção, cálculo, resultado e PDF. Cada campo MUST manter
sua unidade e identificação de origem sintética, sem atribuir publicador ou
data editorial fictícios. Texto de interface e PDF MUST permanecer em
português.
Falha de meteorologia, vento, carta, camada aeronáutica suplementar ou radar
MUST aparecer como indisponível. É proibido inventar boletim, vento, carta ou
radar.

### V. Pilha pequena e banco relacional

O runtime MUST ser um processo Flask, com PostgreSQL como único banco de
dados de piloto, manual, aeronave, aeródromo e plano. O acesso MUST usar SQLAlchemy 2,
psycopg e migrações Alembic. Senha MUST ser armazenada só como hash do
Werkzeug, em sessão do Flask, sem segundo fator. Nova dependência MUST ser
justificada no plano e MUST atualizar `requirements.txt` quando for Python.
Chave de serviço externo MUST ficar fora do repositório.

A carta visual oficial vigente MUST continuar vindo do AISWEB e MUST ficar
indisponível quando não houver fonte oficial válida ou chave necessária. O
OpenAIP MAY ser oferecido como camada aeronáutica suplementar e não oficial,
separada da carta WAC e da base de ruas. A interface MUST identificá-la
visivelmente como “OpenAIP — dados aeronáuticos comunitários; não é carta WAC
nem fonte oficial”, sem apresentá-la como substituta da carta AISWEB ou como
garantia de navegação. Seu uso MUST exigir chave configurada fora do
repositório, atribuição visível conforme os termos do provedor e cumprimento
da licença CC BY-NC 4.0, inclusive sua restrição de uso não comercial. Se a
licença, a atribuição, a chave ou a disponibilidade não puderem ser
confirmadas, a camada MUST ficar indisponível e informar o motivo; não pode
haver fallback silencioso. O radar continua sendo uma sobreposição
independente da REDEMET, e a base de ruas MUST ser identificada como tal.

## Restrições adicionais

### Segurança do acesso e documentação

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

### Perfis sintéticos didáticos de aeronaves

Os vinte perfis proxy de aeronaves atualmente associados a modelos reais MAY
permanecer no banco único do produto para fins didáticos, mesmo sem validação
técnica ou compatibilidade comprovada com o modelo-alvo. Seus valores
sintéticos existentes MAY ser usados pelos cálculos didáticos sem pesquisa ou
validação aeronáutica adicional. Perfis sintéticos genéricos sem associação a
modelo MUST NOT ser mantidos.

A associação a um modelo real identifica somente o tema do exercício; MUST
NOT ser apresentada como identificação, especificação ou validação daquela
aeronave. A seleção, os cálculos, os resultados e o PDF MUST identificar
claramente “perfil sintético didático — valores não validados; não representam
dados do modelo associado”. A interface e o PDF MUST também manter o aviso de
que o sistema é exclusivamente didático, não serve para planejamento de voo
real e não autoriza voo.

Cada campo sintético MUST manter unidade e identificação de que seu valor é
sintético. A falta de fonte aeronáutica aplicável MUST NOT impedir a
disponibilidade desses perfis didáticos. O sistema MUST preservar coerência
interna suficiente para os testes e cálculos do software, sem sugerir que os
valores sejam limites operacionais, tolerâncias do fabricante ou dados
aprovados.

Dados sintéticos MUST NOT incluir aeródromos, coordenadas, meteorologia,
vento, cartas, pôr do sol ou checklists. Esses dados continuam sujeitos aos
requisitos normais de fonte e vigência.

### Restrições de domínio e pilha

O piloto informa origem, destino e hora. O sistema reconhece o aeródromo
pelo identificador publicado na emenda vigente do ROTAER.

#### Catálogo nacional e rota

O banco MUST conter os aeródromos de avião da emenda vigente do ROTAER,
obtidos pela área `rotaer` do AISWEB. Coordenada, elevação e situação vêm
só dessa publicação. Heliponto fica de fora. Sem a emenda vigente, o
catálogo nacional MUST aparecer indisponível. É proibido completar a lista
com coordenada estimada ou tratar a semente antiga de sete indicativos como
se fosse o Brasil inteiro.

O banco MUST conter os modelos de avião pequeno usados no Brasil. Avião
pequeno é o definido no RBAC nº 01: peso máximo de decolagem aprovado igual
ou inferior a 5.670 kg. Helicóptero, planador, balão e avião grande ficam de
fora. A ordem de prioridade é a quantidade de aeronaves daquele modelo em
situação normal (`CD_INTERDICAO=N`) no extrato público vigente do Registro
Aeronáutico Brasileiro; códigos `U`, `Z` e todos os demais ficam de fora da
contagem. Para o MVP, somente os 30 primeiros modelos completos nessa ordem
MUST ser oferecidos na caixa de seleção e aceitos em cálculos didáticos. Um
modelo é completo quando sua variante está identificada e os dados técnicos
necessários ao cálculo — combustível utilizável, velocidade e consumo do
mesmo perfil nominal, peso vazio, peso máximo de decolagem e limite de
bagagem — têm unidade e fonte rastreável, oficial ou secundária. Dados de
fonte secundária contam para a completude didática, mas MUST ser marcados como
estimativas e vinculados ao publicador, referência, data e variante/modelo
informados pela fonte. Todos os demais modelos ficam em espera e MUST NOT
aparecer na seleção nem ser aceitos para cálculo. Modelos sem fonte para
qualquer campo obrigatório MUST permanecer incompletos e MUST NOT ser usados
no cálculo. É proibido inventar peso, velocidade ou consumo para esses modelos.
Perfis sintéticos didáticos, inclusive proxies associados a modelos reais, não
contam entre os 30 modelos e não tornam completo ou elegível o registro
nacional. Podem ser oferecidos em categoria claramente separada como perfis
sintéticos, sujeitos a “Perfis sintéticos didáticos de aeronaves”.

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

### Pilha e acesso

Cada plano pertence a um piloto. A consulta de plano MUST filtrar pelo piloto
da sessão. Meteorologia de aeródromo vem do Aviation Weather Center.
Radar vem da REDEMET e carta visual oficial vigente vem do AISWEB. Sem a chave
correspondente, aquele item fica indisponível. OpenAIP só pode aparecer como
camada aeronáutica comunitária suplementar, nos termos definidos no princípio
V, nunca rotulada como WAC. Vento de rota vem do produto
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
| Camada aeronáutica suplementar | OpenAIP, não oficial, CC BY-NC 4.0, chave fora do repositório e atribuição visível |
| PDF | reportlab 4.0.7 |
| Mapa no navegador | Leaflet 1.9, carregado pelo CDN |
| Execução | `.venv` na raiz |
| Processo | GitHub Spec Kit 1.2.2, integração `cursor-agent` |
| Verificação | pytest para cálculo, limite do manual e isolamento entre pilotos; conferência manual no navegador |

O ambiente Python do projeto é o `.venv` na raiz. Não instalar essas
bibliotecas no Python do sistema.

## Fluxo de desenvolvimento

### Fluxo Spec Kit

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
cálculo no servidor, unidade/fonte/modelo e estado de confiança visíveis,
estimativas secundárias claramente didáticas e não operacionais, aviso
educacional preservado, proxies sintéticos identificados como não validados e
não factuais em seleção, cálculo e PDF, falha de tempo/vento/carta/radar
explícita, plano visível só para o piloto dono, senha mínima, bloqueio de
tentativas, sessão encerrada ao sair, catálogo de aeródromos só da emenda
vigente, contagem RAB somente em `CD_INTERDICAO=N`, rota e escalas calculadas
no servidor, e nenhuma dependência nova sem justificativa no plano.
Revisões de mapa MUST ainda verificar que OpenAIP esteja identificado como
fonte suplementar não oficial, com a atribuição e as condições de licença
cumpridas, e que a indisponibilidade da carta oficial AISWEB não seja escondida
por substituição automática.

**Version**: 6.0.0 | **Ratified**: 2026-10-21 | **Last Amended**: 2026-11-25
