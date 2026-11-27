# Quickstart: METAR regional e TAF independente

## Pré-requisitos

- `.venv` e dependências existentes.
- Testes usam respostas AWC simuladas; credenciais externas não são necessárias.
- Teste manual autenticado usa aeródromos com coordenadas ROTAER, incluindo plano com SBBU e localidades sem METAR próprio.

## Testes

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -o addopts='' -q \
  tests/test_tempo.py tests/test_tela_piloto.py tests/test_rota_pdf.py
```

## Cenários e resultados

| Cenário | Resultado esperado |
|---|---|
| METAR direto e outras estações no raio | Mantém o METAR direto. |
| Sem METAR direto; uma ou mais estações até 50 NM | Seleciona a mais próxima, com nome, ICAO, distância e hora UTC. |
| Estação exatamente a 50 NM | Elegível, usando distância sem arredondamento. |
| Estações empatadas | Menor indicativo em ordem lexical vence. |
| Mais próxima está além de 50 NM | METAR indisponível; nenhuma estação distante é atribuída. |
| Sem METAR, mas há TAF direto | TAF aparece; METAR permanece indisponível. |
| Falha METAR e TAF válido | TAF preservado e falha METAR registrada sem credencial. |
| METAR regional no relatório/PDF | Conteúdo e fonte identificam a estação regional, não o aeródromo alvo. |
| Abrir plano salvo | HTML usa a consulta atual de METAR/TAF, sem alterar JSON salvo, rota ou resultados. |

## Conferência manual

1. Crie ou recalcule um plano com uma localidade que tenha METAR AWC e uma que não tenha.
2. Confirme preferência por METAR direto e, nos demais casos, estação regional a até 50 NM com distância e horário UTC.
3. Confirme que o TAF próprio do aeródromo aparece mesmo sem METAR e que TAF de estação vizinha nunca é usado.
4. Verifique que o modal de fontes e o apêndice PDF identificam a estação AWC que publicou o METAR.
5. Abra novamente um plano salvo e confirme que a atualização meteorológica é somente de leitura.
