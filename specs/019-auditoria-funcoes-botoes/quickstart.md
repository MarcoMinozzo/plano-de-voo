# Quickstart: Auditoria de funções, botões e camadas

## Pré-requisitos

- Usar o ambiente virtual local do projeto.
- Executar testes com os fixtures isolados já configurados; não submeter formulários de produção.
- Não imprimir nem alterar chaves de AISWEB, OpenAIP ou REDEMET.

## Verificação automatizada

```bash
uv run pytest --no-cov tests/test_acesso.py tests/test_tela_piloto.py tests/test_tempo.py tests/test_casca_visual.py
```

Resultado: 54 testes focados aprovados.

Depois, executar:

```bash
uv run pytest -q
```

Resultado: 146 aprovados e uma falha no gate de complexidade de `servidor/pdf_plano.py::_conteudo_relatorio` (complexidade 25). A falha também constava na linha de base de 137 aprovações; sua causa não foi atribuída e permanece fora do escopo desta feature.

## Verificação manual não destrutiva

1. Abrir Perfil; conferir rótulo, campo e botão. A persistência e a confirmação de sucesso são cobertas em ambiente de teste; não salvar um nome real durante a auditoria.
2. Abrir um plano de teste; alternar entre trechos e conferir que uma aba fica selecionada e que a rota permanece visível.
3. Confirmar que as ruas carregam. Verificar os textos de indisponibilidade de WAC, OpenAIP e radar sem tentar habilitar camadas bloqueadas.
4. Em 390 px e 1440 px, confirmar que a página não excede a viewport e que todas as colunas da tabela são acessíveis por rolagem interna.
5. Inspecionar navegação e formulários. Não executar logout, impressão, cálculo de plano real ou qualquer ação que altere dados persistentes.

## Resultado da auditoria não destrutiva

| Ação | Classificação | Evidência ou estado |
|---|---|---|
| Entrar e criar acesso | Funcionando | Caminhos HTML de sucesso e validação cobertos por testes isolados. |
| Salvar nome de exibição | Funcionando | Commit, confirmação após redirecionamento, validação e isolamento cobertos por testes. |
| Abrir painel, criar e alterar plano | Funcionando | Fluxos de formulário, busca por aeródromo, preservação após recusa e isolamento por piloto cobertos por testes. |
| Alternar trechos e consultar mapa de ruas | Funcionando | Abas têm estado acessível e atualizam o trecho; a verificação anterior no navegador carregou 9/9 tiles estáveis. |
| WAC, OpenAIP e radar | Indisponível com motivo/gate explícito | WAC continua bloqueada até validação oficial; OpenAIP e radar permanecem desligados quando chave, cobertura ou limites necessários faltam. |
| Imprimir plano | Funcionando | Geração e conteúdo do PDF cobertos por testes; a ação de impressão sem plano é um link informativo que diz “Não há voo para imprimir.” |
| Sair | Funcionando | Encerramento de sessão e redirecionamento cobertos por teste HTML isolado; nenhum logout de usuário real foi executado. |

No navegador do workspace, Entrar e Cadastro foram conferidos sem envio de formulário: em 390 px, `scrollWidth` ficou em 390 px; em 1440 px, ficou em 1440 px. A estrutura de tabela com os 11 cabeçalhos e as classes reais do template foi conferida com os estilos de produção: a 390 px, a área teve 294 px e o conteúdo da tabela 992 px, enquanto o documento permaneceu em 390 px; a 1440 px, o documento permaneceu em 1440 px. Os testes de regressão também renderizam o template real e confirmam os 11 cabeçalhos dentro do contêiner rolável.
