# controles/avaliacao_controler.py
from typing import Tuple, Optional, Dict, List, Any
from dados.database import perfis, jogos, salvar_jogos, avaliacoes, salvar_avaliacoes
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO

__all__ = [
    "Avaliar_jogo", "Listar_avaliacao", "Listar_avaliacao_por_id", 
    "Editar_avaliacao", "Remover_avaliacao"
]

def _encontrar_jogo(id_jogo: int) -> Optional[Dict[str, Any]]:
    return next((j for j in jogos if j.get("id") == id_jogo), None)

def _recalcular_nota_geral(id_jogo: int) -> None:
    """Recalcula a média do jogo usando todas as avaliações."""
    notas = [a["score"] for a in avaliacoes if a.get("id_jogo") == id_jogo]
    jogo = _encontrar_jogo(id_jogo)
    if jogo:
        if len(notas) > 0:
            media = sum(notas) / len(notas)
            jogo["nota_geral"] = round(media, 2)
        else:
            jogo["nota_geral"] = 0.0
        salvar_jogos()

def Avaliar_jogo(id_jogo: int, score: float, descricao: str, id_perfil: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    # Valida IDs
    if not any(p.get("id") == id_perfil for p in perfis):
        return NAO_ENCONTRADO, None
    if not _encontrar_jogo(id_jogo):
        return NAO_ENCONTRADO, None

    # Valida Score (0 a 10)
    try:
        s = float(score)
        if not (0.0 <= s <= 10.0):
            return DADOS_INVALIDOS, None
    except (ValueError, TypeError):
        return DADOS_INVALIDOS, None

    # Verifica Duplicidade (Regra: Avaliação Única por Jogo)
    ja_existe = any(a.get("id_perfil") == id_perfil and a.get("id_jogo") == id_jogo for a in avaliacoes)
    if ja_existe:
        return CONFLITO, None

    novo_id = max((a.get("id", 0) for a in avaliacoes), default=0) + 1
    
    nova_avaliacao = {
        "id": novo_id,
        "id_jogo": id_jogo,
        "id_perfil": id_perfil,
        "score": s,
        "descricao": descricao or ""
    }
    
    avaliacoes.append(nova_avaliacao)
    salvar_avaliacoes()
    _recalcular_nota_geral(id_jogo) # Recalcula nota geral
    return OK, nova_avaliacao

def Listar_avaliacao() -> Tuple[int, List[Dict[str, Any]]]:
    return OK, avaliacoes

def Listar_avaliacao_por_id(id_avaliacao: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    avaliacao = next((a for a in avaliacoes if a.get("id") == id_avaliacao), None)
    if avaliacao is None:
        return NAO_ENCONTRADO, None
    return OK, avaliacao

def Editar_avaliacao(id_avaliacao: int, score: Optional[float], descricao: Optional[str]) -> Tuple[int, Optional[Dict[str, Any]]]:
    avaliacao = next((a for a in avaliacoes if a.get("id") == id_avaliacao), None)
    if avaliacao is None:
        return NAO_ENCONTRADO, None

    if score is not None:
        try:
            s = float(score)
            if not (0.0 <= s <= 10.0):
                return DADOS_INVALIDOS, None
            avaliacao["score"] = s
        except ValueError:
            return DADOS_INVALIDOS, None

    if descricao is not None:
        avaliacao["descricao"] = descricao

    salvar_avaliacoes()
    _recalcular_nota_geral(avaliacao["id_jogo"])
    return OK, avaliacao

def Remover_avaliacao(id_avaliacao: int) -> Tuple[int, Optional[None]]:
    avaliacao = next((a for a in avaliacoes if a.get("id") == id_avaliacao), None)
    if avaliacao is None:
        return NAO_ENCONTRADO, None

    id_jogo_afetado = avaliacao["id_jogo"]
    avaliacoes.remove(avaliacao)
    salvar_avaliacoes()
    _recalcular_nota_geral(id_jogo_afetado)
    return OK, None