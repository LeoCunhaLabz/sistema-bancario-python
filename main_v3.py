from abc import ABC, abstractclassmethod, abstractproperty

from datetime import datetime
import textwrap

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:

    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
    
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("=== Saldo insuficiente ===")
            return False

        elif valor <= 0:
            print("=== O valor do saque deve ser positivo ===")
            return False

        else:
            self._saldo -= valor
            print("=== Saque realizado com sucesso ===")
            return True
        
        return False

    def depositar(self, valor):
        if valor <= 0:
            print("=== O valor do depósito deve ser positivo ===")
            return False

        self._saldo += valor
        print("=== Depósito realizado com sucesso ===")
        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print("=== Limite do saque excedido ===")
            return False

        elif excedeu_saques:
            print("=== Número máximo de saques já foi excedido ===")
            return False

        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self):
        return f"""
        Conta Corrente - {self.numero}
        Titular: {self.cliente.nome}
        Saldo: {self.saldo}
        Limite: {self.limite}
        Limite de Saques: {self.limite_saques}
        """

class Historico:
    def __init__(self):
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass
    
    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
    
class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property  # Add @property decorator here
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu = """
    ======== MENU ========
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [nc] Nova Conta
    [lc] Listar Contas
    [nu] Novo Usuário
    [q] Sair
    """
    print(menu)

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente, contas):
    for conta in contas:
        if conta.cliente == cliente:
            return conta
    print("=== Conta não encontrada ===")
    return None

def depositar(clientes, contas):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("=== Cliente não encontrado ===")
        return
    
    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente, contas)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def sacar(clientes, contas):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("=== Cliente não encontrado ===")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente, contas)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes, contas):
    cpf = input("Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("=== Cliente não encontrado ===")
        return
    
    conta = recuperar_conta_cliente(cliente, contas)
    if not conta:
        return

    print("=============== EXTRATO ===============")
    for transacao in conta.historico.transacoes:
        print(f"{transacao['data']} - {transacao['tipo']}: {transacao['valor']}")
    
    print(f"\nSaldo: {conta.saldo}")
    print("=======================================")

def criar_conta(clientes, numero_conta, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("=== Cliente não encontrado ===")
        return
    
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("=== Conta criada com sucesso ===")

def listar_contas(contas):
    if not contas:
        print("=== Nenhuma conta cadastrada ===")
        return
    
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("=== Cliente já cadastrado ===")
        return

    nome = input("Informe o nome do cliente: ")
    data_nascimento = input("Informe a data de nascimento (dd/mm/aaaa): ")
    endereco = input("Informe o endereço do cliente: ")
    
    cliente = PessoaFisica(nome, data_nascimento, cpf, endereco)

    clientes.append(cliente)

    print("=== Cliente criado com sucesso ===")

def main():
    clientes = []
    contas = []

    while True:
        menu()
        opcao = input("Escolha uma opção: ")

        if opcao == "d":
            depositar(clientes, contas)
        
        elif opcao == "s":
            sacar(clientes, contas)

        elif opcao == "e":
            exibir_extrato(clientes, contas)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(clientes, numero_conta, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            print("=== Sistema encerrado ===")
            break

        else:
            print("=== Opção inválida ===")

main()