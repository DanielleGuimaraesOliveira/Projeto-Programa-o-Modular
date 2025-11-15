# controles/jogo_controler.py
"""Lógica de jogos: cadastro, listagem, busca, atualização e remoção.

Funções mantêm as assinaturas públicas (Cadastrar_Jogo, Listar_Jogo, ...)
para compatibilidade com o restante do projeto.
"""
from typing import Dict, List, Optional, Tuple

from dados.database import jogos, salvar_jogos
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO

__all__ = [
    "Cadastrar_Jogo", "Listar_Jogo", "Busca_Jogo", "Atualizar_Jogo", "Remover_Jogo"
]


def _proximo_id(jogos_list: List[Dict]) -> int:
    """Retorna o próximo id disponível com segurança quando a lista está vazia."""
    return max((j["id"] for j in jogos_list), default=0) + 1


def _encontrar_por_id(id_jogo: int) -> Optional[Dict]:
    """Retorna o jogo com o id informado ou None se não existir."""
    return next((j for j in jogos if j["id"] == id_jogo), None)


def _titulo_ja_existe(titulo: str) -> bool:
    """Verifica existência de título (case-insensitive)."""
    return any(j["titulo"].strip().lower() == titulo.strip().lower() for j in jogos)


def _validar_campos_obrigatorios(titulo: Optional[str], genero: Optional[str]) -> bool:
    """Valida presença dos campos obrigatórios."""
    return bool(titulo and titulo.strip()) and bool(genero and genero.strip())


def Cadastrar_Jogo(titulo: str, descricao: Optional[str], genero: str) -> Tuple[int, Optional[Dict]]:
    """Cadastra um novo jogo.

    Retorna (código, jogo) — em caso de conflito ou dados inválidos retorna (código, None).
    """
    if not _validar_campos_obrigatorios(titulo, genero):
        return DADOS_INVALIDOS, None

    if _titulo_ja_existe(titulo):
        return CONFLITO, None

    novo_jogo = {
        "id": _proximo_id(jogos),
        "titulo": titulo.strip(),
        "descricao": (descricao or "").strip(),
        "genero": genero.strip(),
        "nota_geral": 0.0
    }
    jogos.append(novo_jogo)
    salvar_jogos()
    return OK, novo_jogo


def Listar_Jogo() -> Tuple[int, List[Dict]]:
    """Retorna a lista completa de jogos."""
    return OK, jogos


def Busca_Jogo(id_jogo: int) -> Tuple[int, Optional[Dict]]:
    """Busca um jogo por id."""
    jogo = _encontrar_por_id(id_jogo)
    if jogo is None:
        return NAO_ENCONTRADO, None
    return OK, jogo


def Atualizar_Jogo(id_jogo: int, titulo: str, descricao: Optional[str], genero: str) -> Tuple[int, Optional[Dict]]:
    """Atualiza campos de um jogo existente."""
    jogo = _encontrar_por_id(id_jogo)
    if jogo is None:
        return NAO_ENCONTRADO, None

    if not _validar_campos_obrigatorios(titulo, genero):
        return DADOS_INVALIDOS, None

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
