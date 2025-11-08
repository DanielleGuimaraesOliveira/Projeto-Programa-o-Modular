# interface/menu_principal.py
from interface import menu_jogos

def menu_principal(perfil_ativo):
    while True:
        print("\n===== MENU PRINCIPAL =====")
        print(f"👤 Usuário ativo: {perfil_ativo['nome']}")
        print("1. Jogos")
        print("2. Perfis")
        print("3. Biblioteca")
        print("4. Favoritos")
        print("5. Avaliações")
        print("6. Seguidores")
        print("0. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            # passa o perfil ativo para o menu de jogos (necessário para avaliar)
            menu_jogos.exibir_menu(perfil_ativo)
        elif opcao == "0":
            print("👋 Saindo... até logo!")
            break
        else:
            print("🚧 Opção ainda não implementada.")