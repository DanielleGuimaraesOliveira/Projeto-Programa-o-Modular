# interface/menu_perfil.py
from controles import perfil_controler
from utils.codigos import OK, CONFLITO, DADOS_INVALIDOS, NAO_ENCONTRADO

def exibir_menu_inicial():
    """
    Exibe o menu inicial: entrar ou criar perfil.
    """
    while True:
        print("\n=== MENU INICIAL ===")
        print("1. Entrar com perfil existente")
        print("2. Criar novo perfil")
        print("0. Sair")
        opcao = input("Escolha: ")

        if opcao == "1":
            perfil = selecionar_perfil()
            if perfil:
                return perfil
        elif opcao == "2":
            perfil = cadastrar_perfil()
            if perfil:
                return perfil
        elif opcao == "0":
            print("👋 Até logo!")
            return None
        else:
            print("❌ Opção inválida.")

def selecionar_perfil():
    """
    Pede o nome do perfil e verifica se existe (em vez de listar IDs).
    """
    nome = input("Digite o nome do perfil: ").strip()
    if not nome:
        print("⚠️  Nome vazio.")
        return None

    codigo, perfil = perfil_controler.Busca_Perfil_por_nome(nome)
    if codigo == OK:
        print(f"✅ Entrando como {perfil['nome']}")
        return perfil
    else:
        print("❌ Perfil não encontrado.")
        return None


def cadastrar_perfil():
    """
    Permite criar um novo perfil.
    """
    nome = input("Digite o nome de usuário: ").strip()
    descricao = input("Digite uma descrição (opcional): ").strip()
    avatar = input("Digite o nome do avatar (opcional): ").strip()

    codigo, perfil = perfil_controler.Criar_Perfil(nome, descricao, avatar)
    if codigo == OK:
        print(f"✅ Perfil '{perfil['nome']}' criado com sucesso!")
        return perfil
    elif codigo == CONFLITO:
        print("⚠️  Já existe um perfil com esse nome.")
    elif codigo == DADOS_INVALIDOS:
        print("❌ Nome inválido.")
    else:
        print("❌ Erro inesperado.")
    return None
