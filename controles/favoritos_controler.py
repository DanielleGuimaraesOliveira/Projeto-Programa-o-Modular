from typing import Tuple, Optional, List, Dict, Any

from dados.database import perfis, salvar_perfis
from utils.codigos import OK, NAO_ENCONTRADO, CONFLITO
from controles import jogo_controler

__all__ = ["Favoritar_Jogo", "Desfavoritar_Jogo", "Listar_Favoritos"]

def _encontrar_perfil(id_perfil: int) -> Optional[Dict[str, Any]]:
    return next((p for p in perfis if p.get("id") == id_perfil or p.get("ID_perfil") == id_perfil), None)

def Favoritar_Jogo(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    # valida jogo existe
    c, jogo = jogo_controler.Busca_Jogo(id_jogo)
    if c != OK or jogo is None:
        return NAO_ENCONTRADO, None

    favs = perfil.setdefault("favoritos", [])
    if id_jogo in favs:
        return CONFLITO, None
    favs.append(id_jogo)
    salvar_perfis()
    return OK, perfil

def Desfavoritar_Jogo(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[None]]:
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    favs = perfil.get("favoritos", [])
    if id_jogo not in favs:
        return NAO_ENCONTRADO, None
    favs.remove(id_jogo)
    salvar_perfis()
    return OK, None

def Listar_Favoritos(id_perfil: int) -> Tuple[int, List[int]]:
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, []
    return OK, perfil.get("favoritos", [])