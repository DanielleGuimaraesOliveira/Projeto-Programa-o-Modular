# interface/menu_favoritos.py
"""
Menu de Favoritos (interface CLI).

Objetivo:
- Fornecer interação em linha de comando para listar, adicionar e remover jogos
  favoritos do perfil ativo.

Descrição:
- Valida entradas do usuário e delega operações aos controllers:
  favoritos_controler e jogo_controler.
- Tradução dos códigos de retorno em mensagens legíveis.
- Não realiza persistência direta; delega aos controllers.

Parâmetros/Dependências:
- Depende dos módulos: controles.favoritos_controler, controles.jogo_controler
  e utils.codigos para códigos de status.
"""
from typing import Optional, Dict
from controles import favoritos_controler
from controles import jogo_controler
from utils.codigos import OK, NAO_ENCONTRADO, CONFLITO, DADOS_INVALIDOS

def _input_strip(prompt: str) -> str:
    """
    Objetivo:
    - Ler entrada do usuário e retornar a string já .strip().

    Parâmetros:
    - prompt (str): texto exibido na solicitação.

    Retorno:
    - str: entrada do usuário sem espaços nas extremidades.
    """
    return input(prompt).strip()

def exibir_menu_favoritos(perfil: Optional[Dict]):
    """
    Objetivo:
    - Exibir o menu de favoritos e tratar ações do usuário para o perfil ativo.

    Descrição:
    - Opções suportadas:
      1) Listar favoritos
      2) Adicionar favorito por ID de jogo
      3) Desfavoritar jogo
      0) Voltar
    - Para cada ação, valida parâmetros (IDs) e mostra mensagens conforme código retornado.

    Parâmetros:
    - perfil (Optional[Dict]): dicionário do perfil ativo (deve conter 'id'). Se None,
      a função informa que não há perfil ativo e retorna.

    Assertivas:
    - Pré: se `perfil` é fornecido, contém chave 'id'.
    - Pós: operações delegadas aos controllers; persistência tratada pelos controllers/TADs.

    Retorno:
    - None (efeito colateral: interação com o usuário e alterações no estado via controllers).
    """
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