# Quickstart: validar plano diurno e relatório organizado

## Pré-requisitos

- Ambiente Python do projeto disponível em `.venv`.
- Dependências Node já instaladas conforme o `package-lock.json`.
- Para testes unitários, use respostas AISWEB/REDEMET simuladas; não são
  necessárias credenciais externas.
- Para validação manual completa, use um usuário autenticado e um banco de
  desenvolvimento com aeródromos ROTAER verificados.

## Testes automatizados

1. Rode os testes focados de ROTAER/AISWEB, programação, rota, tela e PDF:

   ```bash
   PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -o addopts='' -q \
     tests/test_catalogo_aerodromos.py \
     tests/test_programacao.py \
     tests/test_rota.py \
     tests/test_tempo.py \
     tests/test_tela_piloto.py \
     tests/test_rota_pdf.py
   ```

2. Gere o CSS após alterar classes Tailwind:

   ```bash
   npm run css:build
   ```

## Cenários e resultados esperados

| Cenário | Verificação |
|---|---|
| Um trecho dentro do período diurno | ETD, ETA, nascer e pôr do sol aparecem em UTC; ETA não ultrapassa o pôr do sol de destino. |
| Primeiro horário após o pôr do sol | O trecho é reagendado para o nascer do sol seguinte na origem e o pernoite identifica local/data. |
| Trecho longo que ainda não cabe no próximo dia | A programação é marcada indisponível, sem atraso infinito nem escala inventada. |
| AISWEB sem nascer ou pôr do sol válido | Nenhum horário solar é inferido e o relatório não declara a programação diurna disponível. |
| Plano salvo antes da feature | Página e JSON continuam legíveis e não fabricam ETD/ETA ou horários solares. |
| WAC validada, WAC PDF(s), e sem WAC | Há no máximo um controle WAC e um radar, sem botões Google Maps/OpenAIP/ruas; PDFs correspondentes à rota abrem/listam-se como documentos; sem cobertura oficial completa não há controle nem mensagem redundante. |
| REDEMET disponível, indisponível, e RainViewer elegível | Um único controle; prioridade REDEMET; RainViewer só aparece com fonte, horário, crédito e ressalva de cobertura. |
| Fontes e impressão | Modal e apêndice relacionam campo/fonte; corpo principal não repete citações. |
| Peso acima do limite | Alerta vermelho contém rótulo textual explicando o limite excedido. |
| Tela estreita e larga | Conferir 390 px e 1440 px; sem rolagem horizontal global, controles operáveis e relatório perto de 80% da largura em tela larga. |

## Conferência no navegador

1. Abra um plano com uma perna e outro com escalas; alterne as abas e confirme
   que o mapa e os dados permanecem associados ao trecho ativo.
2. Teste radar desligado/ligado e falha de carregamento. A interface deve
   manter o mesmo controle e identificar a fonte realmente ativa.
3. Abra o modal de fontes por teclado e toque, feche com Escape e confirme
   que o foco retorna ao ícone.
4. Abra a impressão e confirme que as fontes aparecem em seção separada e que
   o botão de impressão permanece somente no topo.
