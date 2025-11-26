"""
Interface de menu de avaliações.

Objetivo:
- Fornecer interação em linha de comando para listar, criar, editar e remover avaliações,
  além de visualizar avaliações de um jogo e listar as avaliações do usuário ativo.

Descrição:
- Usa os controllers de avaliação, jogo e perfil para operações de leitura/escrita.
- Valida entradas do usuário e traduz códigos de retorno em mensagens amigáveis.
- Não realiza persistência direta; delega aos controllers.
"""
from typing import Optional, Dict
from controles import avaliacao_controler
from controles import jogo_controler
from controles import perfil_controler
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO

def _input_strip(prompt: str) -> str:
    """
    Objetivo:
    - Ler uma entrada do usuário e remover espaços em branco nas extremidades.

    Parâmetros:
    - prompt (str): texto a ser exibido na solicitação.

    Retorno:
    - str: entrada do usuário já .strip().
    """
    return input(prompt).strip()

def _buscar_avaliacao_usuario_jogo(id_perfil: int, id_jogo: int):
    """
    Objetivo:
    - Localizar a avaliação de um perfil específico para um jogo específico.

    Descrição:
    - Recupera todas as avaliações via avaliacao_controler.Listar_avaliacao()
      e procura pelo par (id_perfil, id_jogo).

    Parâmetros:
    - id_perfil (int): identificador do perfil autor da avaliação.
    - id_jogo (int): identificador do jogo avaliado.

    Retorno:
    - dict da avaliação se encontrada, caso contrário None.
    """
    _, todas = avaliacao_controler.Listar_avaliacao()
    return next((a for a in todas if a.get("id_perfil") == id_perfil and a.get("id_jogo") == id_jogo), None)

def exibir_menu_avaliacoes(perfil: Optional[Dict]):
    """
    Objetivo:
    - Apresentar o menu de avaliações para o perfil ativo e tratar as opções do usuário.

    Descrição:
    - Permite listar as avaliações próprias, criar/editar uma avaliação, remover uma avaliação
      e listar avaliações de um jogo.
    - Valida existência de perfil e de jogos antes de operar.
    - Tradução de códigos de retorno dos controllers para mensagens na interface.

    Parâmetros:
    - perfil (Optional[Dict]): dicionário do perfil ativo (obtido por exibir_menu_inicial).
      Se None, exibe mensagem de erro e retorna.

    Assertivas:
    - Pré: perfil é None ou contém a chave "id".
    - Pós: operações efetuadas delegam persistência aos controllers; função apenas controla I/O.

    Retorno:
    - None (efeito colateral: exibe mensagens e modifica dados via controllers).
    """
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
            # Lista as avaliações do perfil atual
            codigo, todas = avaliacao_controler.Listar_avaliacao()
            minhas = [a for a in todas if a.get("id_perfil") == perfil["id"]]
            
            if not minhas:
                print("  (nenhuma avaliação feita)")
            else:
                print("\n📝 Suas avaliações:")
                for a in minhas:
                    cid, jogo = jogo_controler.Busca_Jogo(a.get("id_jogo"))
                    titulo = jogo.get("titulo") if cid == OK and jogo else f"Jogo #{a.get('id_jogo')}"
                    # nota/opinião: compatibiliza chaves entre controller/interface
                    nota = a.get("nota") if a.get("nota") is not None else a.get("score")
                    opiniao = a.get("opiniao", a.get("descricao", "(sem opinião)"))
                    print(f"  Jogo: {titulo} | Nota: {nota} | Opinião: {opiniao}")

        elif opcao == "2":
            try:
                id_j = int(_input_strip("ID do jogo para avaliar/editar: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            
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
            existente = _buscar_avaliacao_usuario_jogo(perfil["id"], id_j)
            
            if existente:
                cod, _ = avaliacao_controler.Editar_avaliacao(existente["id"], nota, opiniao)
                msg = "✅ Avaliação atualizada."
            else:
                cod, _ = avaliacao_controler.Avaliar_jogo(id_j, nota, opiniao, perfil["id"])
                msg = "✅ Avaliação registrada."
            
            if cod == OK:
                print(msg)
            elif cod == DADOS_INVALIDOS:
                print("❌ Nota inválida (use 0-10).")
            elif cod == CONFLITO:
                print("❌ Você já avaliou este jogo.")
            else:
                print(f"❌ Erro ao salvar (código {cod}).")

        elif opcao == "3":
            try:
                id_j = int(_input_strip("ID do jogo para remover avaliação: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            
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
            
            _, todas = avaliacao_controler.Listar_avaliacao()
            do_jogo = [a for a in todas if a.get("id_jogo") == id_j]
            
            if not do_jogo:
                print("  (nenhuma avaliação para este jogo)")
            else:
                print(f"\n🗣️ Avaliações do Jogo #{id_j}:")
                for a in do_jogo:
                    _, autor = perfil_controler.Busca_Perfil(a.get("id_perfil"))
                    nome = autor.get("nome", "Desconhecido") if autor else "Desconhecido"
                    nota = a.get("nota", a.get("score"))
                    opiniao = a.get("opiniao", a.get("descricao", ""))
                    print(f"  👤 {nome}: Nota {nota} | {opiniao}")

        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida.")