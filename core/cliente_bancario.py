"""
cliente_bancario.py

Camada de DOMÍNIO (Core) do sistema bancário.

Regra de ouro deste arquivo: ele NÃO conversa com o usuário.
Nada de input() nem print() aqui. Esta classe apenas recebe dados,
faz contas e devolve resultados (dicionários). Quem fala com o
usuário é o arquivo da interface (Tkinter).

Princípio central: a lista 'movimentacoes' e a UNICA fonte da verdade
sobre o dinheiro. O saldo NUNCA e guardado como atributo; ele e sempre
recalculado somando essa lista (ver calcular_saldo). E como um extrato
de banco: o saldo e a soma do historico, nao um numero solto.
"""

from datetime import date


class ClienteBancario:

    def __init__(self, nome=None, idade=None, cpf=None,
                 agencia=None, numero_conta=None, saldo_inicial=1000.0):
        # --- Dados cadastrais ---
        self.nome = nome
        self.idade = idade
        self.cpf = cpf
        self.agencia = agencia
        self.numero_conta = numero_conta

        # --- Fonte unica da verdade ---
        # Cada item: {"Tipo": "Deposito"/"Saque", "Valor": float, "Data": date}
        self.movimentacoes = []

        # --- Taxas / parametros fixos da conta ---
        self.cheque_especial = 500.0
        self.taxa_juros_mensal = 0.02   # 2% ao mes
        self.taxa_seguro = 15.0         # seguro mensal (financiamento)
        self.taxa_contrato = 500.0      # confeccao de contrato (cobrada 1x)

        # --- Carga inicial automatica ---
        self._carregar_transacoes_iniciais(saldo_inicial)

    # ------------------------------------------------------------------
    # CARGA INICIAL (metodo de controle interno / privado)
    # ------------------------------------------------------------------
    def _carregar_transacoes_iniciais(self, saldo_inicial):
        """Popula a conta com movimentacoes automaticas.

        O saldo de abertura entra como a PRIMEIRA movimentacao, para
        que ele tambem faca parte da fonte unica da verdade (nada de
        saldo guardado por fora).
        """
        transacoes_iniciais = [
            ("Deposito", saldo_inicial, date(2025, 1, 5)),   # abertura
            ("Deposito", 2500.0,        date(2025, 1, 10)),
            ("Saque",    300.0,         date(2025, 1, 15)),
            ("Deposito", 800.0,         date(2025, 2, 1)),
            ("Saque",    1200.0,        date(2025, 2, 20)),
        ]
        for tipo, valor, data in transacoes_iniciais:
            self.movimentacoes.append(
                {"Tipo": tipo, "Valor": valor, "Data": data}
            )

    # ------------------------------------------------------------------
    # SALDO (sempre calculado, nunca armazenado)
    # ------------------------------------------------------------------
    def calcular_saldo(self, ate_data=None):
        """Calcula o saldo em tempo real iterando as movimentacoes.

        Se 'ate_data' for informada, considera apenas movimentacoes com
        Data <= ate_data (usado para o saldo parcial do extrato).
        """
        saldo = 0.0
        for mov in self.movimentacoes:
            if ate_data is not None and mov["Data"] > ate_data:
                continue
            if mov["Tipo"] == "Deposito":
                saldo += mov["Valor"]
            else:  # Saque
                saldo -= mov["Valor"]
        return saldo

    def ver_saldo(self):
        """Devolve um resumo do saldo atual (data = hoje)."""
        return {
            "nome": self.nome,
            "saldo": self.calcular_saldo(),
            "data": date.today(),
        }

    # ------------------------------------------------------------------
    # DEPOSITO
    # ------------------------------------------------------------------
    def depositar(self, valor, data=None):
        if valor <= 0:
            return {"sucesso": False,
                    "motivo": "O valor do deposito deve ser positivo.",
                    "valor": valor}

        data = data or date.today()
        self.movimentacoes.append(
            {"Tipo": "Deposito", "Valor": valor, "Data": data}
        )
        return {
            "sucesso": True,
            "valor": valor,
            "novo_saldo": self.calcular_saldo(),
            "data": data,
        }

    # ------------------------------------------------------------------
    # SAQUE
    # ------------------------------------------------------------------
    def sacar(self, valor, data=None):
        if valor <= 0:
            return {"sucesso": False,
                    "motivo": "O valor do saque deve ser positivo.",
                    "valor": valor}

        # Validacao contra o saldo DINAMICO + limite do cheque especial
        saldo_atual = self.calcular_saldo()
        if valor > saldo_atual + self.cheque_especial:
            return {
                "sucesso": False,
                "motivo": "Saldo somado ao cheque especial e insuficiente.",
                "valor": valor,
                "saldo": saldo_atual,
                "limite_disponivel": saldo_atual + self.cheque_especial,
                "data": date.today(),
            }

        data = data or date.today()
        self.movimentacoes.append(
            {"Tipo": "Saque", "Valor": valor, "Data": data}
        )
        return {
            "sucesso": True,
            "valor": valor,
            "novo_saldo": self.calcular_saldo(),
            "data": data,
        }

    # ------------------------------------------------------------------
    # EXTRATO (filtra periodo, agrupa por dia, saldo parcial por data)
    # ------------------------------------------------------------------
    def extrato(self, dataInicial, dataFinal):
        """Monta o extrato entre duas datas.

        - Filtra as movimentacoes do periodo.
        - Agrupa por dia.
        - Para cada dia, calcula o saldo parcial = saldo de TODA a conta
          ate aquele dia (somando as movimentacoes, sem usar estado).

        Retorna uma lista (ordenada por data) com um item por dia:
            {"data": date, "movimentacoes": [...], "saldo_parcial": float}
        """
        # 1) Filtra o periodo
        movs_periodo = [
            mov for mov in self.movimentacoes
            if dataInicial <= mov["Data"] <= dataFinal
        ]

        # 2) Agrupa por dia
        dias = {}
        for mov in movs_periodo:
            dias.setdefault(mov["Data"], []).append(mov)

        # 3) Para cada dia (em ordem), calcula o saldo parcial
        extrato_final = []
        for dia in sorted(dias.keys()):
            extrato_final.append({
                "data": dia,
                "movimentacoes": dias[dia],
                "saldo_parcial": self.calcular_saldo(ate_data=dia),
            })
        return extrato_final

    # ------------------------------------------------------------------
    # SIMULACAO DE FINANCIAMENTO (Tabela PRICE + CET)
    # ------------------------------------------------------------------
    def simularFinanciamento(self, emprestimo, nParcelas):
        """Simula um financiamento pela Tabela PRICE e calcula o CET."""
        i = self.taxa_juros_mensal

        # Parcela base (Tabela PRICE / juros compostos)
        pmt = (emprestimo * i) / (1 - (1 + i) ** (-nParcelas))

        parcela_com_seguro = pmt + self.taxa_seguro
        total_pago = parcela_com_seguro * nParcelas + self.taxa_contrato
        custo_total_reais = total_pago - emprestimo  # quanto pagou a mais

        # CET como TAXA efetiva (resolvido numericamente)
        cet_mensal = self._calcular_cet(emprestimo, parcela_com_seguro,
                                        nParcelas)
        cet_anual = (1 + cet_mensal) ** 12 - 1

        return {
            "emprestimo": emprestimo,
            "nParcelas": nParcelas,
            "parcela_base": pmt,
            "parcela_com_seguro": parcela_com_seguro,
            "total_pago": total_pago,
            "custo_total_reais": custo_total_reais,
            "cet_mensal": cet_mensal,   # ex.: 0.031 -> 3,1% a.m.
            "cet_anual": cet_anual,     # ex.: 0.44  -> 44%  a.a.
        }

    def _calcular_cet(self, emprestimo, parcela, nParcelas):
        """Taxa mensal efetiva (CET) que satisfaz:

            (emprestimo - taxa_contrato) = soma( parcela / (1+i)^t ), t=1..n

        Ou seja: o cliente "recebe" o emprestimo menos a taxa de contrato
        e paga 'parcela' (ja com seguro) durante nParcelas meses. Procuramos
        a taxa i que torna esses dois lados iguais. Como nao da pra isolar i
        na formula, usamos BISSECAO (metodo numerico simples e robusto).

        Observacao: o modelo assume a taxa de contrato como custo a vista
        (t=0). Se o seu professor modelar de outra forma, basta ajustar a
        linha de 'valor_liquido' abaixo.
        """
        valor_liquido = emprestimo - self.taxa_contrato

        def valor_presente(taxa):
            return sum(parcela / (1 + taxa) ** t
                       for t in range(1, nParcelas + 1))

        # Procura a taxa entre 0% e 100% ao mes
        baixo, alto = 0.0, 1.0
        for _ in range(100):  # 100 iteracoes dao precisao de sobra
            meio = (baixo + alto) / 2
            if valor_presente(meio) > valor_liquido:
                baixo = meio   # parcelas valem mais que o recebido -> sobe a taxa
            else:
                alto = meio
        return (baixo + alto) / 2