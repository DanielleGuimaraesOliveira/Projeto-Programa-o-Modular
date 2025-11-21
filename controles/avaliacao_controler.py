from typing import Tuple, Optional, Dict, Any

from dados.database import perfis, jogos, salvar_perfis, salvar_jogos
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO
from controles import jogo_controler

def _encontrar_perfil(id_perfil: int) -> Optional[Dict[str, Any]]:
    return next((p for p in perfis if p.get("id") == id_perfil or p.get("ID_perfil") == id_perfil), None)


def _recalcular_nota_geral(id_jogo: int) -> None:
    """Recalcula e atualiza nota_geral do jogo somando todas as notas presentes nas bibliotecas dos perfis."""
    soma = 0.0
    cont = 0
    for perfil in perfis:
        for entrada in perfil.get("biblioteca", []):
            if entrada.get("jogo_id") == id_jogo and "nota" in entrada:
                try:
                    n = float(entrada.get("nota"))
                except Exception:
                    continue
                soma += n
                cont += 1
    # atualiza no jogo
    codigo, jogo = jogo_controler.Busca_Jogo(id_jogo)
    if codigo == OK and jogo is not None:
        jogo["nota_geral"] = round(soma / cont, 2) if cont > 0 else 0.0
        salvar_jogos()


def Avaliar_Jogo(id_perfil: int, id_jogo: int, nota: float, opiniao: Optional[str] = "") -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Cria ou atualiza a avaliação de um perfil para um jogo.
    - valida perfil e jogo
    - nota deve ser número entre 0 e 10
    - mantém item na biblioteca (cria entrada com jogo_id se necessário) e adiciona/atualiza campos 'nota' e 'opiniao'
    Retorna (código, perfil) em caso de sucesso.
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    codigo_jogo, jogo = jogo_controler.Busca_Jogo(id_jogo)
    if codigo_jogo != OK or jogo is None:
        return NAO_ENCONTRADO, None

    try:
        n = float(nota)
    except Exception:
        return DADOS_INVALIDOS, None
    if not (0.0 <= n <= 10.0):
        return DADOS_INVALIDOS, None

    bibli = perfil.setdefault("biblioteca", [])
    entry = next((e for e in bibli if e.get("jogo_id") == id_jogo), None)
    if entry is None:
        # cria entrada mínima na biblioteca (não define status)
        entry = {"jogo_id": id_jogo, "nota": n, "opiniao": (opiniao or "")}
        bibli.append(entry)
    else:
        # atualiza/insere campos de avaliação
        entry["nota"] = n
        entry["opiniao"] = (opiniao or "")

    salvar_perfis()
    # recalcula nota geral do jogo
    _recalcular_nota_geral(id_jogo)
    return OK, perfil


def Remover_Avaliacao(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[None]]:
    """
    Remove apenas a avaliação (nota/opiniao) de um jogo na biblioteca do perfil.
    Não remove a entrada da biblioteca nem favoritos.
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    bibli = perfil.get("biblioteca", [])
    entry = next((e for e in bibli if e.get("jogo_id") == id_jogo), None)
    if entry is None:
        return NAO_ENCONTRADO, None

    removed = False
    if "nota" in entry:
        entry.pop("nota", None)
        removed = True
    if "opiniao" in entry:
        entry.pop("opiniao", None)
        removed = True

    if not removed:
        # não havia avaliação
        return NAO_ENCONTRADO, None

    salvar_perfis()
    _recalcular_nota_geral(id_jogo)
    return OK, None

__all__ = ["Avaliar_Jogo", "Remover_Avaliacao"]