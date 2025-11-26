# controles/biblioteca_controler.py
"""
Lógica da Biblioteca.
Gerencia a coleção de jogos do usuário, garantindo unicidade de títulos
e status exclusivo (jogando/jogado/platinado).
"""
from typing import Tuple, Optional, Dict, Any, List
from utils.codigos import OK, NAO_ENCONTRADO, DADOS_INVALIDOS, CONFLITO
from controles import jogo_controler

VALID_STATUSES = {"jogando", "jogado", "platinado"}

__all__ = [
    "Adicionar_Jogo", "Remover_Jogo", "Atualizar_Status_Jogo",
    "Listar_Biblioteca", "Listar_Biblioteca_por_status"
]


def _encontrar_perfil(id_perfil: int) -> Optional[Dict[str, Any]]:
    """
    Objetivo:
    - Recuperar o dicionário do perfil com id `id_perfil` usando o TAD de perfis.

    Descrição:
    - Importa localmente `perfil_controler` para evitar import circular e retorna o perfil.
    """
    from controles import perfil_controler
    return next((p for p in perfil_controler._get_perfis() if p.get("id") == id_perfil), None)


def _recalcular_contadores(perfil: Dict[str, Any]) -> None:
    """
    Objetivo:
    - Atualizar os contadores derivados do campo 'biblioteca' (jogando, jogados, platinados).

    Descrição:
    - Conta itens na biblioteca com status correspondente e atualiza os campos no perfil.
    """
    bibli = perfil.get("biblioteca", [])
    perfil["jogando"] = sum(1 for e in bibli if e.get("status") == "jogando")
    perfil["jogados"] = sum(1 for e in bibli if e.get("status") == "jogado")
    perfil["platinados"] = sum(1 for e in bibli if e.get("status") == "platinado")


def Adicionar_Jogo(id_perfil: int, id_jogo: int, status: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Adicionar um jogo à biblioteca de um perfil com um status obrigatório e exclusivo.

    Descrição:
    - Verifica existência do perfil e do jogo.
    - Valida o status (deve ser um dos valores permitidos).
    - Impede duplicação (um mesmo jogo não pode aparecer duas vezes na biblioteca do usuário).
    - Adiciona a entrada {"id_jogo": id_jogo, "status": status} e recalcula contadores.
    - Marca perfis para gravação via TAD (salvar_perfis).

    Parâmetros:
    - id_perfil (int): identificador do perfil.
    - id_jogo (int): identificador do jogo.
    - status (str): um dos {"jogando", "jogado", "platinado"} (case-insensitive).

    Assertivas:
    - Pré: perfil existe; jogo existe; status válido.
    - Pós: a biblioteca do perfil contém exatamente uma entrada para id_jogo com o status definido;
           contadores atualizados.

    Retorno:
    - (OK, perfil_dict) — operação bem-sucedida.
    - (NAO_ENCONTRADO, None) — perfil ou jogo não encontrado.
    - (DADOS_INVALIDOS, None) — status inválido.
    - (CONFLITO, None) — jogo já presente na biblioteca do perfil.
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    c, jogo = jogo_controler.Busca_Jogo(id_jogo)
    if c != OK or jogo is None:
        return NAO_ENCONTRADO, None

    if not status or status.lower() not in VALID_STATUSES:
        return DADOS_INVALIDOS, None
    status = status.lower()

    bibli = perfil.setdefault("biblioteca", [])
    existing = next((e for e in bibli if e.get("id_jogo") == id_jogo), None)
    if existing:
        return CONFLITO, None

    bibli.append({"id_jogo": id_jogo, "status": status})
    _recalcular_contadores(perfil)
    from controles import perfil_controler
    perfil_controler.salvar_perfis()
    return OK, perfil


def Remover_Jogo(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[None]]:
    """
    Objetivo:
    - Remover um jogo da biblioteca de um perfil sem afetar avaliações ou favoritos.

    Descrição:
    - Localiza o perfil e a entrada na biblioteca correspondente a id_jogo.
    - Remove a entrada, recalcula contadores e marca perfis para gravação.

    Parâmetros:
    - id_perfil (int): identificador do perfil.
    - id_jogo (int): identificador do jogo a remover.

    Assertivas:
    - Pré: perfil existe; se não existir a entrada, retorna NAO_ENCONTRADO.
    - Pós: entrada removida e contadores atualizados.

    Retorno:
    - (OK, None) — remoção bem-sucedida.
    - (NAO_ENCONTRADO, None) — perfil inexistente ou item não presente na biblioteca.
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None
    bibli = perfil.get("biblioteca", [])
    entry = next((e for e in bibli if e.get("id_jogo") == id_jogo), None)
    if not entry:
        return NAO_ENCONTRADO, None
    bibli.remove(entry)
    _recalcular_contadores(perfil)
    from controles import perfil_controler
    perfil_controler.salvar_perfis()
    return OK, None


def Atualizar_Status_Jogo(id_perfil: int, id_jogo: int, status: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Atualizar o status de um jogo já presente na biblioteca do perfil.

    Descrição:
    - Verifica existência do perfil e validade do status.
    - Localiza a entrada da biblioteca e altera seu campo 'status', evitando duplicações.
    - Recalcula contadores e marca perfis para gravação.

    Parâmetros:
    - id_perfil (int): identificador do perfil.
    - id_jogo (int): identificador do jogo cujo status será alterado.
    - status (str): novo status válido {"jogando","jogado","platinado"}.

    Assertivas:
    - Pré: perfil existe; entrada para id_jogo existe; status válido.
    - Pós: existe exatamente uma entrada para id_jogo com o novo status; contadores ajustados.

    Retorno:
    - (OK, perfil_dict) — atualização bem-sucedida.
    - (NAO_ENCONTRADO, None) — perfil inexistente ou item não está na biblioteca.
    - (DADOS_INVALIDOS, None) — status inválido.
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
        return NAO_ENCONTRADO, None
    entry["status"] = status
    _recalcular_contadores(perfil)
    from controles import perfil_controler
    perfil_controler.salvar_perfis()
    return OK, perfil


def Listar_Biblioteca(id_perfil: int) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Objetivo:
    - Retornar todos os itens ativos da biblioteca de um perfil.

    Descrição:
    - Recupera o perfil e devolve a lista 'biblioteca' (ou lista vazia se ausente).

    Parâmetros:
    - id_perfil (int): identificador do perfil.

    Retorno:
    - (OK, lista_de_entradas) — sucesso.
    - (NAO_ENCONTRADO, []) — perfil inexistente.
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, []
    return OK, perfil.get("biblioteca", [])


def Listar_Biblioteca_por_status(id_perfil: int, status: str) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Objetivo:
    - Retornar itens da biblioteca filtrados por status.

    Descrição:
    - Valida perfil e status, filtra entradas cujo campo 'status' corresponde ao solicitado.

    Parâmetros:
    - id_perfil (int): identificador do perfil.
    - status (str): filtro de status (case-insensitive).

    Assertivas:
    - Pré: perfil existe; status válido.
    - Pós: retorna apenas entradas cujo 'status' corresponda ao filtro.

    Retorno:
    - (OK, lista_filtrada) — sucesso.
    - (NAO_ENCONTRADO, []) — perfil inexistente.
    - (DADOS_INVALIDOS, []) — status inválido.
    """
    perfil = _encontrar_perfil(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, []
    if not status or status.lower() not in VALID_STATUSES:
        return DADOS_INVALIDOS, []
    filtrada = [e for e in perfil.get("biblioteca", []) if e.get("status") == status.lower()]
    return OK, filtrada