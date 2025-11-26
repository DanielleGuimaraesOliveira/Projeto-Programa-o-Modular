# controles/avaliacao_controler.py
from typing import Tuple, Optional, Dict, List, Any
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO

__all__ = [
    "Avaliar_jogo", "Listar_avaliacao", "Listar_avaliacao_por_id",
    "Editar_avaliacao", "Remover_avaliacao"
]

def _encontrar_jogo(id_jogo: int) -> Optional[Dict[str, Any]]:
    """
    Objetivo:
    - Recuperar o dicionário do jogo com id `id_jogo`.

    Descrição:
    - Importa localmente o jogo_controler para evitar import circular.
    - Usa a função pública Busca_Jogo do módulo de jogo.

    Parâmetros:
    - id_jogo (int): identificador do jogo.

    Retorno:
    - Dict do jogo se encontrado, caso contrário None.
    """
    from controles import jogo_controler
    codigo, jogo = jogo_controler.Busca_Jogo(id_jogo)
    return jogo if codigo == OK else None


def _recalcular_nota_geral(id_jogo: int) -> None:
    """
    Objetivo:
    - Recalcular e atualizar a nota_geral do jogo identificado por id_jogo.

    Descrição:
    - Varre todas as avaliações contidas nos perfis, agrega as notas do jogo
      informado e calcula a média (duas casas).
    - Atualiza o campo `nota_geral` do jogo via API do jogo_controler e marca
      jogos como modificados (salvar_jogos).

    Parâmetros:
    - id_jogo (int): identificador do jogo cuja nota deve ser recalculada.

    Assertivas / Invariantes:
    - Se não houver avaliações, nota_geral passa a 0.0.
    - A atualização marca o storage de jogos para gravação posterior.

    Retorno:
    - None (efeito colateral: atualiza jogo em memória).
    """
    from controles import perfil_controler
    from controles import jogo_controler

    notas: List[float] = []
    for p in perfil_controler._get_perfis():
        for a in p.get("avaliacoes", []):
            if a.get("id_jogo") == id_jogo:
                n = a.get("nota")
                if isinstance(n, (int, float)):
                    notas.append(float(n))

    nova = round(sum(notas) / len(notas), 2) if notas else 0.0
    codigo, jogo = jogo_controler.Busca_Jogo(id_jogo)
    if codigo == OK and jogo is not None:
        jogo["nota_geral"] = nova
        jogo_controler.salvar_jogos()


