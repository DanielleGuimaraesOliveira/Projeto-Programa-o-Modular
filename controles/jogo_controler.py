# controles/jogo_controler.py
"""Lógica de jogos: cadastro, listagem, busca, atualização e remoção.

Mantém as assinaturas públicas (Cadastrar_Jogo, Listar_Jogo, Busca_Jogo,
Atualizar_Jogo, Remover_Jogo) para compatibilidade com o restante do projeto.
"""
from typing import Dict, List, Optional, Tuple, Any

from dados.database import jogos, salvar_jogos
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO

__all__ = [
    "Cadastrar_Jogo", "Listar_Jogo", "Busca_Jogo", "Atualizar_Jogo", "Remover_Jogo"
]


def _proximo_id(jogos_list: List[Dict[str, Any]]) -> int:
    """Retorna próximo id seguro mesmo quando a lista está vazia."""
    return max((j.get("id", 0) for j in jogos_list), default=0) + 1


def _encontrar_por_id(id_jogo: int) -> Optional[Dict[str, Any]]:
    """Retorna o jogo com o id informado ou None se não existir."""
    return next((j for j in jogos if j.get("id") == id_jogo or j.get("id_jogo") == id_jogo), None)


def _titulo_ja_existe(titulo: str, ignorar_id: Optional[int] = None) -> bool:
    """Verifica existência de título (case-insensitive). Pode ignorar um id (útil na atualização)."""
    titulo_norm = (titulo or "").strip().lower()
    if not titulo_norm:
        return False
    return any(
        (j.get("id") != ignorar_id and j.get("id_jogo") != ignorar_id)
        and (j.get("titulo", "").strip().lower() == titulo_norm)
        for j in jogos
    )


def _validar_campos_obrigatorios(titulo: Optional[str], genero: Optional[str]) -> bool:
    """Valida presença dos campos obrigatórios titulo e genero."""
    return bool(titulo and titulo.strip()) and bool(genero and genero.strip())


def Cadastrar_Jogo(titulo: str, descricao: Optional[str], genero: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Cadastra um novo jogo.

    Retorna (código, jogo) — em caso de erro retorna (código, None).
    """
    if not _validar_campos_obrigatorios(titulo, genero):
        return DADOS_INVALIDOS, None

    if _titulo_ja_existe(titulo):
        return CONFLITO, None

    novo_jogo = {
        "id": _proximo_id(jogos),
        "id_jogo": None,  # manter compatibilidade se necessário; pode ser preenchido por quem consumir
        "titulo": titulo.strip(),
        "descricao": (descricao or "").strip(),
        "genero": genero.strip(),
        "nota_geral": 0.0
    }
    jogos.append(novo_jogo)
    salvar_jogos()
    return OK, novo_jogo


def Listar_Jogo() -> Tuple[int, List[Dict[str, Any]]]:
    """Retorna a lista completa de jogos."""
    return OK, jogos


def Busca_Jogo(id_jogo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Busca um jogo por id."""
    jogo = _encontrar_por_id(id_jogo)
    if jogo is None:
        return NAO_ENCONTRADO, None
    return OK, jogo


def Atualizar_Jogo(id_jogo: int, titulo: str, descricao: Optional[str], genero: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Atualiza campos de um jogo existente.

    Verifica existência, valida campos e evita conflito de título com outros jogos.
    """
    jogo = _encontrar_por_id(id_jogo)
    if jogo is None:
        return NAO_ENCONTRADO, None

    if not _validar_campos_obrigatorios(titulo, genero):
        return DADOS_INVALIDOS, None

    if _titulo_ja_existe(titulo, ignorar_id=id_jogo):
        return CONFLITO, None

    jogo["titulo"] = titulo.strip()
    jogo["descricao"] = (descricao or "").strip()
    jogo["genero"] = genero.strip()
    salvar_jogos()
    return OK, jogo


def Remover_Jogo(id_jogo: int) -> Tuple[int, Optional[None]]:
    """Remove um jogo por id."""
    jogo = _encontrar_por_id(id_jogo)
    if jogo is None:
        return NAO_ENCONTRADO, None

    jogos.remove(jogo)
    salvar_jogos()
    return OK, None
