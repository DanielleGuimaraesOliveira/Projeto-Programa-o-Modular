from typing import Optional, Dict
from controles import perfil_controler
from utils.codigos import OK, CONFLITO, DADOS_INVALIDOS

def _input_strip(prompt: str) -> str:
    return input(prompt).strip()

def _print_header(titulo: str) -> None:
    print(f"\n=== {titulo} ===")

def exibir_menu_inicial() -> Optional[Dict]:
    """
    Exibe menu inicial: entrar, cadastrar perfil ou sair.
    Retorna o dict do perfil ativo ou None se o usuário sair.
    """
    while True:
        _print_header("BEM VINDO - LETTERBOX GAMES")
        print("1. Entrar")
        print("2. Cadastrar perfil")
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
            return None
        else:
            print("❌ Opção inválida.")

def selecionar_perfil() -> Optional[Dict]:
    """
    Solicita ID ou nome do perfil e retorna o perfil se encontrado.
    """
    entrada = _input_strip("Digite ID ou nome do perfil: ")
    if not entrada:
        print("⚠️  Entrada vazia.")
        return None

    # tenta por id primeiro
    if entrada.isdigit():
        codigo, perfil = perfil_controler.Busca_Perfil(int(entrada))
    else:
        codigo, perfil = perfil_controler.Busca_Perfil_por_nome(entrada)

    if codigo == OK and perfil:
        print(f"✅ Entrou como: {perfil.get('nome_usuario', perfil.get('nome','(sem nome)'))}")
        return perfil
    else:
        print("❌ Perfil não encontrado.")
        return None

def cadastrar_perfil() -> Optional[Dict]:
    """
    Cria um novo perfil. Retorna o perfil criado em caso de sucesso.
    """
    nome = _input_strip("Nome de usuário: ")
    if not nome:
        print("⚠️  Nome vazio.")
        return None
    descricao = _input_strip("Descrição (opcional): ")
    avatar = _input_strip("Avatar (opcional): ")

    codigo, perfil = perfil_controler.Criar_Perfil(nome, descricao or None, avatar or None)
    if codigo == OK and perfil:
        print(f"✅ Perfil criado: {perfil.get('nome_usuario')}")
        return perfil
    elif codigo == DADOS_INVALIDOS:
        print("❌ Dados inválidos ao criar perfil.")
    elif codigo == CONFLITO:
        print("❌ Nome de usuário já existe.")
    else:
        print("❌ Erro ao criar perfil.")
    return None
