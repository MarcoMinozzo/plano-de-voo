# Data Model: Catálogo sintético isolado para DEMO

## Entidades existentes alteradas

### Ambiente da aplicação

O modo é selecionado por `DEMO_MODE`; quando habilitado, `APP_ENV` deve ser exatamente `development` e `DATABASE_URL_DEMO` deve ser configurada e diferente da URL normal. A resolução retorna somente a URL escolhida. Falhas de validação interrompem a inicialização antes da criação de engine, sessão ou escrita. O modo normal continua usando `DATABASE_URL`.

### ExtratoRab

O banco DEMO recebe um registro de extrato identificável como sintético, no estado disponível, para associar os perfis DEMO. Esse registro é interno ao banco DEMO e não declara que os perfis pertencem ao RAB real. Ele é criado pela semente DEMO e usado pelo filtro vigente existente.

### Aeronave

Cada perfil tem `nome` genérico e único (`Aeronave DEMO 01` a `Aeronave DEMO 20`), os seis valores obrigatórios do cálculo, unidades esperadas e uma associação ao registro DEMO de extrato. Todos os pesos máximos permanecem abaixo de 5.670 kg; velocidade e consumo usam o mesmo identificador de perfil fictício. Nenhum nome de fabricante ou modelo real é usado.

### FonteTecnicaAeronave

Para cada campo obrigatório, registrar uma fonte com `tipo_fonte="sintetica"`, publicador de demonstração, referência que declare explicitamente geração sintética, identificador genérico do perfil, unidade e valor. `data_publicacao` fica nula por não haver publicação; `data_consulta` registra a geração/carga. Uma migração atualiza a constraint de tipos aceitos e permite a data editorial nula, sem alterar registros existentes.

## Regras de validação

- A fonte sintética só é aplicável quando `permitir_sintetica=True` e o ambiente Flask está em DEMO.
- `modelo_tecnicamente_completo` e `modelos_visiveis` mantêm `False` como padrão; o modo normal não seleciona perfis sintéticos.
- Em DEMO, o cálculo exige velocidade e consumo do mesmo perfil, valores positivos, unidades previstas e limite de peso máximo.
- A carga cria exatamente vinte perfis, é idempotente e não apaga registros.
- A tabela `EmendaRotaer` e os aeródromos continuam sendo carregados somente pela fonte oficial ROTAER. Sem emenda oficial vigente, rotas DEMO são recusadas.

## Relações

```text
ExtratoRab (registro DEMO) 1 ── N Aeronave (perfis DEMO)
Aeronave 1 ── N FonteTecnicaAeronave (uma fonte por campo obrigatório)
EmendaRotaer (fonte oficial vigente) 1 ── N Aerodromo (fonte oficial ROTAER)
```
