# Modelagem de Cliente Bancário

Sistema que simula as operações de uma conta corrente bancária, desenvolvido em Python com Programação Orientada a Objetos. O projeto demonstra a separação rigorosa entre regras de negócio financeiras, interface gráfica e persistência de dados.

## Sobre o Projeto

Projeto acadêmico desenvolvido por Pietro, estudante de Engenharia da Computação, com o objetivo de validar técnicas de modelagem de sistemas, arquitetura de código orientada a objetos e cálculo de sistemas de amortização (Tabela PRICE).

O sistema cobre quatro operações bancárias centrais: depósito, saque, extrato com saldo parcial por dia e simulação de financiamento com cálculo do Custo Efetivo Total (CET).

## Arquitetura

O projeto é dividido em três camadas independentes, cada uma com uma única responsabilidade. Nenhuma camada conhece os detalhes internos da outra — elas se comunicam apenas através de dados simples (números, datas, dicionários).

```
Excel (.xlsx)  <-->  db/   <-->  core/   <-->  ui/
 banco de dados      persistência    domínio       interface
                     (lê/grava        (regras de    (Tkinter:
                      planilha)        negócio)       telas e menus)
```

**`core/` — Domínio.** Contém a classe `ClienteBancario`, responsável por todos os cálculos financeiros e pelo histórico de movimentações. Estritamente livre de comandos de entrada/saída (`input`/`print`) — não sabe que existe uma tela ou um arquivo Excel.

**`ui/` — Interface.** Contém a janela Tkinter. Responsável exclusivamente por coletar valores e datas digitados pelo usuário, chamar os métodos do domínio e formatar o resultado na tela. Não realiza nenhum cálculo.

**`db/` — Persistência.** Contém a classe `RepositorioExcel`, responsável por ler e gravar as movimentações numa planilha Excel. Não realiza cálculos nem interage com o usuário; apenas traduz entre "linhas de planilha" e "lista de dicionários" que o domínio entende.

## Estrutura de Pastas

```
projeto_caixa_eletronico/
├── core/
│   └── cliente_bancario.py    # Classe ClienteBancario (domínio)
├── ui/
│   └── main.py                # Interface Tkinter (ponto de entrada)
├── db/
│   ├── banco_dados.py         # Classe RepositorioExcel (persistência)
│   └── banco_dados.xlsx       # Gerado em tempo de execução (não versionado)
├── .venv/                     # Ambiente virtual (não versionado)
├── .gitignore
└── README.md
```

## Regras de Negócio

### Construtor e Carga Inicial

Ao instanciar `ClienteBancario`, o construtor define os dados cadastrais do cliente e as taxas fixas da conta (limite de cheque especial, taxa de juros mensal, taxa de seguro e taxa de confecção de contrato). Em seguida, chama um método interno (`_carregar_transacoes_iniciais`) que injeta um conjunto de movimentações automáticas — incluindo o próprio saldo de abertura — para popular a estrutura de dados desde o início.

### Saldo Sempre Calculado, Nunca Armazenado

Diferente de uma implementação ingênua que guardaria o saldo num atributo `self.saldo`, esta classe trata a lista de movimentações como a única fonte da verdade. O método `calcular_saldo()` percorre o histórico somando depósitos e subtraindo saques sempre que é chamado — nunca existe um número de saldo "solto" guardado por fora que possa ficar desincronizado do histórico.

### Depósito (`depositar`)

Registra uma operação de crédito na lista de movimentações. Aceita uma data informada pelo usuário ou, se omitida, captura a data atual do sistema automaticamente. Valores menores ou iguais a zero são rejeitados.

### Saque (`sacar`)

Registra uma operação de débito. A transação só é efetivada se o valor solicitado for menor ou igual ao saldo atual (calculado dinamicamente) somado ao limite do cheque especial. Caso contrário, a operação é recusada e o motivo é informado.

### Extrato (`extrato`)

