from typing import Optional, Dict
from controles import perfil_controler
from utils.codigos import OK, CONFLITO, DADOS_INVALIDOS, NAO_ENCONTRADO

def _input_strip(prompt: str) -> str:
    return input(prompt).strip()

def _print_header(titulo: str) -> None:
    print(f"\n=== {titulo} ===")

def exibir_menu_inicial() -> Optional[Dict]:
    """
    Exibe o menu inicial: entrar ou criar perfil.
    Retorna o perfil selecionado/criado (dict) ou None se o usuário sair.
    """
    while True:
        _print_header("MENU INICIAL")
        print("1. Entrar com perfil existente")
        print("2. Criar novo perfil")
        print("0. Sair")
        opcao = _input_strip("Escolha: ")

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

def selecionar_perfil() -> Optional[Dict]:
    """
    Solicita o nome do perfil e tenta recuperar via controlador.
    Retorna o dict do perfil em caso de sucesso, ou None.
    """
    nome = _input_strip("Digite o nome do perfil: ")
    if not nome:
        print("⚠️  Nome vazio.")
        return None

    codigo, perfil = perfil_controler.Busca_Perfil_por_nome(nome)
    if codigo == OK and perfil:
        print(f"✅ Entrando como {perfil['nome']}")
        return perfil
    print("❌ Perfil não encontrado.")
    return None

def cadastrar_perfil() -> Optional[Dict]:
    """
    Gera a interface para criação de um novo perfil.
    Valida nome não vazio antes de chamar o controlador.
    """
    nome = _input_strip("Digite o nome de usuário: ")
    if not nome:
        print("⚠️  Nome inválido ou vazio.")
        return None

    descricao = _input_strip("Digite uma descrição (opcional): ")
    avatar = _input_strip("Digite o nome do avatar (opcional): ")

    codigo, perfil = perfil_controler.Criar_Perfil(nome, descricao, avatar)
    if codigo == OK and perfil:
        print(f"✅ Perfil '{perfil['nome']}' criado com sucesso!")
        return perfil
    if codigo == CONFLITO:
        print("⚠️  Já existe um perfil com esse nome.")
    elif codigo == DADOS_INVALIDOS:
        print("❌ Nome inválido.")
    else:
        print("❌ Erro inesperado.")
    return None
