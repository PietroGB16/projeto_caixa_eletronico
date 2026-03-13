# projeto_caixa_eletronico

Modelagem de Cliente Bancário

Apresentação/n
Sou um estudante de 21 anos da graduação de Engenharia da Computação. Este projeto tem como objetivo demonstrar a aplicação de Programação Orientada a Objetos em Python, implementando regras de negócio financeiras e isolando a lógica de processamento de dados da interface do usuário. A entrega serve como validação técnica de modelagem de sistemas, arquitetura de código e cálculo de sistemas de amortização.

Descrição do Projeto/n
O repositório contém um sistema que simula as operações de uma conta corrente bancária. A aplicação é dividida rigorosamente entre a modelagem matemática/lógica e a interação com o usuário, garantindo a coesão das classes.

Estrutura do Código/n
Classe Core (Domínio): Arquivo que abriga a classe do Cliente Bancário. Gerencia os dados pessoais, histórico de movimentações e cálculos financeiros. Estritamente livre de comandos de entrada e saída (input/print).

Interface (Main): Arquivo separado responsável exclusivamente pela interação com o usuário, menus, coleta de datas/valores via terminal e formatação das saídas visuais.

Funcionalidades e Regras de Negócio
Construtor e Carga Inicial: Inicializa os dados bancários e executa um método de controle interno que injeta um conjunto de transações automáticas para popular a estrutura de dados inicial. Estabelece as taxas fixas da conta (confecção de contrato, seguro mensal e juros).

Depósito (depositar): Registra operações de crédito na lista de movimentações. Utiliza a data fornecida pelo usuário ou captura a data atual do sistema de forma autônoma caso o dado seja omitido.

Saque (sacar): Registra operações de débito. A efetivação da transação é condicionada à validação do valor requisitado contra o saldo atual dinâmico somado ao limite do cheque especial.

Extrato (extrato): Filtra o histórico de movimentações entre uma dataInicial e uma dataFinal. Agrupa os registros por dia e determina o saldo parcial de cada data. O saldo é processado estritamente em tempo real através da iteração das movimentações, sem ser armazenado como um estado estático na classe.

Simulação de Financiamento (simularFinanciamento): Estrutura o cálculo de parcelas de um empréstimo utilizando juros compostos baseados na Tabela PRICE. A simulação consolida as taxas fixas da classe para computar o valor final da parcela e o Custo Efetivo Total (CET) da operação.
