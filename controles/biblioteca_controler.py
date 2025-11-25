# controles/biblioteca_controler.py
"""
Lógica da Biblioteca.
Gerencia a coleção de jogos do usuário, garantindo unicidade de títulos
e status exclusivo (jogando/jogado/platinado).
"""
from typing import Tuple, Optional, Dict, Any, List

from dados.database import perfis, salvar_perfis
from utils.codigos import OK, NAO_ENCONTRADO, DADOS_INVALIDOS, CONFLITO
from controles import jogo_controler

VALID_STATUSES = {"jogando", "jogado", "platinado"}

__all__ = [
    "Adicionar_Jogo", "Remover_Jogo", "Atualizar_Status_Jogo",
    "Listar_Biblioteca", "Listar_Biblioteca_por_status"
]

def _encontrar_perfil(id_perfil: int) -> Optional[Dict[str, Any]]:
    return next((p for p in perfis if p.get("id") == id_perfil), None)

def _recalcular_contadores(perfil: Dict[str, Any]) -> None:
    """Recalcula campos derivados (jogando, jogados, platinados)."""
    bibli = perfil.get("biblioteca", [])
    perfil["jogando"] = sum(1 for e in bibli if e.get("status") == "jogando")
    perfil["jogados"] = sum(1 for e in bibli if e.get("status") == "jogado")
    perfil["platinados"] = sum(1 for e in bibli if e.get("status") == "platinado")

def Adicionar_Jogo(id_perfil: int, id_jogo: int, status: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Adiciona jogo à biblioteca.
    Regras: Jogo único por usuário, status obrigatório e válido.
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    # Valida se o jogo existe no sistema
    codigo_jogo, jogo = jogo_controler.Busca_Jogo(id_jogo)
    if codigo_jogo != OK or jogo is None:
        return NAO_ENCONTRADO, None

    # Valida status
    if not status or status.lower() not in VALID_STATUSES:
        return DADOS_INVALIDOS, None
    status = status.lower()

    bibli = perfil.setdefault("biblioteca", [])
    
    # PADRONIZAÇÃO: Mudamos de 'jogo_id' para 'id_jogo'
    entry = next((e for e in bibli if e.get("id_jogo") == id_jogo), None)
    
    if entry:
        # Já existe — regra de Prevenção de Duplicatas 
        return CONFLITO, None

    # Criação do item na biblioteca
    bibli.append({"id_jogo": id_jogo, "status": status})
    
    _recalcular_contadores(perfil)
    salvar_perfis()
    return OK, perfil

def Remover_Jogo(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[None]]:
    """Remove jogo da biblioteca e recalcula contadores."""
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    bibli = perfil.get("biblioteca", [])
    entry = next((e for e in bibli if e.get("id_jogo") == id_jogo), None)
    
    if not entry:
        return NAO_ENCONTRADO, None

    bibli.remove(entry)
    _recalcular_contadores(perfil)
    salvar_perfis()
    return OK, None

def Atualizar_Status_Jogo(id_perfil: int, id_jogo: int, status: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Atualiza status.
    Regra: Ao alterar, o anterior é removido (substituído)[cite: 31].
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    if not status or status.lower() not in VALID_STATUSES:
        return DADOS_INVALIDOS, None
    status = status.lower()

    bibli = perfil.setdefault("biblioteca", [])
    entry = next((e for e in bibli if e.get("id_jogo") == id_jogo), None)
    
    if not entry:
        return NAO_ENCONTRADO, None # Jogo não está na biblioteca

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
    """Retorna itens filtrados por status."""
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, [] # [cite: 222]
    
    if not status or status.lower() not in VALID_STATUSES:
        return DADOS_INVALIDOS, [] # [cite: 222]
    
    filtrada = [e for e in perfil.get("biblioteca", []) if e.get("status") == status.lower()]
    return OK, filtrada