def Avaliar_jogo(id_jogo: int, score: float, descricao: str, id_perfil: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Registrar uma avaliação (nota + opinião) de um perfil para um jogo.

    Descrição:
    - Verifica existência de perfil e jogo.
    - Valida `score` (float entre 0.0 e 10.0).
    - Impede duplicidade: um perfil avalia um jogo no máximo uma vez.
    - Cria a avaliação no perfil, marca perfis para gravação e recalcula a nota geral.

    Parâmetros:
    - id_jogo (int): id do jogo a ser avaliado.
    - score (float): nota numérica obrigatória (0.0 a 10.0).
    - descricao (str): texto opcional da avaliação.
    - id_perfil (int): id do perfil que avalia.

    Assertivas:
    - Pré: perfil e jogo existem; score é numérico e 0.0 <= score <= 10.0.
    - Pós: existe exatamente uma avaliação do par (id_perfil, id_jogo); nota_geral é atualizada.

    Retorno:
    - (OK, avaliacao_dict) — criado com sucesso.
    - (CONFLITO, None) — avaliação já existe para o par perfil/jogo.
    - (DADOS_INVALIDOS, None) — score inválido.
    - (NAO_ENCONTRADO, None) — perfil ou jogo inexistente.
    """
    from controles import perfil_controler

    # valida perfil e jogo
    if not any(p.get("id") == id_perfil for p in perfil_controler._get_perfis()):
        return NAO_ENCONTRADO, None
    if not _encontrar_jogo(id_jogo):
        return NAO_ENCONTRADO, None

    try:
        s = float(score)
        if not (0.0 <= s <= 10.0):
            return DADOS_INVALIDOS, None
    except (ValueError, TypeError):
        return DADOS_INVALIDOS, None

    perfil = next((p for p in perfil_controler._get_perfis() if p.get("id") == id_perfil), None)
    if perfil is None:
        return NAO_ENCONTRADO, None

    avals = perfil.setdefault("avaliacoes", [])
    if any(a.get("id_jogo") == id_jogo for a in avals):
        return CONFLITO, None

    novo_id = max((a.get("id", 0) for p in perfil_controler._get_perfis() for a in p.get("avaliacoes", [])), default=0) + 1
    nova = {"id": novo_id, "id_jogo": id_jogo, "id_perfil": id_perfil, "nota": s, "opiniao": descricao or ""}
    avals.append(nova)
    perfil_controler.salvar_perfis()
    _recalcular_nota_geral(id_jogo)
    return OK, nova


def Listar_avaliacao() -> Tuple[int, List[Dict[str, Any]]]:
    """
    Objetivo:
    - Retornar todas as avaliações existentes no sistema.

    Descrição:
    - Percorre os perfis e agrega todas as avaliações em uma lista.

    Parâmetros:
    - nenhum

    Assertivas:
    - A lista retornada contém dicionários de avaliação com campos mínimos:
      id, id_jogo, id_perfil, nota, opiniao.

    Retorno:
    - (OK, lista_de_avaliacoes)
    """
    from controles import perfil_controler
    todas: List[Dict[str, Any]] = []
    for p in perfil_controler._get_perfis():
        for a in p.get("avaliacoes", []):
            todas.append(a)
    return OK, todas


def Listar_avaliacao_por_id(id_avaliacao: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Recuperar a avaliação identificada por id_avaliacao.

    Descrição:
    - Varre as avaliações de todos os perfis procurando a avaliação com id fornecido.

    Parâmetros:
    - id_avaliacao (int): identificador da avaliação.

    Retorno:
    - (OK, avaliacao_dict) se encontrada.
    - (NAO_ENCONTRADO, None) caso contrário.
    """
    from controles import perfil_controler
    for p in perfil_controler._get_perfis():
        a = next((x for x in p.get("avaliacoes", []) if x.get("id") == id_avaliacao), None)
        if a:
            return OK, a
    return NAO_ENCONTRADO, None


def Editar_avaliacao(id_avaliacao: int, score: Optional[float], descricao: Optional[str]) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Editar uma avaliação existente (nota e/ou descrição).

    Descrição:
    - Localiza a avaliação por id, valida score se fornecido, aplica mudanças,
      marca perfis para gravação e recalcula nota geral do jogo afetado.

    Parâmetros:
    - id_avaliacao (int): id da avaliação a editar.
    - score (Optional[float]): nova nota (se fornecida).
    - descricao (Optional[str]): novo texto (se fornecido).

    Assertivas:
    - Pré: se score fornecido, deve ser numérico e 0.0 <= score <= 10.0.
    - Pós: avaliação atualizada; nota_geral do jogo recalculada.

    Retorno:
    - (OK, avaliacao_dict) — edição bem-sucedida.
    - (DADOS_INVALIDOS, None) — score inválido.
    - (NAO_ENCONTRADO, None) — avaliação não existe.
    """
    from controles import perfil_controler
    for p in perfil_controler._get_perfis():
        a = next((x for x in p.get("avaliacoes", []) if x.get("id") == id_avaliacao), None)
        if a:
            if score is not None:
                try:
                    s = float(score)
                    if not (0.0 <= s <= 10.0):
                        return DADOS_INVALIDOS, None
                    a["nota"] = s
                except (ValueError, TypeError):
                    return DADOS_INVALIDOS, None
            if descricao is not None:
                a["opiniao"] = descricao
            perfil_controler.salvar_perfis()
            _recalcular_nota_geral(a["id_jogo"])
            return OK, a
    return NAO_ENCONTRADO, None


def Remover_avaliacao(id_avaliacao: int) -> Tuple[int, Optional[None]]:
    """
    Objetivo:
    - Remover uma avaliação do sistema.

    Descrição:
    - Localiza e exclui a avaliação por id dentro do perfil correspondente,
      marca perfis para gravação e recalcula a nota geral do jogo envolvido.

    Parâmetros:
    - id_avaliacao (int): identificador da avaliação a remover.

    Assertivas:
    - Pós: avaliação removida; nota_geral do jogo recalculada.

    Retorno:
    - (OK, None) — remoção bem-sucedida.
    - (NAO_ENCONTRADO, None) — avaliação não encontrada.
    """
    from controles import perfil_controler
    for p in perfil_controler._get_perfis():
        a = next((x for x in p.get("avaliacoes", []) if x.get("id") == id_avaliacao), None)
        if a:
            id_jogo = a["id_jogo"]
            p["avaliacoes"].remove(a)
            perfil_controler.salvar_perfis()
            _recalcular_nota_geral(id_jogo)
            return OK, None
    return NAO_ENCONTRADO, None