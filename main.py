# main.py
from interface.menu_perfil import exibir_menu_inicial
from interface.menu_principal import menu_principal

def main():
    print("🎮 Bem-vindo ao Letterbox Games 🎮")
    perfil_ativo = exibir_menu_inicial()
    try:
        if perfil_ativo:
            menu_principal(perfil_ativo)
    finally:
        # flush de controllers que mantêm TADs
        try:
            from controles import perfil_controler
            perfil_controler.flush_perfis()
        except Exception:
            pass
        try:
            from controles import jogo_controler
            jogo_controler.flush_jogos()
        except Exception:
            pass

if __name__ == "__main__":
    main()
