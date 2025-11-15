from typing import Tuple, Optional, Dict, Any

from dados.database import perfis, salvar_perfis
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO
from controles import jogo_controler

def _encontrar_perfil(id_perfil: int) -> Optional[Dict[str, Any]]:
    return next((p for p in perfis if p.get("id") == id_perfil or p.get("ID_perfil") == id_perfil), None)

def Avaliar_Jogo(id_perfil: int, id_jogo: int, nota: float, opiniao: Optional[str] = "") -> Tuple[int, Optional[Dict[str, Any]]]:
    """Adiciona/atualiza avaliação (separa da biblioteca)."""
    # valida nota
    try:
        nota_val = float(nota)
    except Exception:
        return DADOS_INVALIDOS, None
    if nota_val < 0 or nota_val > 10:
        return DADOS_INVALIDOS, None

    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    # valida existência do jogo
    codigo_jogo, jogo = jogo_controler.Busca_Jogo(id_jogo)
    if codigo_jogo != OK:
        return NAO_ENCONTRADO, None

    avaliacoes = perfil.setdefault("avaliacoes", [])
    entry = next((e for e in avaliacoes if e.get("jogo_id") == id_jogo), None)
    if entry:
        entry["nota"] = nota_val
        entry["opiniao"] = (opiniao or "").strip()
    else:
        avaliacoes.append({
            "jogo_id": id_jogo,
            "nota": nota_val,
            "opiniao": (opiniao or "").strip()
        })

    salvar_perfis()
    return OK, perfil

def Remover_Avaliacao(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[None]]:
    """Remove avaliação do perfil."""
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    avaliacoes = perfil.get("avaliacoes", [])
    entry = next((e for e in avaliacoes if e.get("jogo_id") == id_jogo), None)
    if not entry:
        return NAO_ENCONTRADO, None

    avaliacoes.remove(entry)
    salvar_perfis()
    return OK, None