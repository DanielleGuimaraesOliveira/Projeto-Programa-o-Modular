# interface/menu_favoritos.py
from typing import Optional, Dict
from controles import favoritos_controler
from controles import jogo_controler
from utils.codigos import OK, NAO_ENCONTRADO, CONFLITO, DADOS_INVALIDOS

def _input_strip(prompt: str) -> str:
    return input(prompt).strip()

def exibir_menu_favoritos(perfil: Optional[Dict]):
    if not perfil:
        print("❌ Nenhum perfil ativo.")
        return

    while True:
        print("\n=== FAVORITOS ===")
        print("1. Listar favoritos")
        print("2. Adicionar favorito (por ID)")
        print("3. Desfavoritar jogo")
        print("0. Voltar")
        opcao = _input_strip("Escolha: ")

        if opcao == "1":
            codigo, lista = favoritos_controler.Listar_Favoritos(perfil['id'])
            if codigo == OK:
                print("\n⭐ Seus Jogos Favoritos:")
                if not lista:
                    print("  (nenhum favorito)")
                else:
                    for jid in lista:
                        c, jogo = jogo_controler.Busca_Jogo(jid)
                        titulo = jogo.get("titulo") if c == OK and jogo else f"Jogo #{jid}"
                        print(f"  {jid} - {titulo}")
            else:
                print("❌ Erro ao listar favoritos.")

        elif opcao == "2":
            try:
                id_j = int(_input_strip("ID do jogo a favoritar: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            
            codigo, _ = favoritos_controler.Favoritar_Jogo(perfil['id'], id_j)
            
            if codigo == OK:
                print("✅ Jogo adicionado aos favoritos!")
            elif codigo == CONFLITO:
                print("⚠️  Este jogo já está nos seus favoritos.")
            elif codigo == NAO_ENCONTRADO:
                print("❌ Jogo não encontrado.")
            else:
                print("❌ Erro ao favoritar.")

        elif opcao == "3":
            try:
                id_j = int(_input_strip("ID do jogo a desfavoritar: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            
            codigo, _ = favoritos_controler.Desfavoritar_Jogo(perfil['id'], id_j)
            
            if codigo == OK:
                print("✅ Jogo removido dos favoritos.")
            elif codigo == NAO_ENCONTRADO:
                print("❌ Jogo não está favoritado ou não existe.")
            else:
                print("❌ Erro ao processar desfavoritar.")

        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida.")