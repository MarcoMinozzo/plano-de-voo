# Quickstart: Enxugar a tela do piloto

1. Subir o serviço como em `documentacao/operacao.md`.
2. Entrar e abrir Plano novo. A caixa da aeronave mostra um nome. Origem e destino mostram aeródromos diferentes. Os campos são tipo de avião, origem, destino, data e hora, número de passageiros, peso das pessoas e peso da bagagem. Não há combustível a bordo nem peso de piloto.
3. Com mais de doze aeródromos, digitar um pedaço do código e um pedaço do nome, com e sem acento. A caixa continua no lugar e só mostra as opções em que o pedaço aparece no código ou no nome. Um texto que não está em nenhum dos dois não cria aeródromo.
4. Calcular um plano. A tela abre pela rota e pelo estado. A tabela não repete a fonte em cada célula. Tempo, vento, carta e radar indisponíveis aparecem numa linha. O mapa, se houver, traz a frase da carta imediatamente antes.
5. Abrir "Como ler este plano" e conferir o texto do piloto.
6. Marcar um item do checklist e voltar a ele com a palavra marcado. Os outros não dizem "não marcado".
7. `pytest tests/test_tela_piloto.py tests/test_orientacao.py`
