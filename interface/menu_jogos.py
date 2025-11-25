# interface/menu_jogos.py
from controles import jogo_controler as jogo_controller
from controles import perfil_controler
from controles import avaliacao_controler as avaliacao_controller
from controles import biblioteca_controler # Adicionado para gerenciar status
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO

def _buscar_avaliacao_especifica(id_perfil, id_jogo):
    """Helper para encontrar uma avaliação na lista global."""
    _, todas = avaliacao_controller.Listar_avaliacao()
    return next((a for a in todas if a.get("id_perfil") == id_perfil and a.get("id_jogo") == id_jogo), None)

def _coletar_media_e_opinioes(id_jogo, perfil_atual=None):
    """
    Retorna (media, lista_opinioes) buscando na lista GLOBAL de avaliações.
    """
    # FIX: Busca na lista global, não dentro dos perfis
    _, todas_avaliacoes = avaliacao_controller.Listar_avaliacao()
    
    avals_deste_jogo = [a for a in todas_avaliacoes if a.get("id_jogo") == id_jogo]
    
    if not avals_deste_jogo:
        return 0.0, []

    soma_notas = sum(float(a.get("score", 0)) for a in avals_deste_jogo)
    quantidade = len(avals_deste_jogo)
    
    lista_opinioes = []
    for aval in avals_deste_jogo:
        # Busca nome do autor
        _, autor = perfil_controler.Busca_Perfil(aval["id_perfil"])
        nome_autor = autor["nome"] if autor else "(desconhecido)"
        
        lista_opinioes.append({
            "perfil": nome_autor,
            "nota": aval.get("score"),
            "opiniao": aval.get("descricao", "")
        })

    media = round(soma_notas / quantidade, 2)
    return media, lista_opinioes

def _normalize(s: str) -> str:
    return ' '.join(''.join(ch for ch in s.lower() if ch.isalnum() or ch.isspace()).split())

def _is_subsequence(query: str, text: str) -> bool:
    it = iter(text)
    return all(ch in it for ch in query)

def _smart_search_matches(lista_jogos, termo):
    q = _normalize(termo)
    if not q: return []
    results = []
    for j in lista_jogos:
        title = j.get("titulo", "")
        norm = _normalize(title)
        score = 0
        if q in norm: score += 100
        initials = ''.join(w[0] for w in norm.split() if w)
        if q in initials: score += 90
        for w in norm.split():
            if w.startswith(q):
                score += 70
                break
        if _is_subsequence(q.replace(' ', ''), norm.replace(' ', '')): score += 50
        if len(q) <= 2 and norm.startswith(q): score += 20
        if score > 0: results.append((score, j))
    results.sort(key=lambda x: (-x[0], x[1].get("titulo", "")))
    return [r[1] for r in results]

def exibir_menu(perfil):
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
    print("\n--- Cadastrar Jogo ---")
    titulo = input("Título: ").strip()
    genero = input("Gênero: ").strip()
    descricao = input("Descrição (opcional): ").strip()
    
    # Nota inicial é ignorada pelo controller, mas mantemos o input
    input("Nota geral inicial (Será calculada automaticamente): ") 
    
    # Passamos None na nota pois o controller define como 0.0
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
    try:
        id_up = int(input("ID do jogo a atualizar: ").strip())
    except ValueError:
        print("⚠️  ID inválido.")
        return
    titulo = input("Novo título: ").strip()
    genero = input("Novo gênero: ").strip()
    descricao = input("Nova descrição (opcional): ").strip()
    
    # Controller ignora nota na atualização
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
    codigo, lista = jogo_controller.Listar_Jogo()
    if codigo == OK:
        print("\n📋 Catálogo de Jogos:")
        if not lista:
            print("  Nenhum jogo disponível.")
            return
        for j in lista:
            genero = j.get('genero', '-')
            # Usa o campo nota_geral direto do jogo (que é atualizado automaticamente)
            media = j.get("nota_geral", 0.0)
            
            linha = f"  {j['id']} - {j['titulo']} ({genero}) - Nota geral: {media}"
            print(linha)
            
            if perfil:
                # FIX: Busca avaliação na lista global
                aval = _buscar_avaliacao_especifica(perfil["id"], j["id"])
                if aval:
                    print(f"     → Sua nota: {aval.get('score')} | Sua opinião: {aval.get('descricao','(sem opinião)')}")
    else:
        print("❌ Erro ao listar jogos.")

