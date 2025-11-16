# interface/menu_jogos.py
from controles import jogo_controler as jogo_controller
from controles import perfil_controler
from controles import avaliacao_controler as avaliacao_controller
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO

def _coletar_media_e_opinioes(id_jogo, perfil_atual=None):
    """
    Retorna (media, lista_opinioes) calculadas a partir de todos os perfis.
    lista_opinioes: [{'perfil': nome, 'nota': x, 'opiniao': s}, ...]
    """
    status, todos_perfis = perfil_controler.Listar_Perfil()
    if status != OK:
        return 0.0, []

    soma_notas = 0.0
    quantidade_avaliacoes = 0
    lista_opinioes = []
    for perfil in todos_perfis:
        for entrada in perfil.get("biblioteca", []):
            if entrada.get("jogo_id") == id_jogo:
                try:
                    nota_valor = float(entrada.get("nota", 0))
                except Exception:
                    continue
                soma_notas += nota_valor
                quantidade_avaliacoes += 1
                lista_opinioes.append({
                    "perfil": perfil.get("nome", "(sem nome)"),
                    "nota": nota_valor,
                    "opiniao": entrada.get("opiniao", "")
                })
    media = round(soma_notas / quantidade_avaliacoes, 2) if quantidade_avaliacoes > 0 else 0.0
    return media, lista_opinioes

def _normalize(s: str) -> str:
    return ' '.join(''.join(ch for ch in s.lower() if ch.isalnum() or ch.isspace()).split())

def _is_subsequence(query: str, text: str) -> bool:
    it = iter(text)
    return all(ch in it for ch in query)

def _smart_search_matches(lista_jogos, termo):
    """
    Retorna lista de jogos ordenada por relevância usando heurísticas:
    - match exato/substring (alto)
    - match nas iniciais das palavras (alto)
    - prefixo de alguma palavra (médio)
    - subsequence das letras (baixo) -> ajuda com 'gd' -> 'god'
    """
    q = _normalize(termo)
    if not q:
        return []

    results = []
    for j in lista_jogos:
        title = j.get("titulo", "")
        norm = _normalize(title)

        score = 0
        # substring exata
        if q in norm:
            score += 100
        # iniciais das palavras
        initials = ''.join(w[0] for w in norm.split() if w)
        if q in initials:
            score += 90
        # prefixo de alguma palavra
        for w in norm.split():
            if w.startswith(q):
                score += 70
                break
        # subsequence (letras em ordem, não necessariamente contíguas)
        if _is_subsequence(q.replace(' ', ''), norm.replace(' ', '')):
            score += 50
        # pequenos bônus para termos curtos que aparecem como prefixo no título
        if len(q) <= 2 and norm.startswith(q):
            score += 20

        if score > 0:
            results.append((score, j))

    # ordenar por score desc, depois título asc
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
        print("6. Minha biblioteca")
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
    nota_input = input("Nota geral inicial (0-10, opcional, ENTER para 0): ").strip()
    nota = 0.0
    if nota_input:
        try:
            nota = float(nota_input.replace(',', '.'))
        except ValueError:
            print("⚠️  Nota inválida. Use número entre 0 e 10.")
            return
    codigo, jogo = jogo_controller.Cadastrar_Jogo(titulo, descricao, genero, nota)
    if codigo == OK:
        print(f"✅ Jogo cadastrado: {jogo['titulo']} (id={jogo['id']})")
    elif codigo == DADOS_INVALIDOS:
        print("❌ Dados inválidos.")
    elif codigo == CONFLITO:
        print("❌ Jogo já existe.")
    else:
        print("❌ Erro ao cadastrar.")

def buscar_jogo_por_id():
    try:
        id_busca = int(input("ID do jogo: ").strip())
    except ValueError:
        print("⚠️  ID inválido.")
        return
    codigo, jogo = jogo_controller.Busca_Jogo(id_busca)
    if codigo == OK and jogo:
        print(f"✅ Encontrado: {jogo['id']} - {jogo['titulo']} ({jogo.get('genero','-')})")
        print(f"Descrição: {jogo.get('descricao','(sem descrição)')}")
        print(f"Nota geral: {jogo.get('nota_geral', 0.0)}")
    else:
        print("❌ Jogo não encontrado.")

