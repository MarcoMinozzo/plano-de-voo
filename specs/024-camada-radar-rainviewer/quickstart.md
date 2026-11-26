# Quickstart: Camada suplementar de radar RainViewer

## Pré-requisitos

- Ambiente virtual e dependências do projeto restaurados.
- Banco de teste isolado conforme `documentacao/operacao.md`.
- Os testes devem simular manifesto, tiles e máscara; não dependem de acesso à rede ou chave externa.
- Para conferência manual, use um plano próprio e uma conexão de internet. A API pública atual não exige chave, mas está sujeita aos termos educacionais, à atribuição obrigatória e à disponibilidade do provedor.

## Validação automatizada

```bash
uv run pytest -q tests/test_rainviewer.py tests/test_tela_piloto.py
git diff --check
```

## Cenários

1. Abra um plano e confirme que RainViewer começa desligado e que a abertura do plano não consulta o provedor.
2. Ative RainViewer; confirme que a camada é carregada pela aplicação, com atribuição RainViewer, link e horário do frame.
3. Confirme que a máscara diferencia áreas sem cobertura de áreas sem eco e que a legenda informa que a máscara pode estar desatualizada.
4. Simule manifesto vazio, timeout, resposta inválida, tile inválido e máscara indisponível; confirme estado explícito e nenhum fallback automático.
5. Simule REDEMET disponível e RainViewer indisponível, depois o inverso; confirme que os estados e controles permanecem separados.
6. Abra o plano de outro piloto e confirme que as rotas de manifesto e tiles não expõem dados sem autorização.
7. Em conferência manual na região do plano, compare a área com cobertura apresentada com o mapa público RainViewer e confirme que a imagem não é tratada como radar oficial nem como orientação de voo.

## Limitações conhecidas

- A API documentada oferece frames históricos recentes e zoom nativo limitado; a cobertura varia por região.
- RainViewer agrega vários provedores brasileiros, inclusive fontes que também podem alimentar a REDEMET; não é uma rede independente de observação.
- Sem confirmação de termos, crédito, frame válido ou cobertura interpretável, a camada permanece indisponível.
