# interface/menu_jogos.py
from controles import jogo_controler as jogo_controller
from controles import perfil_controler
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO

def _coletar_media_e_opinioes(id_jogo, perfil_atual=None):
    """
    Retorna (media, lista_opinioes) calculadas a partir de todos os perfis.
    lista_opinioes: [{'perfil': nome, 'nota': x, 'opiniao': s}, ...]
    """
    codigo_p, todos_perfis = perfil_controler.Listar_Perfil()
    if codigo_p != OK:
        return 0.0, []

    total = 0.0
    count = 0
    opinioes = []
    for p in todos_perfis:
        for e in p.get("biblioteca", []):
            if e.get("jogo_id") == id_jogo:
                try:
                    nota = float(e.get("nota", 0))
                except Exception:
                    continue
                total += nota
                count += 1
                # incluir opinião (pode incluir a do próprio usuário também)
                opinioes.append({
                    "perfil": p.get("nome", "(sem nome)"),
                    "nota": nota,
                    "opiniao": e.get("opiniao", "")
                })
    media = round(total / count, 2) if count > 0 else 0.0
    return media, opinioes

def exibir_menu(perfil):
    while True:
        print("\n=== CATÁLOGO DE JOGOS ===")
        print("1. Listar catálogo")
        print("2. Buscar jogo por nome")
        print("3. Avaliar / Adicionar à minha biblioteca")
        print("4. Minha biblioteca")
        print("0. Voltar")
        opcao = input("Escolha: ")

        if opcao == "1":
            listar_jogos(perfil)
        elif opcao == "2":
            buscar_jogo_por_nome(perfil)
        elif opcao == "3":
            avaliar_jogo(perfil)
        elif opcao == "4":
            mostrar_biblioteca(perfil)
        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida.")

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
    matches = [j for j in lista if termo.lower() in j.get("titulo","").lower()]
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
    # mostra detalhes do jogo
    titulo = jogo.get('titulo','(sem título)')
    genero = jogo.get('genero','-')
    descricao = jogo.get('descricao','(sem descrição)')
    # calcula média e coleta opiniões de todos os perfis
    media, opinioes = _coletar_media_e_opinioes(jogo.get("id"), perfil)
    print(f"\n🎯 {titulo} - {genero}")
    print(f"Descrição: {descricao}")
    print(f"Nota geral: {media}")

    # mostrar opiniões/outros perfis (já obtidas em opinioes)
    outras = [o for o in opinioes if not (perfil and o["perfil"] == perfil.get("nome"))]
    if outras:
        print("\n🗣️ Opiniões de outros usuários:")
        for o in outras:
            opin = o["opiniao"] if o["opiniao"] else "(sem opinião)"
            print(f"  - {o['perfil']}: Nota {o['nota']} | {opin}")
    else:
        print("\n🗣️ Nenhuma opinião de outros usuários para este jogo ainda.")
    # mostrar também a opinião do próprio usuário (se houver)
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

    codigo, aval = perfil_controler.Adicionar_Avaliacao(perfil['id'], jogo_selecionado['id'], nota, opiniao)
    if codigo == OK:
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
            codigo, _ = perfil_controler.Adicionar_Avaliacao(perfil['id'], id_jogo, nova_nota, nova_opiniao)
            if codigo == OK:
                print("✅ Avaliação atualizada.")
                entry["nota"] = nova_nota
                entry["opiniao"] = nova_opiniao or ""
            elif codigo == DADOS_INVALIDOS:
                print("❌ Nota inválida (use 0-10).")
            else:
                print("❌ Erro ao atualizar avaliação.")
            return
        elif acao == "2":
            codigo, _ = perfil_controler.Remover_Avaliacao(perfil['id'], id_jogo)
            if codigo == OK:
                print("🗑️ Avaliação removida da biblioteca.")
            else:
                print("❌ Não foi possível remover a avaliação.")
            return
        elif acao == "0":
            return
        else:
            print("❌ Opção inválida.")
