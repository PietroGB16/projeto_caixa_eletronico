from datetime import date


class Cliente_Bancario:
    def __init__(self, nome=None, idade=None, cpf=None, agencia=None, numero_conta=None, data=None):
        self.nome = nome
        self.idade = idade
        self.cpf = cpf
        self.agencia = agencia
        self.numero_conta = numero_conta
        self.data = data
        self.saldo = 1000
        self.movimentacoes = []
        self.cheque_especial = 500
        self.taxa_juros_mensal = 0.02
        self.taxa_seguro = 15
        self.taxa_contrato = 500

    def ver_saldo(self):
        
        self.data = date.today()
        return {
            "nome": self.nome,
            "saldo": self.saldo,
            "data": self.data
        }

    def depositar(self, valor, data=None):

        self.saldo += valor
        data = data or date.today()
        self.movimentacoes.append(
            {"Tipo": "Depósito", "Valor": valor, "Data": data})
        return {
            "valor": valor,
            "novo_saldo": self.saldo,
            "data": data
        }

    def sacar(self, valor, data=None):

        if valor > self.saldo + self.cheque_especial:
            return {"sucesso": False, "valor": valor, "saldo": self.saldo, "data": date.today()}
        else:
            self.saldo -= valor
            data = data or date.today()
            self.movimentacoes.append(
                {"Tipo": "Saque", "Valor": valor, "Data": data})
            return {"sucesso": True, "valor": valor, "novo_saldo": self.saldo, "data": data}

    def extrato(self, dataInicial, dataFinal):

        extrato_movs = [
            mov for mov in self.movimentacoes
            if dataInicial <= mov["Data"] <= dataFinal
        ]
        return extrato_movs 

    def financiamento(self, emprestimo, nParcelas):

        pmt = (emprestimo * self.taxa_juros_mensal) / (
            1 - (1 + self.taxa_juros_mensal) ** (-nParcelas)
        )
        valor_total = (pmt + self.taxa_seguro) * nParcelas + self.taxa_contrato
        return {
            "emprestimo": emprestimo,
            "nParcelas": nParcelas,
            "parcela_base": pmt,
            "parcela_com_seguro": pmt + self.taxa_seguro,
            "valor_total": valor_total
        }


