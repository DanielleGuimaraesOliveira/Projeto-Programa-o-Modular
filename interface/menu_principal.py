# interface/menu_principal.py
from interface import menu_jogos
from interface import menu_perfis
from interface import menu_perfil
from interface import menu_biblioteca
from interface import menu_favoritos
from interface import menu_avaliacoes

def menu_principal(perfil_ativo):
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