from typing import Optional, Dict
from controles import biblioteca_controler
from controles import jogo_controler
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO

def _input_strip(prompt: str) -> str:
    return input(prompt).strip()

def exibir_menu_biblioteca(perfil: Optional[Dict]):
    if not perfil:
        print("❌ Nenhum perfil ativo.")
        return
    while True:
        print("\n=== BIBLIOTECA ===")
        print("1. Listar minha biblioteca")
        print("2. Adicionar jogo à biblioteca")
        print("3. Atualizar status de um jogo")
        print("4. Remover jogo da biblioteca")
        print("5. Listar por status")
        print("6. Favoritar jogo")
        print("7. Listar favoritos")
        print("0. Voltar")
        opcao = _input_strip("Escolha: ")

        if opcao == "1":
            codigo, lista = biblioteca_controler.Listar_Biblioteca(perfil['id'])
            if codigo == OK:
                if not lista:
                    print("  (biblioteca vazia)")
                else:
                    for i, e in enumerate(lista, start=1):
                        cid, jogo = jogo_controler.Busca_Jogo(e.get("jogo_id"))
                        titulo = jogo.get("titulo") if cid == OK and jogo else f"#{e.get('jogo_id')}"
                        print(f"  {i}. {e.get('jogo_id')} - {titulo} | Status: {e.get('status')}")
            else:
                print("❌ Erro ao listar biblioteca.")
        elif opcao == "2":
            try:
                id_j = int(_input_strip("ID do jogo a adicionar: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            status = _input_strip("Status (jogando/jogado/platinado): ")
            codigo, _ = biblioteca_controler.Adicionar_Jogo(perfil['id'], id_j, status)
            if codigo == OK:
                print("✅ Jogo adicionado à biblioteca.")
            elif codigo == DADOS_INVALIDOS:
                print("❌ Status inválido.")
            elif codigo == CONFLITO:
                print("❌ Jogo já presente na biblioteca.")
            else:
                print("❌ Erro ao adicionar.")
        elif opcao == "3":
            try:
                id_j = int(_input_strip("ID do jogo para atualizar status: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            status = _input_strip("Novo status (jogando/jogado/platinado): ")
            codigo, _ = biblioteca_controler.Atualizar_Status_Jogo(perfil['id'], id_j, status)
            if codigo == OK:
                print("✅ Status atualizado.")
            elif codigo == NAO_ENCONTRADO:
                print("❌ Jogo não encontrado na sua biblioteca.")
            elif codigo == DADOS_INVALIDOS:
                print("❌ Status inválido.")
            else:
                print("❌ Erro ao atualizar.")
        elif opcao == "4":
            try:
                id_j = int(_input_strip("ID do jogo a remover: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            codigo, _ = biblioteca_controler.Remover_Jogo(perfil['id'], id_j)
            if codigo == OK:
                print("✅ Jogo removido da biblioteca.")
            elif codigo == NAO_ENCONTRADO:
                print("❌ Jogo não encontrado na sua biblioteca.")
            else:
                print("❌ Erro ao remover.")
        elif opcao == "5":
            status = _input_strip("Status para filtrar (jogando/jogado/platinado): ")
            codigo, lista = biblioteca_controler.Listar_Biblioteca_por_status(perfil['id'], status)
            if codigo == OK:
                if not lista:
                    print("  (nenhum item com esse status)")
                else:
                    for e in lista:
                        cid, jogo = jogo_controler.Busca_Jogo(e.get("jogo_id"))
                        titulo = jogo.get("titulo") if cid == OK and jogo else f"#{e.get('jogo_id')}"
                        print(f"  {e.get('jogo_id')} - {titulo} | Status: {e.get('status')}")
            elif codigo == DADOS_INVALIDOS:
                print("❌ Status inválido.")
            else:
                print("❌ Erro ao filtrar.")
        elif opcao == "6":
            try:
                id_j = int(_input_strip("ID do jogo para favoritar: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            codigo, _ = biblioteca_controler.Favoritar_Jogo(perfil['id'], id_j)
            if codigo == OK:
                print("✅ Jogo favoritado.")
            elif codigo == CONFLITO:
                print("❌ Jogo já favoritado.")
            elif codigo == NAO_ENCONTRADO:
                print("❌ Jogo ou perfil não encontrado.")
            else:
                print("❌ Erro ao favoritar.")
        elif opcao == "7":
            codigo, lista = biblioteca_controler.Listar_Favoritos(perfil['id'])
            if codigo == OK:
                if not lista:
                    print("  (nenhum favorito)")
                else:
                    for jid in lista:
                        cid, jogo = jogo_controler.Busca_Jogo(jid)
                        titulo = jogo.get("titulo") if cid == OK and jogo else f"#{jid}"
                        print(f"  {jid} - {titulo}")
            else:
                print("❌ Erro ao listar favoritos.")
        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida.")