def atualizar_jogo():
    try:
        id_up = int(input("ID do jogo a atualizar: ").strip())
    except ValueError:
        print("⚠️  ID inválido.")
        return
    titulo = input("Novo título: ").strip()
    genero = input("Novo gênero: ").strip()
    descricao = input("Nova descrição (opcional): ").strip()
    nota_input = input("Nova nota geral (0-10): ").strip()
    try:
        nota = float(nota_input.replace(',', '.'))
    except ValueError:
        print("⚠️  Nota inválida.")
        return
    codigo, jogo = jogo_controller.Atualizar_Jogo(id_up, titulo, descricao, genero, nota)
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
            # calcula media em tempo de exibição
            media, _ = _coletar_media_e_opinioes(j.get("id"))
            linha = f"  {j['id']} - {j['titulo']} ({genero}) - Nota geral: {media}"
            print(linha)
            if perfil:
                bibli = perfil.get("biblioteca", [])
                aval = next((e for e in bibli if e.get("jogo_id") == j["id"]), None)
                if aval:
                    print(f"     → Sua nota: {aval.get('nota')} | Sua opinião: {aval.get('opiniao','(sem opinião)')}")
    else:
        print("❌ Erro ao listar jogos.")

def buscar_jogo_por_nome(perfil):
    termo = input("Digite parte do nome do jogo para buscar: ").strip()
    if not termo:
        print("⚠️  Termo vazio.")
        return
    codigo, lista = jogo_controller.Listar_Jogo()
    if codigo != OK:
        print("❌ Erro ao acessar catálogo.")
        return

    matches = _smart_search_matches(lista, termo)
    if not matches:
        print("🔎 Nenhum jogo encontrado com esse termo.")
        return

    print(f"\n🔎 Jogos encontrados ({len(matches)}):")
    for i, j in enumerate(matches, start=1):
        print(f"  {i}. {j['titulo']} ({j.get('genero','-')})")

    try:
        sub = input("Escolha o número do resultado para ver mais detalhes ou ENTER para voltar: ").strip()
        if not sub:
            return
        sub_idx = int(sub)
        if sub_idx < 1 or sub_idx > len(matches):
            print("⚠️  Número fora do intervalo.")
            return
    except ValueError:
        print("⚠️  Entrada inválida.")
        return

    jogo = matches[sub_idx - 1]
    titulo = jogo.get('titulo','(sem título)')
    genero = jogo.get('genero','-')
    descricao = jogo.get('descricao','(sem descrição)')
    media, opinioes = _coletar_media_e_opinioes(jogo.get("id"), perfil)
    print(f"\n🎯 {titulo} - {genero}")
    print(f"Descrição: {descricao}")
    print(f"Nota geral: {media}")

    outras = [o for o in opinioes if not (perfil and o["perfil"] == perfil.get("nome"))]
    if outras:
        print("\n🗣️ Opiniões de outros usuários:")
        for o in outras:
            opin = o["opiniao"] if o["opiniao"] else "(sem opinião)"
            print(f"  - {o['perfil']}: Nota {o['nota']} | {opin}")
    else:
        print("\n🗣️ Nenhuma opinião de outros usuários para este jogo ainda.")
    if perfil:
        entry = next((e for e in perfil.get("biblioteca", []) if e.get("jogo_id") == jogo.get("id")), None)
        if entry:
            print(f"\n✅ Sua avaliação: Nota {entry.get('nota')} | {entry.get('opiniao','(sem opinião)')}")

