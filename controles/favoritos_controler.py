# controles/favoritos_controler.py
"""
Módulo de Favoritos.
Gerencia a lista de jogos favoritos de cada perfil.
"""
from typing import Tuple, Optional, List, Dict, Any

from dados.database import perfis, salvar_perfis
from utils.codigos import OK, NAO_ENCONTRADO, CONFLITO
from controles import jogo_controler

__all__ = ["Favoritar_Jogo", "Desfavoritar_Jogo", "Listar_Favoritos"]

def _encontrar_perfil(id_perfil: int) -> Optional[Dict[str, Any]]:
    return next((p for p in perfis if p.get("id") == id_perfil), None)

def Favoritar_Jogo(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Adiciona jogo aos favoritos.
    Regra: Cada jogo pode ser favoritado apenas uma vez por usuário.
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    # Valida se o jogo existe
    c, jogo = jogo_controler.Busca_Jogo(id_jogo)
    if c != OK or jogo is None:
        return NAO_ENCONTRADO, None

    favs = perfil.setdefault("favoritos", [])
    
    # Validação de Duplicidade [cite: 36-37]
    if id_jogo in favs:
        return CONFLITO, None
    
    favs.append(id_jogo)
    salvar_perfis()
    return OK, perfil

def Desfavoritar_Jogo(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[None]]:
    """
    Remove jogo dos favoritos.
    Regra: Apenas remove o marcador, sem alterar status na biblioteca.
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    favs = perfil.get("favoritos", [])
    
    # Verifica se o jogo realmente está favoritado 
    if id_jogo not in favs:
        return NAO_ENCONTRADO, None
    
    favs.remove(id_jogo)
    salvar_perfis()
    return OK, None

def Listar_Favoritos(id_perfil: int) -> Tuple[int, List[int]]:
    """Retorna a lista de IDs dos jogos favoritos."""
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, []
    return OK, perfil.get("favoritos", [])