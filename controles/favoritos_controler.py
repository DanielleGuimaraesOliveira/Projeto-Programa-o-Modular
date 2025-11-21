from typing import Tuple, Optional, List, Dict, Any


try:
    from controles.biblioteca_controler import (
        Favoritar_Jogo as _bib_favoritar,
        Desfavoritar_Jogo as _bib_desfavoritar,
        Listar_Favoritos as _bib_listar
    )
except (ImportError, ModuleNotFoundError):
    # stubs claros para sinalizar erro em tempo de execução caso o módulo falte
    def _missing(*args, **kwargs):
        raise ModuleNotFoundError(
            "Módulo 'controles.biblioteca_controler' não disponível. "
            "Implemente Favoritar_Jogo/Desfavoritar_Jogo/Listar_Favoritos ou adicione este módulo."
        )
    _bib_favoritar = _missing  # type: ignore
    _bib_desfavoritar = _missing  # type: ignore
    _bib_listar = _missing  # type: ignore

__all__ = ["Favoritar_Jogo", "Desfavoritar_Jogo", "Listar_Favoritos"]

def Favoritar_Jogo(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Favorita um jogo para o perfil. Delega para controles.biblioteca_controler.Favoritar_Jogo.
    Retorna (codigo, perfil) compatível com o padrão do projeto.
    """
    return _bib_favoritar(id_perfil, id_jogo)

def Desfavoritar_Jogo(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[None]]:
    """
    Remove um jogo dos favoritos do perfil. Delega para controles.biblioteca_controler.Desfavoritar_Jogo.
    """
    return _bib_desfavoritar(id_perfil, id_jogo)

def Listar_Favoritos(id_perfil: int) -> Tuple[int, List[int]]:
    """
    Retorna a lista de ids de jogos favoritados pelo perfil.
    """
    return _bib_listar(id_perfil)