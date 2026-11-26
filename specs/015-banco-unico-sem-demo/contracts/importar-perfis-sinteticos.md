# Contrato: Importação de perfis sintéticos

## Configuração

- Destino: base canônica configurada para o produto.
- Origem: variável temporária `DATABASE_URL_DEMO_ORIGEM`, lida somente pelo
  comando de importação.
- As URLs devem identificar bases distintas. Credenciais nunca são impressas
  nem gravadas em arquivos do repositório.

## Comportamento

- Importa exatamente vinte proxies e seis fontes técnicas por proxy.
- Preserva os valores e unidades existentes; remapeia IDs e mantém as fontes
  relacionadas à aeronave correta.
- Não copia ROTAER, RAB, pilotos, planos, perfis genéricos ou o extrato RAB
  sintético.
- Origem incompleta ou conflito divergente retorna erro explícito e não
  realiza escrita parcial. Registros idênticos já presentes são ignorados.
- A base de origem permanece intacta. A importação pode ser repetida.

## Saída

O comando informa quantos perfis foram importados e quantos já estavam
presentes, sem incluir URLs ou credenciais na saída.
