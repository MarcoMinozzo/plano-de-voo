# Validação rápida: cartões de autenticação

## Pré-requisitos

- Dependências Python disponíveis no `.venv` do repositório.
- Dependências Node já instaladas conforme o lockfile.

## Verificações automatizadas

Na raiz do repositório:

```bash
npm run css:build
.venv/bin/pytest --no-cov tests/test_casca_visual.py tests/test_acesso.py
git diff --check
```

Resultado esperado: CSS compilado, testes focados aprovados e nenhuma falha de whitespace.

## Inspeção visual

Abrir `/entrar` e `/cadastro` em 390 px e 1440 px de largura:

- Confirmar logos de 155,52 px e 129,6 px, respectivamente, centralizados e sem distorção.
- Confirmar que os cartões estão centrados; reduzir a altura para garantir que a página role sem cortar campos ou ações.
- No login, confirmar ausência do título visível “Entrar”, botão “Acessar”, espaço maior antes do botão e frase de direitos abaixo de “Criar acesso”.
- Enviar formulários apenas com dados de teste e confirmar que os handlers e validações permanecem inalterados.
