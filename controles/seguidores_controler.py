from typing import Tuple, Optional, List, Dict, Any

from dados.database import perfis, salvar_perfis
from utils.codigos import OK, NAO_ENCONTRADO, CONFLITO, DADOS_INVALIDOS

__all__ = [
    "Seguir_Perfil",
    "Parar_de_Seguir",
    "Listar_Seguidores",
    "Listar_Seguindo",
    "Is_Seguindo"
]

def _encontrar_perfil(id_perfil: int) -> Optional[Dict[str, Any]]:
    return next((p for p in perfis if p.get("id") == id_perfil or p.get("ID_perfil") == id_perfil), None)

def Seguir_Perfil(id_seguidor: int, id_alvo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Faz id_seguidor seguir id_alvo."""
    if id_seguidor == id_alvo:
        return DADOS_INVALIDOS, None

    seguidor = _encontrar_perfil(id_seguidor)
    alvo = _encontrar_perfil(id_alvo)
    if seguidor is None or alvo is None:
        return NAO_ENCONTRADO, None

    seguindo = seguidor.setdefault("seguindo", [])
    seguidores = alvo.setdefault("seguidores", [])
    if id_alvo in seguindo:
        return CONFLITO, None

    seguindo.append(id_alvo)
    seguidores.append(id_seguidor)
    salvar_perfis()
    return OK, seguidor

def Parar_de_Seguir(id_seguidor: int, id_alvo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Faz id_seguidor parar de seguir id_alvo."""
    seguidor = _encontrar_perfil(id_seguidor)
    alvo = _encontrar_perfil(id_alvo)
    if seguidor is None or alvo is None:
        return NAO_ENCONTRADO, None

    seguindo = seguidor.get("seguindo", [])
    if id_alvo not in seguindo:
        return NAO_ENCONTRADO, None

    seguindo.remove(id_alvo)
    if id_seguidor in alvo.get("seguidores", []):
        alvo["seguidores"].remove(id_seguidor)
    salvar_perfis()
    return OK, seguidor

def Listar_Seguidores(id_perfil: int) -> Tuple[int, List[int]]:
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, []
    return OK, perfil.get("seguidores", [])

def Listar_Seguindo(id_perfil: int) -> Tuple[int, List[int]]:
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, []
    return OK, perfil.get("seguindo", [])

def Is_Seguindo(id_seguidor: int, id_alvo: int) -> bool:
    seguidor = _encontrar_perfil(id_seguidor)
    if seguidor is None:
        return False
    return id_alvo in seguidor.get("seguindo", [])