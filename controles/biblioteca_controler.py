from typing import Tuple, Optional, Dict, Any, List

from dados.database import perfis, salvar_perfis
from utils.codigos import OK, NAO_ENCONTRADO, DADOS_INVALIDOS, CONFLITO
from controles import jogo_controler

VALID_STATUSES = {"jogando", "jogado", "platinado"}

def _encontrar_perfil(id_perfil: int) -> Optional[Dict[str, Any]]:
    return next((p for p in perfis if p.get("id") == id_perfil or p.get("ID_perfil") == id_perfil), None)

def _recalcular_contadores(perfil: Dict[str, Any]) -> None:
    """Recalcula campos derivados (jogando, jogados, platinados) a partir da biblioteca."""
    bibli = perfil.get("biblioteca", [])
    perfil["jogando"] = sum(1 for e in bibli if e.get("status") == "jogando")
    perfil["jogados"] = sum(1 for e in bibli if e.get("status") == "jogado")
    perfil["platinados"] = sum(1 for e in bibli if e.get("status") == "platinado")

def Adicionar_Jogo(id_perfil: int, id_jogo: int, status: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Adiciona um jogo à biblioteca com status (cada jogo apenas uma vez)."""
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    # valida jogo existe
    codigo_jogo, jogo = jogo_controler.Busca_Jogo(id_jogo)
    if codigo_jogo != OK or jogo is None:
        return NAO_ENCONTRADO, None

    # valida status
    if not status or status.lower() not in VALID_STATUSES:
        return DADOS_INVALIDOS, None
    status = status.lower()

    bibli = perfil.setdefault("biblioteca", [])
    entry = next((e for e in bibli if e.get("jogo_id") == id_jogo), None)
    if entry:
        # já existe — prevenir duplicação; use Atualizar_Status_Jogo para trocar status
        return CONFLITO, None

    bibli.append({"jogo_id": id_jogo, "status": status})
    _recalcular_contadores(perfil)
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
    _recalcular_contadores(perfil)
    salvar_perfis()
    return OK, None

def Atualizar_Status_Jogo(id_perfil: int, id_jogo: int, status: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Atualiza status de um jogo existente na biblioteca (remove duplicatas e recalcula contadores)."""
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    if not status or status.lower() not in VALID_STATUSES:
        return DADOS_INVALIDOS, None
    status = status.lower()

    bibli = perfil.setdefault("biblioteca", [])
    entry = next((e for e in bibli if e.get("jogo_id") == id_jogo), None)
    if not entry:
        return NAO_ENCONTRADO, None

    entry["status"] = status
    _recalcular_contadores(perfil)
    salvar_perfis()
    return OK, perfil

def Listar_Biblioteca(id_perfil: int) -> Tuple[int, List[Dict[str, Any]]]:
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, []
    return OK, perfil.get("biblioteca", [])

def Listar_Biblioteca_por_status(id_perfil: int, status: str) -> Tuple[int, List[Dict[str, Any]]]:
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, []
    if not status or status.lower() not in VALID_STATUSES:
        return DADOS_INVALIDOS, []
    filtrada = [e for e in perfil.get("biblioteca", []) if e.get("status") == status.lower()]
    return OK, filtrada

__all__ = [
    "Adicionar_Jogo", "Remover_Jogo", "Atualizar_Status_Jogo",
    "Listar_Biblioteca", "Listar_Biblioteca_por_status"
]