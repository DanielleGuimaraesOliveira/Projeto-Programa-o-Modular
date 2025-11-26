"""
Menu de Jogos (interface CLI).

Objetivo:
- Fornecer interações em linha de comando para gerenciar o catálogo de jogos:
  listar, cadastrar, atualizar, remover, avaliar e navegar pela biblioteca do usuário.

Descrição:
- Valida entradas do usuário, chama os controllers apropriados (jogo, perfil, avaliação, biblioteca)
  e traduz os códigos de retorno em mensagens legíveis.
- Contém helpers para busca e coleta de médias/opiniões de avaliações.
- Não realiza persistência direta; delega operações aos controllers/TADs.
"""
from controles import jogo_controler as jogo_controller
from controles import perfil_controler
from controles import avaliacao_controler as avaliacao_controller
from controles import biblioteca_controler  # Adicionado para gerenciar status
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO

def _buscar_avaliacao_especifica(id_perfil, id_jogo):
    """
    Objetivo:
    - Encontrar a avaliação feita por um perfil para um jogo específico.

    Descrição:
    - Obtém todas as avaliações via avaliacao_controller.Listar_avaliacao()
      e retorna a avaliação cujo par (id_perfil, id_jogo) coincida.

    Parâmetros:
    - id_perfil: int - id do perfil autor.
    - id_jogo: int - id do jogo avaliado.

    Retorno:
    - dicionário da avaliação ou None se não encontrado.
    """
    _, todas = avaliacao_controller.Listar_avaliacao()
    return next((a for a in todas if a.get("id_perfil") == id_perfil and a.get("id_jogo") == id_jogo), None)

def _coletar_media_e_opinioes(id_jogo, perfil_atual=None):
    """
    Objetivo:
    - Coletar a média de notas e as opiniões para um jogo.

    Descrição:
    - Busca todas as avaliações do jogo na lista global (Listar_avaliacao) e calcula média.
    - Monta uma lista de opiniões com o nome do autor, nota e texto.

    Parâmetros:
    - id_jogo: int - identificador do jogo.
    - perfil_atual: opcional - perfil atual (não usado diretamente aqui, mantido por compatibilidade).

    Retorno:
    - (media: float, lista_opinioes: list[dict])
      media é 0.0 quando não há avaliações; lista_opinioes contém dicionários com keys:
      "perfil", "nota", "opiniao".
    """
    # FIX: Busca na lista global, não dentro dos perfis
    _, todas_avaliacoes = avaliacao_controller.Listar_avaliacao()
    avals_deste_jogo = [a for a in todas_avaliacoes if a.get("id_jogo") == id_jogo]

    if not avals_deste_jogo:
        return 0.0, []

    # nota usa chave "nota" ou compatibiliza com "score"
    soma_notas = sum(float(a.get("nota", a.get("score", 0))) for a in avals_deste_jogo)
    quantidade = len(avals_deste_jogo)

    lista_opinioes = []
    for aval in avals_deste_jogo:
        _, autor = perfil_controler.Busca_Perfil(aval["id_perfil"])
        nome_autor = autor["nome"] if autor else "(desconhecido)"
        nota = aval.get("nota", aval.get("score"))
        opiniao = aval.get("opiniao", aval.get("descricao", ""))
        lista_opinioes.append({
            "perfil": nome_autor,
            "nota": nota,
            "opiniao": opiniao
        })

    media = round(soma_notas / quantidade, 2)
    return media, lista_opinioes

def _normalize(s: str) -> str:
    """
    Objetivo:
    - Normalizar texto para buscas (minúsculas, apenas alfanuméricos e espaços, sem múltiplos espaços).
    """
    return ' '.join(''.join(ch for ch in s.lower() if ch.isalnum() or ch.isspace()).split())

def _is_subsequence(query: str, text: str) -> bool:
    """
    Objetivo:
    - Checar se `query` é subsequência de `text`.
    """
    it = iter(text)
    return all(ch in it for ch in query)

def _smart_search_matches(lista_jogos, termo):
    """
    Objetivo:
    - Retornar uma lista ordenada de jogos que combinam com `termo` usando heurísticas simples.

    Descrição:
    - Pontua correspondências por presença direta, iniciais, prefixos e subsequência.
    - Retorna apenas os dicionários dos jogos ordenados por score descendente.
    """
    q = _normalize(termo)
    if not q:
        return []
    results = []
    for j in lista_jogos:
        title = j.get("titulo", "")
        norm = _normalize(title)
        score = 0
        if q in norm:
            score += 100
        initials = ''.join(w[0] for w in norm.split() if w)
        if q in initials:
            score += 90
        for w in norm.split():
            if w.startswith(q):
                score += 70
                break
        if _is_subsequence(q.replace(' ', ''), norm.replace(' ', '')):
            score += 50
        if len(q) <= 2 and norm.startswith(q):
            score += 20
        if score > 0:
            results.append((score, j))
    results.sort(key=lambda x: (-x[0], x[1].get("titulo", "")))
    return [r[1] for r in results]

