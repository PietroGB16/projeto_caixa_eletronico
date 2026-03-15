from datetime import datetime
from core.logica_caixa_eletronico import Cliente_Bancario
import time 


def criar_cliente():
    print("\n=== Cadastro do Cliente ===")
    time.sleep(0.5)
    nome = input("Nome: ")
    idade = int(input("Idade: "))
    cpf = input("CPF: ")
    agencia = input("Agência: ")
    numero_conta = input("Número da Conta: ")
    return Cliente_Bancario(nome=nome,
                            idade=idade,
                            cpf=cpf,
                            agencia=agencia,
                            numero_conta=numero_conta)


def mostrar_menu():
    print("-=" * 20)
    print("[0] - Sair")
    print("[1] - Ver Saldo")
    print("[2] - Depositar")
    print("[3] - Sacar")
    print("[4] - Extrato")
    print("[5] - Financiamento")
    print("-=" * 20)


cliente = criar_cliente()

while True:
    mostrar_menu()
    try:
        opcao = int(input("\nEscolha sua opção (0-5): "))
    except ValueError:
        print("Digite um número válido!")
        continue

    if opcao == 0:
        print("Até logo!")
        break

    elif opcao == 1:
        dados = cliente.ver_saldo()
        print(
            f"Olá {dados['nome']}! Seu saldo é R${dados['saldo']:.2f} (Data: {dados['data']})")

    elif opcao == 2:
        try:
            valor = float(input("Digite o valor do depósito: R$"))
        except ValueError:
            print("Digite um número válido!")
            continue
        dados = cliente.depositar(valor)
        print(f"Depósito de R${dados['valor']:.2f} realizado com sucesso.")
        print(
            f"Novo saldo: R${dados['novo_saldo']:.2f} (Data: {dados['data']})")

    elif opcao == 3:
        try:
            valor = float(input("Digite o valor do saque: R$"))
        except ValueError:
            print("Digite um número válido!")
            continue
        dados = cliente.sacar(valor)
        if dados["sucesso"]:
            print(f"Saque de R${dados['valor']:.2f} realizado com sucesso.")
            print(
                f"Novo saldo: R${dados['novo_saldo']:.2f} (Data: {dados['data']})")
        else:
            print("Saldo insuficiente para saque!")

    elif opcao == 4:
        d1 = input("Data inicial (YYYY-MM-DD): ")
        d2 = input("Data final (YYYY-MM-DD): ")
        try:
            data_inicial = datetime.strptime(d1, "%Y-%m-%d").date()
            data_final = datetime.strptime(d2, "%Y-%m-%d").date()
        except ValueError:
            print("Formato de data inválido! Use YYYY-MM-DD.")
            continue

        extrato = cliente.extrato(data_inicial, data_final)
        if not extrato:
            print("Não há movimentações nesse período.")
        else:
            print("=== Extrato ===")
            for mov in extrato:
                print(f"{mov['Data']} - {mov['Tipo']} : R${mov['Valor']:.2f}")

    elif opcao == 5:
        try:
            emprestimo = float(input("Digite o valor do empréstimo: R$"))
            parcelas = int(input("Digite o número de parcelas: "))
        except ValueError:
            print("Digite valores numéricos válidos!")
            continue
        dados = cliente.financiamento(emprestimo, parcelas)
        print(
            f"Valor de cada parcela (sem seguro): R${dados['parcela_base']:.2f}")
        print(f"Parcela com seguro: R${dados['parcela_com_seguro']:.2f}")
        print(
            f"Valor total pago em {dados['nParcelas']} meses: R${dados['valor_total']:.2f}")

    else:
        print("Opção inválida! Escolha entre 0 e 5.")
