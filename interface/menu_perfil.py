"""
Menu principal / seleção de perfil (interface CLI).

Objetivo:
- Fornecer a interface de linha de comando para entrada no sistema, criação de perfis
  e seleção do perfil ativo.

Descrição:
- Exibe opções: entrar (selecionar perfil por ID ou nome), cadastrar perfil ou sair.
- Valida entradas do usuário, chama funções do controller de perfis e traduz códigos
  de retorno em mensagens amigáveis.
- Não realiza persistência; delega operações aos controllers (perfil_controler).

Dependências:
- controles.perfil_controler
- utils.codigos (OK, CONFLITO, DADOS_INVALIDOS)

Observação:
- As funções retornam objetos de perfil (dict) quando apropriado — prontas para serem
  usadas pelos menus subsequentes (jogos, biblioteca, avaliações).
"""
from typing import Optional, Dict
from controles import perfil_controler
from utils.codigos import OK, CONFLITO, DADOS_INVALIDOS

def _input_strip(prompt: str) -> str:
    """
    Objetivo:
    - Ler entrada do usuário e remover espaços nas extremidades.

    Parâmetros:
    - prompt (str): texto mostrado ao usuário.

    Retorno:
    - str: entrada do usuário já .strip()
    """
    return input(prompt).strip()

def _print_header(titulo: str) -> None:
    """
    Objetivo:
    - Exibir cabeçalho simples no CLI.

    Parâmetros:
    - titulo (str): texto do cabeçalho.
    """
    print(f"\n=== {titulo} ===")

def exibir_menu_inicial() -> Optional[Dict]:
    """
    Objetivo:
    - Exibir o menu inicial do aplicativo e retornar o perfil ativo selecionado.

    Descrição:
    - Loop principal que permite ao usuário entrar, cadastrar um novo perfil ou sair.
    - Ao escolher "Entrar", chama selecionar_perfil(); ao escolher "Cadastrar",
      chama cadastrar_perfil().

    Retorno:
    - Dict do perfil ativo (quando o usuário entra ou cria um perfil com sucesso).
    - None se o usuário optar por sair.
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
    Objetivo:
    - Permitir ao usuário selecionar um perfil por ID ou nome.

    Descrição:
    - Solicita uma entrada; tenta interpretar como ID (inteiro) primeiro,
      caso contrário realiza busca por nome via perfil_controler.Busca_Perfil_por_nome.
    - Exibe mensagem de sucesso com o nome do usuário ou mensagem de erro.

    Retorno:
    - Dict do perfil encontrado, ou None se não existir ou entrada for vazia/inválida.
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
        # apresentação compatível com possíveis chaves ('nome_usuario' ou 'nome')
        print(f"✅ Entrou como: {perfil.get('nome_usuario', perfil.get('nome','(sem nome)'))}")
        return perfil
    else:
        print("❌ Perfil não encontrado.")
        return None

def cadastrar_perfil() -> Optional[Dict]:
    """
    Objetivo:
    - Criar um novo perfil solicitando nome de usuário, descrição e avatar.

    Descrição:
    - Lê entradas do usuário, valida nome não vazio e delega a criação para
      perfil_controler.Criar_Perfil. Trata códigos de retorno e exibe mensagens.

    Retorno:
    - Dict do perfil criado em caso de sucesso.
    - None em caso de falha ou entrada inválida.
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