def avaliar_jogo(perfil):
    codigo, lista = jogo_controller.Listar_Jogo()
    if codigo != OK or not lista:
        print("❌ Não há jogos disponíveis.")
        return

    # ... (Lógica de seleção do jogo mantida igual) ...
    escolha = input("ID do jogo ou nome para buscar: ").strip()
    jogo_selecionado = None
    
    if escolha.isdigit():
        target_id = int(escolha)
        jogo_selecionado = next((j for j in lista if j["id"] == target_id), None)
    else:
        matches = [j for j in lista if escolha.lower() in j.get("titulo","").lower()]
        if matches:
            jogo_selecionado = matches[0] # Simplificado para o exemplo

    if not jogo_selecionado:
        print("❌ Jogo não encontrado.")
        return

    try:
        nota = float(input(f"Sua nota para '{jogo_selecionado['titulo']}' (0-10): ").replace(',', '.'))
    except ValueError:
        print("⚠️  Nota inválida.")
        return

    opiniao = input("Escreva sua opinião (opcional): ").strip()

    # FIX: Correção da ordem dos parâmetros: (id_jogo, score, descricao, id_perfil)
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
    Mostra a biblioteca (Status) e permite editar avaliações.
    """
    if not perfil: return
    
    # Recarrega perfil para garantir dados atualizados
    _, perfil = perfil_controler.Busca_Perfil(perfil["id"])
    bibli = perfil.get("biblioteca", [])

    if not bibli:
        print("\n📚 Sua biblioteca está vazia.")
        return

    print("\n📚 Sua biblioteca (Status & Avaliações):")
    for i, entry in enumerate(bibli, start=1):
        id_jogo = entry.get("id_jogo") # FIX: chave padronizada
        status = entry.get("status", "sem status")
        
        _, jogo = jogo_controller.Busca_Jogo(id_jogo)
        titulo = jogo.get("titulo") if jogo else "Jogo Removido"
        
        # Busca avaliação correspondente
        aval = _buscar_avaliacao_especifica(perfil["id"], id_jogo)
        nota_str = f"Nota: {aval['score']}" if aval else "Não avaliado"
        
        print(f"  {i}. {titulo} | Status: [{status.upper()}] | {nota_str}")

    escolha = input("\nEscolha o número do item para gerenciar: ").strip()
    if not escolha or not escolha.isdigit(): return
    idx = int(escolha) - 1
    if idx < 0 or idx >= len(bibli): return

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
        if cod == OK: print("✅ Status atualizado.")
        else: print("❌ Erro/Status inválido.")

    elif acao == "2":
        aval = _buscar_avaliacao_especifica(perfil["id"], id_jogo)
        try:
            nota = float(input("Nota (0-10): "))
        except: return
        opiniao = input("Opinião: ")
        
        if aval:
            # Editar
            cod, _ = avaliacao_controller.Editar_avaliacao(aval["id"], nota, opiniao)
        else:
            # Criar nova via controller de avaliação (ordem correta)
            cod, _ = avaliacao_controller.Avaliar_jogo(id_jogo, nota, opiniao, perfil["id"])
        
        if cod == OK: print("✅ Avaliação salva.")
        else: print("❌ Erro ao salvar.")

    elif acao == "3":
        # Usa o wrapper do perfil que busca o ID correto
        cod, _ = perfil_controler.Remover_Avaliacao(perfil["id"], id_jogo)
        if cod == OK: print("✅ Avaliação removida.")
        elif cod == NAO_ENCONTRADO: print("❌ Você não tem avaliação neste jogo.")
    
    elif acao == "4":
        cod, _ = biblioteca_controler.Remover_Jogo(perfil["id"], id_jogo)
        if cod == OK: print("✅ Jogo removido da biblioteca.")