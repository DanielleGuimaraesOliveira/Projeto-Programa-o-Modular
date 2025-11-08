# controllers/perfil_controller.py
from dados.database import perfis, salvar_perfis, jogos, salvar_jogos
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO

def Criar_Perfil(nome, descricao=None, avatar=None):
    """
    Cria um novo perfil se o nome for válido e não duplicado.
    """
    if not nome or nome.strip() == "":
        return DADOS_INVALIDOS, None

    if any(p["nome"].lower() == nome.lower() for p in perfis):
        return CONFLITO, None

    novo_id = max([p["id"] for p in perfis]) + 1 if perfis else 1
    novo_perfil = {
        "id": novo_id,
        "nome": nome,
        "descricao": descricao or "",
        "avatar": avatar or "",
        "favoritos": [],
        "biblioteca": []   # campo para armazenar {jogo_id, nota, opiniao}
    }
    perfis.append(novo_perfil)
    # salva em arquivo para persistir entre execuções
    salvar_perfis()
    return OK, novo_perfil


def Listar_Perfil():
    """
    Retorna todos os perfis cadastrados.
    """
    return OK, perfis


def Busca_Perfil(id_perfil):
    """
    Busca um perfil pelo ID.
    """
    perfil = next((p for p in perfis if p["id"] == id_perfil), None)
    if not perfil:
        return NAO_ENCONTRADO, None
    return OK, perfil


def Busca_Perfil_por_nome(nome):
    """
    Busca um perfil pelo nome (case-insensitive).
    """
    if not nome or nome.strip() == "":
        return NAO_ENCONTRADO, None
    perfil = next((p for p in perfis if p["nome"].lower() == nome.strip().lower()), None)
    if not perfil:
        return NAO_ENCONTRADO, None
    return OK, perfil


def Atualizar_Perfil(id_perfil, nome=None, descricao=None, avatar=None):
    """
    Atualiza os campos fornecidos do perfil e salva as mudanças em disco.
    - nome: se fornecido, valida não vazio e sem conflito com outro perfil.
    - descricao, avatar: valores podem ser string vazia para limpar.
    """
    perfil = next((p for p in perfis if p["id"] == id_perfil), None)
    if not perfil:
        return NAO_ENCONTRADO, None

    if nome is not None:
        if nome.strip() == "":
            return DADOS_INVALIDOS, None
        if any(p["nome"].lower() == nome.lower() and p["id"] != id_perfil for p in perfis):
            return CONFLITO, None
        perfil["nome"] = nome

    if descricao is not None:
        perfil["descricao"] = descricao

    if avatar is not None:
        perfil["avatar"] = avatar

    # persiste alterações
    salvar_perfis()
    return OK, perfil


def Remover_Perfil(id_perfil):
    """
    Remove um perfil e salva as alterações.
    """
    global perfis
    perfil = next((p for p in perfis if p["id"] == id_perfil), None)
    if not perfil:
        return NAO_ENCONTRADO, None
    perfis.remove(perfil)
    salvar_perfis()
    return OK, None


def _recalcular_nota_geral(id_jogo):
    """
    Recalcula a nota média (nota_geral) do jogo a partir de todas as avaliações
    presentes em todos os perfis e persiste em dados/jogos.json.
    """
    total = 0.0
    count = 0
    for p in perfis:
        for e in p.get("biblioteca", []):
            if e.get("jogo_id") == id_jogo:
                try:
                    total += float(e.get("nota", 0))
                    count += 1
                except Exception:
                    continue
    media = round(total / count, 2) if count > 0 else 0.0
    jogo = next((j for j in jogos if j["id"] == id_jogo), None)
    if jogo is not None:
        jogo["nota_geral"] = media
        salvar_jogos()
    return media


def Adicionar_Avaliacao(id_perfil, id_jogo, nota, opiniao=None):
    """
    Adiciona ou atualiza uma avaliação (nota + opiniao) de um jogo no perfil.
    nota: float entre 0 e 10
    Atualiza também a nota_geral do jogo.
    """
    perfil = next((p for p in perfis if p["id"] == id_perfil), None)
    if not perfil:
        return NAO_ENCONTRADO, None

    jogo = next((j for j in jogos if j["id"] == id_jogo), None)
    if not jogo:
        return NAO_ENCONTRADO, None

    try:
        nota = float(nota)
    except Exception:
        return DADOS_INVALIDOS, None

    if nota < 0 or nota > 10:
        return DADOS_INVALIDOS, None

    if "biblioteca" not in perfil:
        perfil["biblioteca"] = []

    entry = next((e for e in perfil["biblioteca"] if e["jogo_id"] == id_jogo), None)
    if entry:
        entry["nota"] = nota
        entry["opiniao"] = opiniao or ""
    else:
        novo = {"jogo_id": id_jogo, "nota": nota, "opiniao": opiniao or ""}
        perfil["biblioteca"].append(novo)
        entry = novo

    salvar_perfis()
    # recalcula média global do jogo e persiste
    _recalcular_nota_geral(id_jogo)
    return OK, entry


def Remover_Avaliacao(id_perfil, id_jogo):
    """
    Remove a avaliação de um jogo da biblioteca do perfil.
    Retorna OK, None em sucesso ou NAO_ENCONTRADO se perfil/jogo/entrada não existir.
    Após remoção recalcula nota_geral do jogo.
    """
    perfil = next((p for p in perfis if p["id"] == id_perfil), None)
    if not perfil:
        return NAO_ENCONTRADO, None

    if "biblioteca" not in perfil or not perfil["biblioteca"]:
        return NAO_ENCONTRADO, None

    entry = next((e for e in perfil["biblioteca"] if e.get("jogo_id") == id_jogo), None)
    if not entry:
        return NAO_ENCONTRADO, None

    perfil["biblioteca"].remove(entry)
    salvar_perfis()
    # recalcula média global do jogo e persiste
    _recalcular_nota_geral(id_jogo)
    return OK, None
