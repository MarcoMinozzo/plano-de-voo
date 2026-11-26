# Contrato: Camada RainViewer no plano

## Regras comuns

- Todas as rotas são subordinadas a um plano existente e exigem piloto autenticado.
- O plano deve pertencer ao piloto da sessão; plano alheio retorna `404`.
- O navegador chama somente rotas da aplicação. O servidor usa hosts fixos da RainViewer.
- Nenhuma chave de usuário ou segredo é exigido ou retornado.
- A REDEMET permanece uma camada separada; erro RainViewer não muda seu estado.

## Consultar o frame atual

`GET /planos/{plano_id}/camadas/rainviewer`

Resposta disponível (`200`):

```json
{
  "estado": "disponivel",
  "fonte": "RainViewer — radar não oficial",
  "atribuicao": {
    "texto": "Weather data by RainViewer",
    "url": "https://www.rainviewer.com/"
  },
  "hora_frame": 1795707000,
  "max_zoom": 7,
  "radar_url": "/planos/3/camadas/rainviewer/radar/FRAME/7/63/42.png",
  "cobertura_url": "/planos/3/camadas/rainviewer/cobertura/7/63/42.png"
}
```

Quando o manifesto não fornece frames válidos ou não pode ser consultado, a aplicação retorna `503` com JSON contendo `estado: indisponivel` e `motivo`. O horário de geração do manifesto nunca deve ser retornado como `hora_frame`.

## Obter tile de radar

`GET /planos/{plano_id}/camadas/rainviewer/radar/{frame}/{z}/{x}/{y}.png`

- O frame é um identificador validado originado do manifesto atual; valores arbitrários ou URLs são recusados.
- `z`, `x` e `y` devem ser inteiros XYZ válidos; `z` não pode exceder o zoom nativo máximo documentado.
- Resposta válida: `200 image/png`, `X-Content-Type-Options: nosniff` e `Cache-Control` do provedor quando fornecido.
- Coordenadas inválidas retornam `400`; falha, imagem ou tipo de conteúdo inválido do provedor retornam `503`.

## Obter tile da máscara de cobertura

`GET /planos/{plano_id}/camadas/rainviewer/cobertura/{z}/{x}/{y}.png`

- Validação XYZ e controle de propriedade são iguais aos tiles de radar.
- Resposta válida: `200 image/png`.
- Uma máscara ausente ou inválida retorna `503`; a interface indica que a cobertura é desconhecida e não interpreta áreas transparentes do radar como ausência de chuva.

## Contrato de interface

- A camada começa desligada e é carregada após escolha explícita.
- Atribuição clicável e aviso de fonte não oficial permanecem visíveis enquanto RainViewer estiver ativo.
- Horário exibido é do frame, identificado no horário local da aplicação; não usar o campo de geração do manifesto como observação.
- A máscara diferencia áreas sem cobertura; a legenda deve explicar que a cobertura pode estar desatualizada.
- Nenhuma falha provoca fallback automático para REDEMET, ruas, OpenAIP ou WAC.
