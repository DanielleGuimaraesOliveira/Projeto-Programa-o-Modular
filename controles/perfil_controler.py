# controllers/perfil_controller.py
from dados.database import perfis, salvar_perfis
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
