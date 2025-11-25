# interface/menu_avaliacoes.py
from typing import Optional, Dict
from controles import avaliacao_controler
from controles import jogo_controler
from controles import perfil_controler
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO

def _input_strip(prompt: str) -> str:
    return input(prompt).strip()

def _buscar_avaliacao_usuario_jogo(id_perfil, id_jogo):
    """Helper para achar a avaliação específica de um usuário para um jogo."""
    _, todas = avaliacao_controler.Listar_avaliacao()
    return next((a for a in todas if a.get("id_perfil") == id_perfil and a.get("id_jogo") == id_jogo), None)

def exibir_menu_avaliacoes(perfil: Optional[Dict]):
    if not perfil:
        print("❌ Nenhum perfil ativo.")
        return

    while True:
        print("\n=== AVALIAÇÕES ===")
        print("1. Listar minhas avaliações")
        print("2. Avaliar / Editar avaliação")
        print("3. Remover avaliação")
        print("4. Listar avaliações de um jogo (Geral)")
        print("0. Voltar")
        opcao = _input_strip("Escolha: ")

        if opcao == "1":
            # Busca na lista GLOBAL filtrando pelo ID do perfil atual
            codigo, todas = avaliacao_controler.Listar_avaliacao()
            minhas = [a for a in todas if a.get("id_perfil") == perfil["id"]]
            
            if not minhas:
                print("  (nenhuma avaliação feita)")
            else:
                print("\n📝 Suas avaliações:")
                for a in minhas:
                    cid, jogo = jogo_controler.Busca_Jogo(a.get("id_jogo"))
                    titulo = jogo.get("titulo") if cid == OK and jogo else f"Jogo #{a.get('id_jogo')}"
                    print(f"  Jogo: {titulo} | Nota: {a.get('score')} | Opinião: {a.get('descricao','(sem opinião)')}")

        elif opcao == "2":
            try:
                id_j = int(_input_strip("ID do jogo para avaliar/editar: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            
            # Valida se jogo existe antes de pedir nota
            c, _ = jogo_controler.Busca_Jogo(id_j)
            if c != OK:
                print("❌ Jogo não encontrado.")
                continue

            try:
                nota = float(_input_strip("Nota (0-10): ").replace(',', '.'))
            except ValueError:
                print("❌ Nota inválida.")
                continue
            
            opiniao = _input_strip("Opinião (opcional): ")
            
            # Verifica se já existe para decidir entre Criar ou Editar
            existente = _buscar_avaliacao_usuario_jogo(perfil["id"], id_j)
            
            if existente:
                # Edição
                cod, _ = avaliacao_controler.Editar_avaliacao(existente["id"], nota, opiniao)
                msg = "✅ Avaliação atualizada."
            else:
                # Criação (Ordem: id_jogo, score, descricao, id_perfil)
                cod, _ = avaliacao_controler.Avaliar_jogo(id_j, nota, opiniao, perfil["id"])
                msg = "✅ Avaliação registrada."
            
            if cod == OK:
                print(msg)
            elif cod == DADOS_INVALIDOS:
                print("❌ Nota inválida (use 0-10).")
            else:
                print(f"❌ Erro ao salvar (código {cod}).")

        elif opcao == "3":
            try:
                id_j = int(_input_strip("ID do jogo para remover avaliação: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            
            # Precisa achar o ID da avaliação primeiro
            alvo = _buscar_avaliacao_usuario_jogo(perfil["id"], id_j)
            
            if not alvo:
                print("❌ Você não tem avaliação para este jogo.")
            else:
                codigo, _ = avaliacao_controler.Remover_avaliacao(alvo["id"])
                if codigo == OK:
                    print("✅ Avaliação removida.")
                else:
                    print("❌ Erro ao remover.")

        elif opcao == "4":
            try:
                id_j = int(_input_strip("ID do jogo para ver avaliações: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            
            # Busca todas e filtra pelo jogo
            _, todas = avaliacao_controler.Listar_avaliacao()
            do_jogo = [a for a in todas if a.get("id_jogo") == id_j]
            
            if not do_jogo:
                print("  (nenhuma avaliação para este jogo)")
            else:
                print(f"\n🗣️ Avaliações do Jogo #{id_j}:")
                for a in do_jogo:
                    # Busca nome do autor
                    _, autor = perfil_controler.Busca_Perfil(a.get("id_perfil"))
                    nome = autor.get("nome", "Desconhecido") if autor else "Desconhecido"
                    print(f"  👤 {nome}: Nota {a.get('score')} | {a.get('descricao', '')}")

        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida.")