Filtra o histórico de movimentações entre uma `dataInicial` e uma `dataFinal`, agrupa os registros por dia e calcula o saldo parcial de cada data — sempre por iteração em tempo real sobre as movimentações, nunca por um valor armazenado como estado estático.

### Simulação de Financiamento (`simularFinanciamento`)

Calcula o valor da parcela de um empréstimo pela Tabela PRICE (juros compostos), consolidando as taxas fixas da conta:

- **Parcela base:** calculada pela fórmula de amortização PRICE, usando a taxa de juros mensal da conta.
- **Parcela com seguro:** parcela base mais o seguro mensal fixo.
- **Custo Efetivo Total (CET):** taxa mensal e anual que efetivamente reflete o custo do empréstimo, considerando o valor líquido recebido (empréstimo menos a taxa de contrato) frente ao total de parcelas pagas. Como não existe fórmula fechada para isolar essa taxa, ela é resolvida numericamente por busca binária (bisseção).

## Persistência em Excel

A classe `RepositorioExcel` usa a biblioteca `openpyxl` para tratar uma planilha `.xlsx` como banco de dados das movimentações:

- **`carregar()`** lê a planilha e devolve a lista de movimentações no formato que o domínio espera (convertendo as datas de Excel para `date` do Python).
- **`salvar(movimentacoes)`** grava a lista inteira na planilha, sobrescrevendo o arquivo.

A estratégia adotada — regravar a planilha por completo a cada operação — é simples e adequada para um projeto acadêmico, mas não escalaria para um volume grande de transações (ver seção de limitações).

## Interface (Tkinter)

A janela principal é organizada em abas:

- **Conta:** dados cadastrais do cliente e saldo atual, com botão de atualização.
- **Depósito / Saque:** campos para valor e data (opcional), com validação de entrada e mensagens de sucesso ou erro.
- **Extrato:** filtro por período, exibido numa árvore (`Treeview`) onde cada dia é um nó com o saldo parcial, e as movimentações daquele dia aparecem como itens filhos.
- **Financiamento:** campos para valor do empréstimo e número de parcelas, exibindo parcela, total pago e CET mensal/anual.

## Requisitos

- Python 3.10 ou superior
- Tkinter (já incluso na instalação padrão do Python)
- openpyxl

## Como Executar

O projeto usa [uv](https://github.com/astral-sh/uv) para gerenciar o ambiente virtual e as dependências.

```bash
# Na raiz do projeto
uv venv
uv pip install openpyxl
uv run python -m ui.main
```

O comando `-m ui.main` deve ser executado a partir da raiz do projeto, para que o Python encontre corretamente os pacotes `core`, `ui` e `db`.

Na primeira execução, o sistema cria automaticamente a planilha `banco_dados.xlsx` com a carga inicial de movimentações. Nas execuções seguintes, o saldo é recarregado a partir do que está salvo na planilha.

## Decisões de Design e Limitações Conhecidas

- **Valores monetários em `float`:** suficiente para fins acadêmicos. Em um sistema bancário real, usaríamos o tipo `Decimal` para evitar erros de arredondamento de ponto flutuante.
- **Persistência por reescrita completa:** a cada depósito ou saque, a planilha inteira é regravada. Funciona bem na escala deste projeto, mas um sistema real gravaria apenas o registro novo, ou usaria um banco de dados relacional.
- **CET resolvido numericamente:** por bisseção, com 100 iterações — precisão mais que suficiente para os valores envolvidos, mas vale notar que não é uma fórmula fechada.

## Possíveis Melhorias Futuras

- Migrar valores monetários para `Decimal`.
- Substituir a planilha Excel por um banco de dados relacional (SQLite, por exemplo), mantendo a mesma interface de `carregar`/`salvar` para não afetar o domínio.
- Adicionar testes automatizados para as regras de negócio do domínio.
- Permitir múltiplos clientes na mesma base de dados.

## Autor

Pietro — Estudante de Engenharia da Computação