def exibir_menu(perfil):
    """
    Objetivo:
    - Exibir o menu principal do catálogo e encaminhar escolhas do usuário.

    Descrição:
    - Opções: listar, cadastrar, atualizar, remover, avaliar, acessar biblioteca pessoal.
    - Valida entradas e chama funções auxiliares apropriadas.

    Parâmetros:
    - perfil: dicionário do perfil ativo (ou None).
    """
    while True:
        print("\n=== CATÁLOGO DE JOGOS ===")
        print("1. Listar catálogo")
        print("2. Cadastrar jogo")
        print("3. Atualizar jogo")
        print("4. Remover jogo")
        print("5. Avaliar jogo")
        print("6. Minha biblioteca (Status)")
        print("0. Voltar")
        opcao = input("Escolha: ")

        if opcao == "1":
            listar_jogos(perfil)
        elif opcao == "2":
            cadastrar_jogo()
        elif opcao == "3":
            atualizar_jogo()
        elif opcao == "4":
            remover_jogo()
        elif opcao == "5":
            avaliar_jogo(perfil)
        elif opcao == "6":
            mostrar_biblioteca(perfil)
        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida.")

def cadastrar_jogo():
    """
    Objetivo:
    - Ler dados do usuário e cadastrar um novo jogo via jogo_controller.Cadastrar_Jogo.

    Descrição:
    - Solicita título, gênero, descrição e nota inicial (nota é ignorada pelo controller).
    - Mostra mensagens conforme código de retorno.
    """
    print("\n--- Cadastrar Jogo ---")
    titulo = input("Título: ").strip()
    genero = input("Gênero: ").strip()
    descricao = input("Descrição (opcional): ").strip()
    input("Nota geral inicial (Será calculada automaticamente): ")  # mantido para UX
    codigo, jogo = jogo_controller.Cadastrar_Jogo(titulo, descricao, genero, None)
    if codigo == OK:
        print(f"✅ Jogo cadastrado: {jogo['titulo']} (id={jogo['id']})")
    elif codigo == DADOS_INVALIDOS:
        print("❌ Dados inválidos.")
    elif codigo == CONFLITO:
        print("❌ Jogo já existe.")
    else:
        print("❌ Erro ao cadastrar.")

def atualizar_jogo():
    """
    Objetivo:
    - Atualizar os campos editáveis de um jogo existente.

    Descrição:
    - Lê id e novos campos, chama jogo_controller.Atualizar_Jogo e exibe resultado.
    """
    try:
        id_up = int(input("ID do jogo a atualizar: ").strip())
    except ValueError:
        print("⚠️  ID inválido.")
        return
    titulo = input("Novo título: ").strip()
    genero = input("Novo gênero: ").strip()
    descricao = input("Nova descrição (opcional): ").strip()
    codigo, jogo = jogo_controller.Atualizar_Jogo(id_up, titulo, descricao, genero, None)
    if codigo == OK:
        print("✅ Jogo atualizado.")
    elif codigo == DADOS_INVALIDOS:
        print("❌ Dados inválidos.")
    elif codigo == NAO_ENCONTRADO:
        print("❌ Jogo não encontrado.")
    elif codigo == CONFLITO:
        print("❌ Conflito de título.")
    else:
        print("❌ Erro ao atualizar.")

def remover_jogo():
    """
    Objetivo:
    - Remover um jogo do catálogo.

    Descrição:
    - Lê o id do jogo e chama jogo_controller.Remover_Jogo; trata retorno.
    """
    try:
        id_rm = int(input("ID do jogo a remover: ").strip())
    except ValueError:
        print("⚠️  ID inválido.")
        return
    codigo, _ = jogo_controller.Remover_Jogo(id_rm)
    if codigo == OK:
        print("✅ Jogo removido.")
    elif codigo == NAO_ENCONTRADO:
        print("❌ Jogo não encontrado.")
    else:
        print("❌ Erro ao remover.")

def listar_jogos(perfil):
    """
    Objetivo:
    - Listar todos os jogos do catálogo com suas notas gerais.

    Descrição:
    - Busca a lista via jogo_controller.Listar_Jogo e exibe cada jogo.
    - Se houver perfil ativo, mostra também a avaliação do usuário para cada jogo (se existir).
    """
    codigo, lista = jogo_controller.Listar_Jogo()
    if codigo == OK:
        print("\n📋 Catálogo de Jogos:")
        if not lista:
            print("  Nenhum jogo disponível.")
            return
        for j in lista:
            genero = j.get('genero', '-')
            media = j.get("nota_geral", 0.0)
            linha = f"  {j['id']} - {j['titulo']} ({genero}) - Nota geral: {media}"
            print(linha)
            if perfil:
                aval = _buscar_avaliacao_especifica(perfil["id"], j["id"])
                if aval:
                    nota = aval.get("nota", aval.get("score"))
                    opin = aval.get("opiniao", aval.get("descricao", "(sem opinião)"))
                    print(f"     → Sua nota: {nota} | Sua opinião: {opin}")
    else:
        print("❌ Erro ao listar jogos.")

