from typing import Tuple, Optional, Dict, Any, List

from dados.database import perfis, salvar_perfis
from utils.codigos import OK, NAO_ENCONTRADO
from controles import jogo_controler

def _encontrar_perfil(id_perfil: int) -> Optional[Dict[str, Any]]:
    return next((p for p in perfis if p.get("id") == id_perfil or p.get("ID_perfil") == id_perfil), None)

def Adicionar_Jogo(id_perfil: int, id_jogo: int, status: str = "comprado") -> Tuple[int, Optional[Dict[str, Any]]]:
    """Adiciona ou atualiza um jogo na biblioteca com um status (ex: jogando, jogado, platina)."""
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    codigo_jogo, jogo = jogo_controler.Busca_Jogo(id_jogo)
    if codigo_jogo != OK:
        return NAO_ENCONTRADO, None

    bibli = perfil.setdefault("biblioteca", [])
    entry = next((e for e in bibli if e.get("jogo_id") == id_jogo), None)
    if entry:
        entry["status"] = status
    else:
        bibli.append({"jogo_id": id_jogo, "status": status})
    salvar_perfis()
    return OK, perfil

def Remover_Jogo(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[None]]:
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    bibli = perfil.get("biblioteca", [])
    entry = next((e for e in bibli if e.get("jogo_id") == id_jogo), None)
    if not entry:
        return NAO_ENCONTRADO, None

    bibli.remove(entry)
    salvar_perfis()
    return OK, None

def Atualizar_Status_Jogo(id_perfil: int, id_jogo: int, status: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None
    bibli = perfil.setdefault("biblioteca", [])
    entry = next((e for e in bibli if e.get("jogo_id") == id_jogo), None)
    if not entry:
        return NAO_ENCONTRADO, None
    entry["status"] = status
    salvar_perfis()
    return OK, perfil

def Listar_Biblioteca(id_perfil: int) -> Tuple[int, List[Dict[str, Any]]]:
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, []
    return OK, perfil.get("biblioteca", [])