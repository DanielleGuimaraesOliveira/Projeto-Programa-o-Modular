# controles/favoritos_controler.py
"""
Módulo de Favoritos.
Gerencia a lista de jogos favoritos de cada perfil.
"""
from typing import Tuple, Optional, List, Dict, Any
from utils.codigos import OK, NAO_ENCONTRADO, CONFLITO
# removido: from controles import jogo_controler
import json
import os

__all__ = ["Favoritar_Jogo", "Desfavoritar_Jogo", "Listar_Favoritos"]

def _encontrar_perfil(id_perfil: int) -> Optional[Dict[str, Any]]:
    """
    Objetivo:
    - Recuperar o dicionário do perfil com id `id_perfil` usando o TAD de perfis.

    Descrição:
    - Importa localmente `perfil_controler` para evitar import circular e retorna o perfil.
    
    Parâmetros:
    - id_perfil (int): identificador do perfil.

    Retorno:
    - dict do perfil se encontrado, caso contrário None.
    """
    from controles import perfil_controler
    return next((p for p in perfil_controler._get_perfis() if p.get("id") == id_perfil), None)

def Favoritar_Jogo(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Adicionar um jogo à lista de favoritos de um perfil.

    Descrição:
    - Verifica existência do perfil e do jogo.
    - Impede duplicação (mesmo jogo não pode ser favoritado mais de uma vez pelo mesmo perfil).
    - Adiciona o id_jogo na lista 'favoritos' do perfil e marca perfis para gravação.

    Parâmetros:
    - id_perfil (int): identificador do perfil que vai favoritar.
    - id_jogo (int): identificador do jogo a favoritar.

    Assertivas:
    - Pré: perfil existe; jogo existe.
    - Pós: id_jogo presente na lista de favoritos do perfil apenas uma vez.

    Retorno:
    - (OK, perfil_dict) — sucesso e retorno do perfil atualizado.
    - (NAO_ENCONTRADO, None) — perfil ou jogo não encontrado.
    - (CONFLITO, None) — jogo já favoritado por esse perfil.
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    c, jogo = jogo_controler.Busca_Jogo(id_jogo)
    if c != OK or jogo is None:
        return NAO_ENCONTRADO, None

    favs = perfil.setdefault("favoritos", [])
    if id_jogo in favs:
        return CONFLITO, None
    favs.append(id_jogo)
    from controles import perfil_controler
    perfil_controler.salvar_perfis()
    return OK, perfil

def Desfavoritar_Jogo(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[None]]:
    """
    Objetivo:
    - Remover o marcador de favorito de um jogo para um perfil.

    Descrição:
    - Localiza o perfil e verifica se o jogo está favoritado.
    - Remove o id_jogo da lista 'favoritos' sem afetar biblioteca ou avaliações.
    - Marca perfis para gravação.

    Parâmetros:
    - id_perfil (int): identificador do perfil.
    - id_jogo (int): identificador do jogo a desfavoritar.

    Assertivas:
    - Pré: perfil existe; se o jogo não estiver favoritado, retorna NAO_ENCONTRADO.
    - Pós: id_jogo removido da lista de favoritos do perfil.

    Retorno:
    - (OK, None) — desfavoritar bem-sucedido.
    - (NAO_ENCONTRADO, None) — perfil inexistente ou jogo não está favoritado.
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None
    favs = perfil.get("favoritos", [])
    if id_jogo not in favs:
        return NAO_ENCONTRADO, None
    favs.remove(id_jogo)
    from controles import perfil_controler
    perfil_controler.salvar_perfis()
    return OK, None

def Listar_Favoritos(id_perfil: int) -> Tuple[int, List[int]]:
    """
    Objetivo:
    - Retornar a lista de jogos favoritados por um perfil.

    Descrição:
    - Recupera o perfil e devolve o campo 'favoritos' (lista de ids de jogos).
    - Se o perfil não existir, retorna código de não encontrado.

    Parâmetros:
    - id_perfil (int): identificador do perfil.

    Retorno:
    - (OK, lista_de_ids) — sucesso.
    - (NAO_ENCONTRADO, []) — perfil inexistente.
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, []
    return OK, perfil.get("favoritos", [])