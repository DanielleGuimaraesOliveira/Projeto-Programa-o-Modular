"""
Interface de menu da Biblioteca.

Objetivo:
- Fornecer interação em linha de comando para gerenciar a biblioteca pessoal do perfil:
  listar itens, adicionar, atualizar status, remover, filtrar por status e gerenciar favoritos.

Descrição:
- Valida entradas do usuário, chama os controllers apropriados (biblioteca, jogo, favoritos)
  e traduz os códigos de retorno em mensagens legíveis.
- Não realiza persistência direta; delega todas operações de leitura/escrita aos controllers.
- Projetado para ser usado pelo fluxo principal (menu do usuário) com um dicionário `perfil`
  representando o usuário ativo.

Nota:
- Funções assumem que `perfil` (quando fornecido) contém a chave 'id'.
"""
from typing import Optional, Dict
from controles import biblioteca_controler
from controles import jogo_controler
from controles import favoritos_controler
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO

def _input_strip(prompt: str) -> str:
    """
    Objetivo:
    - Ler entrada do usuário e retornar a string sem espaços nas extremidades.

    Parâmetros:
    - prompt (str): texto a ser exibido ao usuário.

    Retorno:
    - str: entrada do usuário com .strip().
    """
    return input(prompt).strip()

def exibir_menu_biblioteca(perfil: Optional[Dict]):
    """
    Objetivo:
    - Exibir o menu de biblioteca para o perfil ativo e tratar as ações escolhidas.

    Descrição:
    - Permite:
      1) Listar a biblioteca do perfil;
      2) Adicionar um jogo à biblioteca (status obrigatório);
      3) Atualizar o status de um jogo já presente;
      4) Remover jogo da biblioteca;
      5) Filtrar listagem por status;
      6) Favoritar um jogo;
      7) Listar favoritos.
    - Para cada operação, valida parâmetros (IDs, status) e mostra mensagens
      apropriadas conforme o código retornado pelos controllers.

    Parâmetros:
    - perfil (Optional[Dict]): dicionário do perfil ativo (deve conter 'id'). Se None,
      a função informa que não há perfil ativo e retorna.

    Assertivas / Invariantes:
    - Pré: se `perfil` é fornecido, contém chave 'id' válida.
    - Pós: alterações delegadas aos controllers; mensagens exibidas ao usuário.
      Persistência é responsabilidade dos controllers/TADs subjacentes.

    Retorno:
    - None (efeito colateral: interage com usuário e altera dados via controllers).
    """
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
                        id_jogo = e.get("id_jogo")
                        cid, jogo = jogo_controler.Busca_Jogo(id_jogo)
                        titulo = jogo.get("titulo") if cid == OK and jogo else f"Jogo #{id_jogo}"
                        print(f"  {i}. {id_jogo} - {titulo} | Status: {e.get('status')}")
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
            elif codigo == NAO_ENCONTRADO:
                print("❌ Jogo não encontrado.")
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
                        id_jogo = e.get("id_jogo")
                        cid, jogo = jogo_controler.Busca_Jogo(id_jogo)
                        titulo = jogo.get("titulo") if cid == OK and jogo else f"Jogo #{id_jogo}"
                        print(f"  {id_jogo} - {titulo} | Status: {e.get('status')}")
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
            codigo, _ = favoritos_controler.Favoritar_Jogo(perfil['id'], id_j)
            if codigo == OK:
                print("✅ Jogo favoritado.")
            elif codigo == CONFLITO:
                print("❌ Jogo já favoritado.")
            elif codigo == NAO_ENCONTRADO:
                print("❌ Jogo ou perfil não encontrado.")
            else:
                print("❌ Erro ao favoritar.")
        
        elif opcao == "7":
            codigo, lista = favoritos_controler.Listar_Favoritos(perfil['id'])
            if codigo == OK:
                if not lista:
                    print("  (nenhum favorito)")
                else:
                    for jid in lista:
                        cid, jogo = jogo_controler.Busca_Jogo(jid)
                        titulo = jogo.get("titulo") if cid == OK and jogo else f"Jogo #{jid}"
                        print(f"  {jid} - {titulo}")
            else:
                print("❌ Erro ao listar favoritos.")
        
        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida.")