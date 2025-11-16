from typing import Optional, Dict
from controles import avaliacao_controler
from controles import jogo_controler
from dados.database import perfis
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO

def _input_strip(prompt: str) -> str:
    return input(prompt).strip()

def exibir_menu_avaliacoes(perfil: Optional[Dict]):
    if not perfil:
        print("❌ Nenhum perfil ativo.")
        return

    while True:
        print("\n=== AVALIAÇÕES ===")
        print("1. Listar minhas avaliações")
        print("2. Avaliar / Editar avaliação")
        print("3. Remover avaliação")
        print("4. Listar avaliações de um jogo")
        print("0. Voltar")
        opcao = _input_strip("Escolha: ")

        if opcao == "1":
            bibli = perfil.get("biblioteca", [])
            avals = [e for e in bibli if "nota" in e]
            if not avals:
                print("  (nenhuma avaliação)")
            else:
                for e in avals:
                    cid, jogo = jogo_controler.Busca_Jogo(e.get("jogo_id"))
                    titulo = jogo.get("titulo") if cid == OK and jogo else f"#{e.get('jogo_id')}"
                    print(f"  {e.get('jogo_id')} - {titulo} | Nota: {e.get('nota')} | Opinião: {e.get('opiniao','')}")
        elif opcao == "2":
            try:
                id_j = int(_input_strip("ID do jogo para avaliar/editar: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            nota_raw = _input_strip("Nota (0-10): ")
            try:
                nota = float(nota_raw)
            except Exception:
                print("❌ Nota inválida.")
                continue
            opiniao = _input_strip("Opinião (opcional): ")
            codigo, _ = avaliacao_controler.Avaliar_Jogo(perfil['id'], id_j, nota, opiniao)
            if codigo == OK:
                print("✅ Avaliação registrada/atualizada.")
            elif codigo == DADOS_INVALIDOS:
                print("❌ Dados inválidos (nota fora de intervalo).")
            elif codigo == NAO_ENCONTRADO:
                print("❌ Perfil ou jogo não encontrado.")
            else:
                print("❌ Erro ao avaliar.")
        elif opcao == "3":
            try:
                id_j = int(_input_strip("ID do jogo para remover avaliação: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            codigo, _ = avaliacao_controler.Remover_Avaliacao(perfil['id'], id_j)
            if codigo == OK:
                print("✅ Avaliação removida.")
            elif codigo == NAO_ENCONTRADO:
                print("❌ Avaliação não encontrada.")
            else:
                print("❌ Erro ao remover avaliação.")
        elif opcao == "4":
            try:
                id_j = int(_input_strip("ID do jogo para listar avaliações: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            resultados = []
            for p in perfis:
                for e in p.get("biblioteca", []):
                    if e.get("jogo_id") == id_j and "nota" in e:
                        nome = p.get("nome_usuario") or p.get("nome") or f"(#{p.get('id')})"
                        resultados.append((nome, e.get("nota"), e.get("opiniao","")))
            if not resultados:
                print("  (nenhuma avaliação encontrada para esse jogo)")
            else:
                for nome, nota, opiniao in resultados:
                    print(f"  {nome} | Nota: {nota} | Opinião: {opiniao}")
        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida.")