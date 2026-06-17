"""
main.py

Camada de INTERFACE (Tkinter) do sistema bancario.

Regra de ouro deste arquivo: ele NAO faz contas. Ele coleta dados do
usuario (valores, datas), chama os metodos da classe ClienteBancario e
formata o resultado na tela. Toda a logica financeira mora em
cliente_bancario.py.

Fluxo: usuario digita  ->  parse (string -> date/float)  ->  chama o
dominio  ->  formata a resposta  ->  mostra na tela.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import os
import sys

# Coloca a RAIZ do projeto no caminho de busca, para achar a pasta core/
# mesmo quando rodamos "python ui/main.py" direto.
RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, RAIZ_PROJETO)

from core.cliente_bancario import ClienteBancario

from core.cliente_bancario import ClienteBancario


# ======================================================================
# FUNCOES AUXILIARES DE FORMATACAO / CONVERSAO
# (ficam aqui, na interface, porque sao sobre "como mostrar/ler texto")
# ======================================================================
def formatar_moeda(valor):
    """1234.5 -> 'R$ 1.234,50' (padrao brasileiro)."""
    s = f"{valor:,.2f}"                       # 1,234.50  (padrao ingles)
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def formatar_data(d):
    """date -> 'dd/mm/aaaa'."""
    return d.strftime("%d/%m/%Y")


def parse_data(texto):
    """'dd/mm/aaaa' -> date. Vazio -> None (dominio usa hoje).

    Lanca ValueError se o formato for invalido (tratado por quem chama).
    """
    texto = texto.strip()
    if not texto:
        return None
    return datetime.strptime(texto, "%d/%m/%Y").date()


def parse_valor(texto):
    """Aceita '1.234,56', '1234,56' ou '1234.56' -> float."""
    texto = texto.strip()
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    return float(texto)


# ======================================================================
# JANELA PRINCIPAL
# ======================================================================
class InterfaceBancaria(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Sistema Bancario - Conta Corrente")
        self.geometry("620x560")
        self.minsize(560, 520)

        # Cria o cliente (o construtor ja faz a carga inicial automatica)
        self.cliente = ClienteBancario(
            nome="Pietro Gomes",
            idade=21,
            cpf="123.456.789-00",
            agencia="0001",
            numero_conta="12345-6",
        )

        self._construir_ui()

    # ------------------------------------------------------------------
    def _construir_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        aba_conta = ttk.Frame(notebook, padding=15)
        aba_deposito = ttk.Frame(notebook, padding=15)
        aba_saque = ttk.Frame(notebook, padding=15)
        aba_extrato = ttk.Frame(notebook, padding=15)
        aba_financiamento = ttk.Frame(notebook, padding=15)

        notebook.add(aba_conta, text="Conta")
        notebook.add(aba_deposito, text="Deposito")
        notebook.add(aba_saque, text="Saque")
        notebook.add(aba_extrato, text="Extrato")
        notebook.add(aba_financiamento, text="Financiamento")

        self._montar_aba_conta(aba_conta)
        self._montar_aba_deposito(aba_deposito)
        self._montar_aba_saque(aba_saque)
        self._montar_aba_extrato(aba_extrato)
        self._montar_aba_financiamento(aba_financiamento)

    # ------------------------------------------------------------------
    # ABA: CONTA (dados do cliente + saldo)
    # ------------------------------------------------------------------
    def _montar_aba_conta(self, frame):
        c = self.cliente
        ttk.Label(frame, text="Dados da Conta",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        dados = [
            ("Titular", c.nome),
            ("CPF", c.cpf),
            ("Agencia", c.agencia),
            ("Conta", c.numero_conta),
            ("Cheque especial", formatar_moeda(c.cheque_especial)),
        ]
        for rotulo, valor in dados:
            linha = ttk.Frame(frame)
            linha.pack(fill="x", pady=2)
            ttk.Label(linha, text=f"{rotulo}:", width=18).pack(side="left")
            ttk.Label(linha, text=str(valor)).pack(side="left")

        ttk.Separator(frame).pack(fill="x", pady=15)

        self.lbl_saldo = ttk.Label(frame, text="", font=("Segoe UI", 18, "bold"))
        self.lbl_saldo.pack(anchor="w")
        ttk.Button(frame, text="Atualizar saldo",
                   command=self._atualizar_saldo).pack(anchor="w", pady=10)

        self._atualizar_saldo()

    def _atualizar_saldo(self):
        saldo = self.cliente.calcular_saldo()
        self.lbl_saldo.config(text=f"Saldo atual: {formatar_moeda(saldo)}")

    # ------------------------------------------------------------------
    # ABA: DEPOSITO
    # ------------------------------------------------------------------
    def _montar_aba_deposito(self, frame):
        ttk.Label(frame, text="Realizar Deposito",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 15))

        ttk.Label(frame, text="Valor (R$):").pack(anchor="w")
        self.ent_dep_valor = ttk.Entry(frame, width=25)
        self.ent_dep_valor.pack(anchor="w", pady=(0, 10))

        ttk.Label(frame, text="Data (DD/MM/AAAA) - vazio = hoje:").pack(anchor="w")
        self.ent_dep_data = ttk.Entry(frame, width=25)
        self.ent_dep_data.pack(anchor="w", pady=(0, 15))

        ttk.Button(frame, text="Depositar",
                   command=self._on_depositar).pack(anchor="w")

    def _on_depositar(self):
        try:
            valor = parse_valor(self.ent_dep_valor.get())
            data = parse_data(self.ent_dep_data.get())
        except ValueError:
            messagebox.showerror("Entrada invalida",
                                 "Verifique o valor e a data (DD/MM/AAAA).")
            return

        r = self.cliente.depositar(valor, data)
        if not r["sucesso"]:
            messagebox.showwarning("Deposito nao realizado", r["motivo"])
            return

        self._atualizar_saldo()
        self.ent_dep_valor.delete(0, tk.END)
        self.ent_dep_data.delete(0, tk.END)
        messagebox.showinfo(
            "Deposito realizado",
            f"Deposito de {formatar_moeda(r['valor'])} em "
            f"{formatar_data(r['data'])}.\n"
            f"Novo saldo: {formatar_moeda(r['novo_saldo'])}"
        )

    # ------------------------------------------------------------------
    # ABA: SAQUE
    # ------------------------------------------------------------------
    def _montar_aba_saque(self, frame):
        ttk.Label(frame, text="Realizar Saque",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 15))

        ttk.Label(frame, text="Valor (R$):").pack(anchor="w")
        self.ent_saq_valor = ttk.Entry(frame, width=25)
        self.ent_saq_valor.pack(anchor="w", pady=(0, 10))

        ttk.Label(frame, text="Data (DD/MM/AAAA) - vazio = hoje:").pack(anchor="w")
        self.ent_saq_data = ttk.Entry(frame, width=25)
        self.ent_saq_data.pack(anchor="w", pady=(0, 15))

        ttk.Button(frame, text="Sacar",
                   command=self._on_sacar).pack(anchor="w")

    def _on_sacar(self):
        try:
            valor = parse_valor(self.ent_saq_valor.get())
            data = parse_data(self.ent_saq_data.get())
        except ValueError:
            messagebox.showerror("Entrada invalida",
                                 "Verifique o valor e a data (DD/MM/AAAA).")
            return

        r = self.cliente.sacar(valor, data)
        if not r["sucesso"]:
            messagebox.showwarning("Saque nao realizado", r["motivo"])
            return

        self._atualizar_saldo()
        self.ent_saq_valor.delete(0, tk.END)
        self.ent_saq_data.delete(0, tk.END)
        messagebox.showinfo(
            "Saque realizado",
            f"Saque de {formatar_moeda(r['valor'])} em "
            f"{formatar_data(r['data'])}.\n"
            f"Novo saldo: {formatar_moeda(r['novo_saldo'])}"
        )

    # ------------------------------------------------------------------
    # ABA: EXTRATO (agrupado por dia, com saldo parcial)
    # ------------------------------------------------------------------
    def _montar_aba_extrato(self, frame):
        ttk.Label(frame, text="Extrato por periodo",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        filtros = ttk.Frame(frame)
        filtros.pack(fill="x", pady=(0, 10))

        ttk.Label(filtros, text="De (DD/MM/AAAA):").grid(row=0, column=0, sticky="w")
        self.ent_ext_inicio = ttk.Entry(filtros, width=15)
        self.ent_ext_inicio.grid(row=0, column=1, padx=5)
        self.ent_ext_inicio.insert(0, "01/01/2025")

        ttk.Label(filtros, text="Ate (DD/MM/AAAA):").grid(row=0, column=2, sticky="w")
        self.ent_ext_fim = ttk.Entry(filtros, width=15)
        self.ent_ext_fim.grid(row=0, column=3, padx=5)
        self.ent_ext_fim.insert(0, "31/12/2025")

        ttk.Button(filtros, text="Gerar",
                   command=self._on_extrato).grid(row=0, column=4, padx=5)

        # Treeview: cada dia e um "no pai" com o saldo parcial;
        # as movimentacoes do dia sao os "nos filhos".
        self.tree = ttk.Treeview(frame, columns=("detalhe",), show="tree headings")
        self.tree.heading("#0", text="Dia / Movimentacao")
        self.tree.heading("detalhe", text="Valor / Saldo do dia")
        self.tree.column("#0", width=260)
        self.tree.column("detalhe", width=260)
        self.tree.pack(fill="both", expand=True)

    def _on_extrato(self):
        try:
            inicio = parse_data(self.ent_ext_inicio.get())
            fim = parse_data(self.ent_ext_fim.get())
        except ValueError:
            messagebox.showerror("Entrada invalida",
                                 "Use o formato DD/MM/AAAA nas duas datas.")
            return
        if inicio is None or fim is None:
            messagebox.showerror("Entrada invalida",
                                 "Informe as duas datas.")
            return

        # Limpa a arvore antes de preencher de novo
        for item in self.tree.get_children():
            self.tree.delete(item)

        extrato = self.cliente.extrato(inicio, fim)
        if not extrato:
            messagebox.showinfo("Extrato",
                                "Nenhuma movimentacao no periodo.")
            return

        for dia in extrato:
            pai = self.tree.insert(
                "", "end",
                text=formatar_data(dia["data"]),
                values=(f"Saldo do dia: {formatar_moeda(dia['saldo_parcial'])}",),
                open=True,
            )
            for mov in dia["movimentacoes"]:
                self.tree.insert(
                    pai, "end",
                    text=f"  {mov['Tipo']}",
                    values=(formatar_moeda(mov["Valor"]),),
                )

    # ------------------------------------------------------------------
    # ABA: FINANCIAMENTO (Tabela PRICE + CET)
    # ------------------------------------------------------------------
    def _montar_aba_financiamento(self, frame):
        ttk.Label(frame, text="Simulacao de Financiamento",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 15))

        entradas = ttk.Frame(frame)
        entradas.pack(fill="x")

        ttk.Label(entradas, text="Valor do emprestimo (R$):").grid(
            row=0, column=0, sticky="w", pady=3)
        self.ent_fin_valor = ttk.Entry(entradas, width=18)
        self.ent_fin_valor.grid(row=0, column=1, padx=5)

        ttk.Label(entradas, text="Numero de parcelas:").grid(
            row=1, column=0, sticky="w", pady=3)
        self.ent_fin_parcelas = ttk.Entry(entradas, width=18)
        self.ent_fin_parcelas.grid(row=1, column=1, padx=5)

        ttk.Button(frame, text="Simular",
                   command=self._on_financiamento).pack(anchor="w", pady=12)

        self.txt_fin = tk.Text(frame, height=10, width=60, state="disabled",
                               wrap="word")
        self.txt_fin.pack(fill="both", expand=True)

    def _on_financiamento(self):
        try:
            valor = parse_valor(self.ent_fin_valor.get())
            nparcelas = int(self.ent_fin_parcelas.get().strip())
        except ValueError:
            messagebox.showerror(
                "Entrada invalida",
                "Informe um valor valido e um numero inteiro de parcelas.")
            return
        if valor <= 0 or nparcelas <= 0:
            messagebox.showerror("Entrada invalida",
                                 "Valor e parcelas devem ser positivos.")
            return

        r = self.cliente.simularFinanciamento(valor, nparcelas)

        texto = (
            f"Emprestimo solicitado: {formatar_moeda(r['emprestimo'])}\n"
            f"Parcelas: {r['nParcelas']}x\n"
            f"\n"
            f"Parcela (juros): {formatar_moeda(r['parcela_base'])}\n"
            f"Parcela com seguro: {formatar_moeda(r['parcela_com_seguro'])}\n"
            f"\n"
            f"Total pago ao final: {formatar_moeda(r['total_pago'])}\n"
            f"Custo total (juros+taxas): {formatar_moeda(r['custo_total_reais'])}\n"
            f"\n"
            f"CET (mensal): {r['cet_mensal'] * 100:.2f}% a.m.\n"
            f"CET (anual):  {r['cet_anual'] * 100:.2f}% a.a."
        )

        self.txt_fin.config(state="normal")
        self.txt_fin.delete("1.0", tk.END)
        self.txt_fin.insert("1.0", texto)
        self.txt_fin.config(state="disabled")


# ======================================================================
if __name__ == "__main__":
    app = InterfaceBancaria()
    app.mainloop()