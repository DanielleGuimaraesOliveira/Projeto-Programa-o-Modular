"""
Menu Principal (CLI)

Objetivo:
- Exibir o menu principal da aplicação e encaminhar o usuário para os submenus
  (Jogos, Perfis, Biblioteca, Favoritos, Avaliações) usando o perfil ativo.

Descrição:
- Recebe um dicionário 'perfil_ativo' e mantém loop até o usuário optar por sair.
- Traduz opções do usuário em chamadas para os módulos de interface correspondentes.
- Trata o caso de desativação de conta (logout) solicitado no submenu de perfis,
  solicitando novo login/criação via menu_perfil quando necessário.

Dependências:
- interface.menu_jogos
- interface.menu_perfis
- interface.menu_perfil
- interface.menu_biblioteca
- interface.menu_favoritos
- interface.menu_avaliacoes

Parâmetros:
- perfil_ativo (dict): dicionário do perfil autenticado; deve conter chave 'id' e 'nome' ou 'nome_usuario'.

Retorno:
- None (efeito colateral: navegação por menus e I/O com usuário).
"""
from interface import menu_jogos
from interface import menu_perfis
from interface import menu_perfil
from interface import menu_biblioteca
from interface import menu_favoritos
from interface import menu_avaliacoes

def menu_principal(perfil_ativo):
    """
    Objetivo:
    - Controlar o loop principal da aplicação e delegar ações para os submenus.

    Descrição:
    - Exibe opções, trata a escolha do usuário e invoca as funções de cada submenu.
    - Quando o submenu de perfis desativa a conta (retorna False), solicita novo login
      via menu_perfil.exibir_menu_inicial(); se o usuário escolher sair, encerra a aplicação.

    Parâmetros:
    - perfil_ativo (dict): perfil autenticado; utilizado por submenus que necessitam do usuário.

    Retorno:
    - None
    """
    while True:
        print("\n===== MENU PRINCIPAL =====")
        print(f"👤 Usuário ativo: {perfil_ativo.get('nome', perfil_ativo.get('nome_usuario','(sem nome)'))}")
        print("1. Jogos")
        print("2. Perfis")
        print("3. Biblioteca")
        print("4. Favoritos")
        print("5. Avaliações")
        print("0. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            # passa o perfil ativo para o menu de jogos (necessário para avaliar)
            menu_jogos.exibir_menu(perfil_ativo)
        elif opcao == "2":
            # chama o menu de perfis; se ele retornar False significa que a conta foi desativada
            resultado = menu_perfis.exibir_menu_perfis(perfil_ativo)
            if resultado is False:
                # volta ao menu inicial (entrar / cadastrar / sair)
                novo_perfil = menu_perfil.exibir_menu_inicial()
                if novo_perfil is None:
                    # usuário escolheu sair no menu inicial -> encerra aplicação
                    print("👋 Saindo... até logo!")
                    return
                # atualiza perfil ativo e continua no loop
                perfil_ativo = novo_perfil
        elif opcao == "3":
            menu_biblioteca.exibir_menu_biblioteca(perfil_ativo)
        elif opcao == "4":
            menu_favoritos.exibir_menu_favoritos(perfil_ativo)
        elif opcao == "5":
            menu_avaliacoes.exibir_menu_avaliacoes(perfil_ativo)
        elif opcao == "0":
            print("👋 Saindo... até logo!")
            break
        else:
            print("🚧 Opção ainda não implementada.")