def avaliar_jogo(perfil):
    """
    Objetivo:
    - Permitir que o perfil avalie um jogo do catálogo.

    Descrição:
    - Permite pesquisar por id ou nome simplificado, ler nota/opinião e chamar avaliacao_controller.Avaliar_jogo.
    - Valida entrada e mostra mensagens conforme retorno.
    """
    codigo, lista = jogo_controller.Listar_Jogo()
    if codigo != OK or not lista:
        print("❌ Não há jogos disponíveis.")
        return

    escolha = input("ID do jogo ou nome para buscar: ").strip()
    jogo_selecionado = None
    if escolha.isdigit():
        target_id = int(escolha)
        jogo_selecionado = next((j for j in lista if j["id"] == target_id), None)
    else:
        matches = [j for j in lista if escolha.lower() in j.get("titulo","").lower()]
        if matches:
            jogo_selecionado = matches[0]

    if not jogo_selecionado:
        print("❌ Jogo não encontrado.")
        return

    try:
        nota = float(input(f"Sua nota para '{jogo_selecionado['titulo']}' (0-10): ").replace(',', '.'))
    except ValueError:
        print("⚠️  Nota inválida.")
        return

    opiniao = input("Escreva sua opinião (opcional): ").strip()
    codigo, _ = avaliacao_controller.Avaliar_jogo(jogo_selecionado['id'], nota, opiniao, perfil['id'])
    if codigo == OK:
        print(f"✅ Avaliação registrada!")
    elif codigo == CONFLITO:
        print("❌ Você já avaliou este jogo. Use a biblioteca para editar.")
    elif codigo == DADOS_INVALIDOS:
        print("❌ Nota inválida (0-10).")
    else:
        print("❌ Erro ao registrar.")

def mostrar_biblioteca(perfil):
    """
    Objetivo:
    - Exibir e permitir gerenciar a biblioteca (status e avaliações) do perfil ativo.

    Descrição:
    - Atualiza o perfil via perfil_controler.Busca_Perfil para garantir dados recentes.
    - Mostra cada item com título, status e possível avaliação do usuário.
    - Permite ações: mudar status, editar/criar avaliação, remover avaliação, remover da biblioteca.
    """
    if not perfil:
        return

    _, perfil = perfil_controler.Busca_Perfil(perfil["id"])
    bibli = perfil.get("biblioteca", [])
    if not bibli:
        print("\n📚 Sua biblioteca está vazia.")
        return

    print("\n📚 Sua biblioteca (Status & Avaliações):")
    for i, entry in enumerate(bibli, start=1):
        id_jogo = entry.get("id_jogo")
        status = entry.get("status", "sem status")
        _, jogo = jogo_controller.Busca_Jogo(id_jogo)
        titulo = jogo.get("titulo") if jogo else "Jogo Removido"
        aval = _buscar_avaliacao_especifica(perfil["id"], id_jogo)
        nota_str = f"Nota: {aval.get('nota', aval.get('score'))}" if aval else "Não avaliado"
        print(f"  {i}. {titulo} | Status: [{status.upper()}] | {nota_str}")

    escolha = input("\nEscolha o número do item para gerenciar: ").strip()
    if not escolha or not escolha.isdigit():
        return
    idx = int(escolha) - 1
    if idx < 0 or idx >= len(bibli):
        return

    item_biblioteca = bibli[idx]
    id_jogo = item_biblioteca.get("id_jogo")
    print(f"\nGerenciando jogo ID {id_jogo}:")
    print("1. Mudar Status (Jogando/Jogado/Platinado)")
    print("2. Editar/Criar Avaliação")
    print("3. Remover Avaliação")
    print("4. Remover da Biblioteca")
    acao = input("Escolha: ").strip()

    if acao == "1":
        novo_status = input("Novo status (jogando, jogado, platinado): ").lower()
        cod, _ = biblioteca_controler.Atualizar_Status_Jogo(perfil["id"], id_jogo, novo_status)
        if cod == OK:
            print("✅ Status atualizado.")
        else:
            print("❌ Erro/Status inválido.")

    elif acao == "2":
        aval = _buscar_avaliacao_especifica(perfil["id"], id_jogo)
        try:
            nota = float(input("Nota (0-10): ").replace(',', '.'))
        except ValueError:
            print("⚠️  Nota inválida.")
            return
        opiniao = input("Opinião: ").strip()
        if aval:
            cod, _ = avaliacao_controller.Editar_avaliacao(aval["id"], nota, opiniao)
        else:
            cod, _ = avaliacao_controller.Avaliar_jogo(id_jogo, nota, opiniao, perfil["id"])
        if cod == OK:
            print("✅ Avaliação salva.")
        else:
            print("❌ Erro ao salvar.")

    elif acao == "3":
        cod, _ = perfil_controler.Remover_Avaliacao(perfil["id"], id_jogo)
        if cod == OK:
            print("✅ Avaliação removida.")
        elif cod == NAO_ENCONTRADO:
            print("❌ Você não tem avaliação neste jogo.")

    elif acao == "4":
        cod, _ = biblioteca_controler.Remover_Jogo(perfil["id"], id_jogo)
        if cod == OK:
            print("✅ Jogo removido da biblioteca.")