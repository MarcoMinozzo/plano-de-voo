# Tasks: Revisão do código pronto

**Input**: Suíte de revisão medida em 13 de novembro de 2026.

**Prerequisites**: O planejamento já entregue permanece até um pedido explícito. Esta tarefa não abre uma especificação nova de comportamento.

## Phase 1: Código já entregue

- [ ] T001 Revisar o código já pronto em `servidor`. Ligar o Postgres em `127.0.0.1:5434` e repetir a cobertura da suíte inteira. A medição de 28%, com piso 27, usou só a suíte nova, a forma e as dependências. Em `servidor/calculo.py`, classificar os mutantes da pontuação 56,2% e piso 56, cobrir os ramos que a suíte não executa e só então subir o piso. Programação futura das cinco portas, sem alterar piso nem teto agora. Não subir o piso 27 enquanto a cobertura de 28% for só da suíte nova. Com o Postgres em `127.0.0.1:5434`, medir a suíte inteira e pôr o piso um ponto abaixo dessa medida. Mutação 56,2% (267 mortos e 208 sobreviventes em 475) com piso 56 em `calculo.py`: ramo não executado ganha teste; fronteira numérica permanece; o piso só sobe depois disso. Nenhum ciclo conhecido. Tetos 23 e 462 ficam. Não unificar com o 17 e as 800 linhas do Radio Eyes. **Parcial (2026-11-26)**: suíte completa no banco descartável configurado passou (136 testes; cobertura 86,56%); mutação recalculada em 68,4% (348/509) e piso/tetos mantidos. Não conectei ao Postgres `127.0.0.1:5434` nem executei a revisão funcional de negócio descrita abaixo; a tarefa permanece aberta.

Sexta porta, programação futura, sem executar teste nesta tarefa. O texto do requisito fica gravado por inteiro:

Business Requirement Validation and Functional Testing

Nao esqueça de aplicar testes das funcionalidades (requisitos funcionais) do aplicativo

Exemplo:

Act as a Software Quality Assurance Engineer.

Your task is to validate the functional correctness

of the software against its business requirements.

For each business requirement:

1. Identify the expected business behavior.

2. Generate positive and negative test scenarios.

3. Identify boundary conditions and exceptional cases.

4. Generate functional test cases.

5. Execute the tests against the application.

6. Compare actual results with expected results.

7. Report failures, inconsistencies and untested scenarios.

Do not consider code coverage as evidence of

business correctness.

Validate the software behavior against the

specified business requirements.
