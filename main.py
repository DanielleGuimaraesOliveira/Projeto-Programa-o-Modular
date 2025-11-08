# main.py
from interface.menu_perfil import exibir_menu_inicial
from interface.menu_principal import menu_principal

def main():
    print("🎮 Bem-vindo ao Letterbox Games 🎮")
    perfil_ativo = exibir_menu_inicial()
    if perfil_ativo:
        menu_principal(perfil_ativo)

if __name__ == "__main__":
    main()
