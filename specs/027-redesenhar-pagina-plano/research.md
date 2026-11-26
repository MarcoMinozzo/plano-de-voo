# Research: Redesenho da página do plano

## Decisão: Reutilizar dados oficiais já carregados

- **Decisão**: Passar ao template os objetos `Aerodromo` resolvidos para os trechos e exibir nome, tipo, coordenadas, elevação e proveniência ROTAER já armazenados.
- **Racional**: `app.py:ver_plano` já consulta cada aeroporto da rota; a página recebe atualmente os pontos do mapa, mas não os registros completos.
- **Alternativas consideradas**: Fazer chamadas AISWEB na abertura da página; rejeitada para evitar latência, credenciais e falhas externas no carregamento do plano.

## Decisão: Contatos somente do AISWEB/ROTAER

- **Decisão**: Interpretar e persistir telefone/e-mail apenas quando publicados na resposta oficial. Campos não publicados ficam indisponíveis; a atualização de emenda não mantém contato antigo ausente na versão atual.
- **Racional**: O usuário escolheu AISWEB/ROTAER como única fonte. O modelo `Aerodromo` não possui contatos e o parser atual extrai localização/elevação, então a extensão deve preservar a fonte e a versão.
- **Alternativas consideradas**: Preencher por pesquisa externa ou inferência; rejeitadas por falta de fonte autorizada selecionada e risco de apresentar dados não verificados.

## Decisão: Remover a máscara de cobertura do desenho do mapa

- **Decisão**: Não adicionar `cobertura_url` como tile layer visual; exibir aviso compacto de cobertura junto aos metadados RainViewer, sem cobrir a base.
- **Racional**: No mapa aberto, a cobertura aparecia como grandes círculos cinza. O template aplica opacidade 0,4 à camada de cobertura. A REDEMET usa imagem separada com limites geográficos e mostrou uma área de ecos distinta; manter suas regras e testar o alinhamento sem substituir a fonte.
- **Alternativas consideradas**: Manter a máscara com opacidade menor; rejeitada porque ainda compete com a rota e não é necessária para informar a falta de garantia de cobertura.

## Decisão: Camadas simples e explícitas

- **Decisão**: Ruas ativas inicialmente; Google Maps como controle desativado até existir chave local; REDEMET e RainViewer desligados inicialmente e independentes. Manter WAC resumida como indisponível e retirar OpenAIP não configurado da seleção.
- **Racional**: Segue o pedido de controles liga/desliga, a resposta do usuário sobre Google Maps e a constituição, sem sugerir uma camada não configurada como disponível.
- **Alternativas consideradas**: Fallback automático para Google/OpenAIP; rejeitado por confundir fonte, licença e disponibilidade.

## Decisão: Reutilizar a pilha atual

- **Decisão**: Usar os modelos/migrações existentes, Jinja, Tailwind, Leaflet e pytest; não adicionar dependência.
- **Racional**: A mudança é de apresentação, sincronização de campos oficiais e correção de uma camada já implementada.
