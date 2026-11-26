# Research: Proxies de aeronaves DEMO

## Decisões

### ROTAER DEMO: reutilizar a emenda oficial já carregada

- A base normal contém a emenda vigente `AMDT 47/26` no estado disponível e 4.519 registros de aeródromo; a base DEMO consultada estava sem emenda e sem aeródromos.
- Não é necessário baixar novamente a lista pelo API AISWEB. O provisionamento deve copiar apenas a emenda vigente e seus aeródromos para o banco DEMO, de forma transacional e idempotente.
- A aplicação DEMO não deve abrir conexão com a base normal. A cópia é uma operação explícita, separada do runtime, e não inclui pilotos, planos ou outros dados.

### Seleção de modelos proxy

- O ranking RAB existente é uma lista preliminar de candidatos, não prova variante, classe nem peso máximo de decolagem. O campo `NR_PMD` não será usado para elegibilidade enquanto sua unidade e semântica não estiverem confirmadas.
- Confirmar cada proxy por modelo/variante com fonte técnica aplicável. Preferir especificação do fabricante, POH/AFM ou publicação oficial; quando não houver, usar pelo menos duas fontes secundárias comparáveis e registrar por que são comparáveis.
- AOPA, Pilot-Next, Aeroway e FAA são pontos de partida para a pesquisa já indicada pelo usuário, não evidência suficiente por si só. Cada afirmação inserida deve apontar para a página/documento consultado, sua data, variante e campo suportado.
- Não extrapolar um dado isolado como se fosse valor certificado. Se não houver suporte para os seis campos necessários ao cálculo, manter o candidato fora do catálogo ativo.

### Dados sintéticos e intervalos

- Manter os 20 nomes genéricos existentes e adicionar até 20 perfis proxy, somente no DEMO.
- Os intervalos devem ser obtidos de dados de modelos ou variantes comparáveis, e o valor nominal deve permanecer dentro do intervalo. Velocidade e consumo devem vir do mesmo perfil de cruzeiro.
- Registrar unidade, intervalo mínimo/máximo, referências, modelo/variante aplicável, método de geração, versão/semente e incerteza para cada campo técnico sintético.
- Uma fonte sem data editorial deve continuar com `data_publicacao` nula; a apresentação dirá “data editorial não se aplica”, sem sugerir uma data inventada.
- O critério de completude existente permanece; acrescentar validação dos intervalos e relações físicas sem relaxar os requisitos para modelos reais.

### Limites e integrações

- O catálogo normal permanece limitado a 30; o catálogo DEMO pode apresentar até 40 perfis completos.
- A meteorologia, vento, carta e pôr do sol continuam vindo das integrações oficiais existentes. Respostas ausentes ou falhas são indisponibilidades explícitas; não criar valores meteorológicos sintéticos.
- Testes de cálculo e apresentação usarão respostas simuladas para fontes externas, sem depender de chamadas reais.

## Evidência do projeto consultada

- O registro local da feature informa a emenda vigente `AMDT 47/26` e os 4.519 aeródromos na base normal, enquanto a base DEMO estava vazia. O teste de provisionamento deve confirmar esses dados antes da transferência.
- `servidor/catalogo.py` já contém carregamento ROTAER e filtragem de modelos completos; `servidor/semente_demo.py` mantém 20 perfis genéricos; `servidor/modelos.py` guarda a procedência por campo.
- `servidor/tempo.py` já integra fontes meteorológicas oficiais. Esta feature não altera a origem nem cria fallback para essas informações.
- `documentacao/operacao.md` descreve as variáveis e a separação da base DEMO; deve ser atualizado para não recomendar nova chamada AISWEB quando o ROTAER oficial já estiver na base normal.

## Alternativas rejeitadas

- **Baixar o ROTAER de novo pela API**: desnecessário, credenciais AISWEB não estão configuradas neste ambiente e a lista oficial já está disponível no banco normal.
- **Copiar toda a base normal para DEMO**: rejeitado; mistura dados de usuário e não é necessário para o fluxo de teste.
- **Gerar valores sem intervalo ou fonte por campo**: rejeitado pela constituição e pela necessidade de detectar valores fora do domínio admissível.
- **Expor proxies também no modo normal**: rejeitado para preservar a separação entre demonstração e catálogo operacional.
