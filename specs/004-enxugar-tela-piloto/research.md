# Research: Enxugar a tela do piloto

## Decisão: caixa de uma linha, nome já visível

**Decision**: `<select>` sem `size`. Sem a opção vazia "Escolha". A primeira aeronave fica selecionada quando o piloto ainda não escolheu. A origem fica no primeiro aeródromo e o destino no segundo, quando há dois. Valor já informado ou gravado prevalece.

**Rationale**: A lista aberta de oito linhas repetia o catálogo e empurrava o cálculo para baixo. A caixa fechada com placeholder vazio parecia sem opção. Mostrar o nome real na caixa fechada resolve os dois.

**Alternatives considered**: Lista aberta com menos linhas. Continua ocupando a página. Campo de texto livre. O piloto pediu caixa de seleção.

## Decisão: filtro só acima de doze

**Decision**: O campo de filtrar origem e destino só é renderizado quando `aerodromos|length > 12`. Um texto só, por caixa. A opção permanece quando o texto é parte do código ou parte do nome já mostrado nessa opção. A comparação ignora maiúsculas e acentos. A cidade que não está nesse nome não entra. O script não cria opção e não roda se o campo não existe.

**Rationale**: Sete aeródromos cabem na caixa ao abrir. A emenda nacional não cabe. O piloto procura pelo código ou pelo nome que vê. A cidade exigiria um dado que o catálogo não guarda.

**Alternatives considered**: Filtro sempre visível. Vira mais um campo na tela curta que o piloto rejeitou. Guardar a cidade e filtrar por ela. Foi recusado na clarificação de 2026-11-23. Dois campos, um para nome e outro para código. O piloto pediu um texto só.

## Decisão: orientação fechada, frase aberta

**Decision**: A frase "Apoio ao planejamento. Não substitui o manual da aeronave, o treinamento de voo nem a norma vigente. Não é autorização de voo." fica visível no formulário e no plano. O `orientacao` completo fica em `<details>` com o resumo "Como ler este plano", só na tela do plano. O PDF segue imprimindo o texto inteiro.

**Rationale**: A constituição exige o texto na tela e no PDF. Exige também que a tela deixe claro que o resultado não autoriza o voo. O bloco amarelo com o manual inteiro era o excesso. O texto continua no HTML da página do plano, então a busca do piloto ainda o encontra.

**Alternatives considered**: Tirar o texto da tela e deixar só no PDF. Falha o portão da constituição. Deixar o bloco amarelo. É a tela que o piloto chamou de excesso.

## Decisão: fonte uma vez na tabela

**Decision**: O primeiro trecho define unidade do título e a legenda de fontes. Célula cujo unidade ou fonte difere mostra os dois entre parênteses. O PDF em `servidor/pdf_plano.py` não muda.

**Rationale**: Unidade e fonte continuam nomeadas, sem repetir a mesma fonte em cada célula. Uma fonte diferente não fica escondida atrás da legenda.

**Alternatives considered**: Tirar a fonte da tela. Viola a constituição. Manter a fonte em cada célula. É a tabela que a releitura pediu para enxugar.

## Decisão: o piloto informa a carga deste voo, o manual informa o combustível

**Decision**: O formulário guarda `numero_passageiros`, `peso_pessoas_kg` e `peso_bagagem_kg`. O número inclui o piloto e o mínimo é 1. O peso das pessoas é o total, sem multiplicar pela quantidade. `avaliar_carga` soma esse peso, a bagagem, o peso vazio e o peso do `combustivel_valor` da aeronave quando a unidade é gal, usando a densidade já existente de 2,72 kg/gal. Um plano antigo, com peso de piloto e de passageiro, mostra na alteração a soma como peso das pessoas.

**Rationale**: O piloto deixou de informar combustível a bordo e um peso de piloto separado. O combustível de planejamento já está no registro do manual. Copiar 22 gal para outra constante violaria a constituição.

**Alternatives considered**: Continuar pedindo combustível a bordo. O piloto pediu que o restante fosse calculado. Um único peso de pessoas e bagagem. O limite de bagagem do manual ficaria sem conferência.

## Decisão: ausência numa linha

**Decision**: Se boletim, vento, carta e radar estão todos sem dado, uma frase: "Tempo, vento, carta de voo visual e radar: indisponível." Se algum tem dado, esse aparece como hoje e os ausentes entram numa frase "Indisponível: …". O mapa e o script do Leaflet só entram quando `pontos|length >= 2`. A frase da carta fica imediatamente antes do mapa.

**Rationale**: Quatro frases iguais e um mapa vazio dominavam a página. O dado presente continua explícito.

**Alternatives considered**: Esconder também o dado presente. O piloto precisa do boletim quando a fonte entrega.

## Decisão: as caixas não inventam o catálogo nacional

**Decision**: Tipo de avião é o modelo de avião pequeno do extrato do RAB. Origem e destino são os aeródromos de avião da emenda vigente do ROTAER. Sem essas publicações, a tela continua na lista já gravada e diz que ela não é o país. Esta feature não chama a carga nem grava aeródromo ou modelo novo.

**Rationale**: A constituição e a spec 002 já definem a fonte. Uma lista "só de voo visual" ou uma lista escrita à mão quebraria essa regra. A chave do AISWEB e o arquivo do extrato não estão no ambiente desta máquina.

**Alternatives considered**: Gravar uma lista completa no repositório. É proibido. Tratar os sete aeródromos da semente como o Brasil. Também é proibido.