def avaliar_jogo(perfil):
    codigo, lista = jogo_controller.Listar_Jogo()
    if codigo != OK or not lista:
        print("❌ Não há jogos disponíveis para avaliar.")
        return

    print("\n📋 Catálogo de jogos:")
    for i, j in enumerate(lista, start=1):
        print(f"  {i}. {j['titulo']} ({j.get('genero','-')})")

    escolha = input("Escolha o número do jogo que deseja avaliar (ou digite parte do nome para buscar): ").strip()
    if not escolha:
        print("⚠️  Escolha vazia.")
        return

    jogo_selecionado = None
    if escolha.isdigit():
        idx = int(escolha)
        if idx < 1 or idx > len(lista):
            print("⚠️  Número fora do intervalo.")
            return
        jogo_selecionado = lista[idx - 1]
    else:
        termo = escolha
        matches = [j for j in lista if termo.lower() in j.get("titulo","").lower()]
        if not matches:
            print("🔎 Nenhum jogo encontrado com esse termo.")
            return
        if len(matches) == 1:
            jogo_selecionado = matches[0]
        else:
            print(f"\n🔎 {len(matches)} resultados encontrados:")
            for i, j in enumerate(matches, start=1):
                print(f"  {i}. {j['titulo']} ({j.get('genero','-')})")
            try:
                sub = input("Escolha o número do resultado desejado ou ENTER para cancelar: ").strip()
                if not sub:
                    return
                sub_idx = int(sub)
                if sub_idx < 1 or sub_idx > len(matches):
                    print("⚠️  Número fora do intervalo.")
                    return
                jogo_selecionado = matches[sub_idx - 1]
            except ValueError:
                print("⚠️  Entrada inválida.")
                return

    try:
        nota = float(input("Sua nota (0-10): ").replace(',', '.'))
    except ValueError:
        print("⚠️  Nota inválida.")
        return

    opiniao = input("Escreva sua opinião (opcional): ").strip()

    # usa o módulo de avaliações separado
    codigo, aval = avaliacao_controller.Avaliar_Jogo(perfil['id'], jogo_selecionado['id'], nota, opiniao)
    if codigo == OK:
        # também grava na biblioteca se quiser — manter compatibilidade
        bibli = perfil.setdefault("biblioteca", [])
        entry = next((e for e in bibli if e.get("jogo_id") == jogo_selecionado["id"]), None)
        if entry:
            entry["nota"] = nota
            entry["opiniao"] = opiniao or ""
        else:
            bibli.append({"jogo_id": jogo_selecionado["id"], "nota": nota, "opiniao": opiniao or ""})
        print(f"✅ Avaliação registrada para '{jogo_selecionado['titulo']}'!")
    elif codigo == DADOS_INVALIDOS:
        print("❌ Nota inválida (use 0-10).")
    elif codigo == NAO_ENCONTRADO:
        print("❌ Jogo ou perfil não encontrado.")
    else:
        print("❌ Erro ao registrar avaliação.")

def mostrar_biblioteca(perfil):
    if not perfil:
        print("❌ Nenhum perfil ativo.")
        return

    bibli = perfil.get("biblioteca", [])
    if not bibli:
        print("\n📚 Sua biblioteca está vazia.")
        return

    print("\n📚 Sua biblioteca:")
    for i, e in enumerate(bibli, start=1):
        codigo, jogo = jogo_controller.Busca_Jogo(e.get("jogo_id"))
        titulo = jogo.get("titulo") if codigo == OK else f"Jogo #{e.get('jogo_id')}"
        print(f"  {i}. {e.get('jogo_id')} - {titulo} | Nota: {e.get('nota')} | Opinião: {e.get('opiniao','(sem opinião)')}")

    escolha = input("\nEscolha o número do item para gerenciar ou ENTER para voltar: ").strip()
    if not escolha:
        return
    try:
        idx = int(escolha)
    except ValueError:
        print("⚠️  Escolha inválida.")
        return
    if idx < 1 or idx > len(bibli):
        print("⚠️  Número fora do intervalo.")
        return

    entry = bibli[idx - 1]
    id_jogo = entry.get("jogo_id")

    while True:
        print(f"\nGerenciando: {id_jogo} - (sua nota: {entry.get('nota')})")
        print("1. Atualizar nota/opinião")
        print("2. Remover da biblioteca")
        print("0. Voltar")
        acao = input("Escolha: ").strip()

        if acao == "1":
            try:
                nova_nota = float(input("Nova nota (0-10): ").replace(',', '.'))
            except ValueError:
                print("⚠️  Nota inválida.")
                continue
            nova_opiniao = input("Nova opinião (opcional): ").strip()
            codigo, _ = avaliacao_controller.Avaliar_Jogo(perfil['id'], id_jogo, nova_nota, nova_opiniao)
            if codigo == OK:
                print("✅ Avaliação atualizada.")
                entry["nota"] = nova_nota
                entry["opiniao"] = nova_opiniao or ""
            elif codigo == DADOS_INVALIDOS:
                print("❌ Nota inválida (use 0-10).")
            else:
                print("❌ Erro ao atualizar avaliação.")
        elif acao == "2":
            confirm = ""
            while confirm not in ["s", "n"]:
                confirm = input("Tem certeza que deseja remover este jogo da sua biblioteca? (s/n): ").strip().lower()
            if confirm == "s":
                codigo, _ = avaliacao_controller.Remover_Avaliacao(perfil['id'], id_jogo)
                if codigo == OK:
                    # também remover da lista local exibida
                    bibli.remove(entry)
                    print("✅ Jogo removido da biblioteca.")
                elif codigo == NAO_ENCONTRADO:
                    print("❌ Jogo não encontrado na biblioteca.")
                else:
                    print("❌ Erro ao remover jogo da biblioteca.")
            else:
                print("❌ Ação cancelada.")
        elif acao == "0":
            return
        else:
            print("❌ Opção inválida.")
