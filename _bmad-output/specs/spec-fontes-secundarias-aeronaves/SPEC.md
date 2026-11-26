---
id: SPEC-fontes-secundarias-aeronaves
companions:
  - secondary-sources.md
  - ../spec-catalogo-aeronaves-mvp-30/spec.md
  - ../../planning-artifacts/research/domain-dados-oficiais-de-aeronaves-do-mvp-2026-11-24/research.md
  - ../../../specs/002-rota-com-escalas/spec.md
sources: []
---

# Dados secundários para catálogo didático de aeronaves

## Why

A exigência anterior de usar somente POH/AFM oficiais bloqueava o preenchimento
do catálogo quando esses documentos não estavam publicamente disponíveis. O
usuário confirmou que o Plano de voo é exclusivamente didático para
desenvolvimento de software e autorizou fontes técnicas secundárias rastreáveis.

## Capabilities

- **CAP-1**
  - **intent:** A equipe pode oferecer modelos de avião pequeno com dados
    técnicos rastreáveis de fontes oficiais ou secundárias para exercícios
    didáticos.
  - **success:** Cada modelo oferecido tem todos os campos necessários ao
    cálculo com unidade, fonte, publicador, data e aplicabilidade identificados;
    todo valor secundário aparece como estimativa didática na seleção, resultado
    e PDF.

## Constraints

- Este SPEC substitui, quando adotado, somente a exigência de fonte oficial
  para valores aeronáuticos; os demais requisitos do catálogo aprovado
  permanecem vigentes.
- O software e seus resultados são exclusivamente didáticos e não podem ser
  apresentados como aptos para planejamento de voo real, despacho ou
  autorização.
- Para fonte secundária, identificar publicador, referência, data e modelo ou
  variante declarados pela fonte; não inventar, transferir ou interpolar valores
  entre modelos.
- Quando fontes aplicáveis divergirem, priorizar a mais recente mesmo se menos
  específica; registrar a divergência e a incerteza, sem calcular média. Se não
  for possível verificar data ou aplicabilidade, manter o campo indisponível.
- Manter os limites já aprovados: avião pequeno até 5.670 kg de PMD aprovado,
  somente `CD_INTERDICAO=N` na contagem RAB, completar antes de limitar a 30 e
  não mostrar modelos incompletos.
- Combustível utilizável, velocidade e consumo devem referir-se ao mesmo perfil
  nominal; todo número continua com unidade e fonte.
- Nenhum cálculo sai do servidor; a interface e o PDF permanecem em português
  e preservam o aviso didático.

## Non-goals

- Autorizar, despachar ou validar voos reais.
- Apresentar estimativas secundárias como valores oficiais, certificados ou
  operacionalmente aprovados.
- Inventar dados para atingir 30 modelos ou substituir a validação de fonte por
  um aviso genérico.

## Success signal

O catálogo oferece até 30 modelos completos em ordem de frota RAB `N`, sem
expor modelos incompletos. Em 100% dos valores secundários, a interface e o PDF
identificam a estimativa e sua fonte; nenhum resultado comunica aptidão para
voo real.

## Assumptions

- Se não for possível verificar a data ou a aplicabilidade da fonte ao modelo,
  manter o campo indisponível.
- O aviso existente de que o resultado não autoriza voo será reforçado para
  deixar explícito que dados secundários são estimativas não operacionais.
