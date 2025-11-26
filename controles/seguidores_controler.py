from typing import Tuple, Optional, List, Dict, Any
from utils.codigos import OK, NAO_ENCONTRADO, CONFLITO, DADOS_INVALIDOS

__all__ = [
    "Seguir_Perfil",
    "Parar_de_Seguir",
    "Listar_Seguidores",
    "Listar_Seguindo",
    "Is_Seguindo"
]

def _encontrar_perfil(id_perfil: int) -> Optional[Dict[str, Any]]:
    """
    Objetivo:
    - Recuperar o dicionário do perfil identificado por id_perfil.

    Descrição:
    - Importa localmente o módulo perfil_controler para evitar import circular.
    - Retorna o dicionário do perfil se existir, caso contrário None.

    Parâmetros:
    - id_perfil (int): identificador do perfil.

    Retorno:
    - Dict do perfil ou None se não encontrado.
    """
    from controles import perfil_controler
    return next((p for p in perfil_controler._get_perfis() if p.get("id") == id_perfil), None)


def Seguir_Perfil(id_seguidor: int, id_alvo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Alternar a relação de seguimento entre dois perfis (seguir / deixar de seguir).

    Descrição:
    - Não permite auto-seguimento.
    - Verifica existência de ambos os perfis.
    - Se o seguidor ainda não segue o alvo, adiciona id_alvo à lista 'seguindo' do seguidor
      e adiciona id_seguidor à lista 'seguidores' do alvo.
    - Marca perfis para gravação via perfil_controler.salvar_perfis().

    Parâmetros:
    - id_seguidor (int): id do perfil que vai seguir/deixar de seguir.
    - id_alvo (int): id do perfil alvo.

    Assertivas:
    - Pré: ids válidos (inteiros) e não iguais.
    - Pós: relação de seguimento refletida nas listas 'seguindo' e 'seguidores' sem duplicatas.

    Retorno:
    - (DADOS_INVALIDOS, None) — tentativa de seguir a si mesmo.
    - (NAO_ENCONTRADO, None) — algum dos perfis não existe.
    - (CONFLITO, None) — seguidor já segue o alvo.
    - (OK, perfil_seguidor_dict) — sucesso (retorna o perfil do seguidor atualizado).
    """
    if id_seguidor == id_alvo:
        return DADOS_INVALIDOS, None

    seguidor = _encontrar_perfil(id_seguidor)
    alvo = _encontrar_perfil(id_alvo)
    if seguidor is None or alvo is None:
        return NAO_ENCONTRADO, None

    seguindo = seguidor.setdefault("seguindo", [])
    seguidores = alvo.setdefault("seguidores", [])
    if id_alvo in seguindo:
        return CONFLITO, None

    seguindo.append(id_alvo)
    if id_seguidor not in seguidores:
        seguidores.append(id_seguidor)

    from controles import perfil_controler
    perfil_controler.salvar_perfis()
    return OK, seguidor


def Parar_de_Seguir(id_seguidor: int, id_alvo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Remover a relação de seguimento (seguidor deixa de seguir alvo).

    Descrição:
    - Verifica existência de perfis e presença da relação.
    - Remove id_alvo da lista 'seguindo' do seguidor e id_seguidor da lista 'seguidores' do alvo.
    - Marca perfis para gravação via perfil_controler.salvar_perfis().

    Parâmetros:
    - id_seguidor (int): id do perfil que deixará de seguir.
    - id_alvo (int): id do perfil alvo.

    Retorno:
    - (NAO_ENCONTRADO, None) — perfis inexistentes ou relação não existente.
    - (OK, perfil_seguidor_dict) — sucesso (retorna o perfil do seguidor atualizado).
    """
    seguidor = _encontrar_perfil(id_seguidor)
    alvo = _encontrar_perfil(id_alvo)
    if seguidor is None or alvo is None:
        return NAO_ENCONTRADO, None

    seguindo = seguidor.get("seguindo", [])
    if id_alvo not in seguindo:
        return NAO_ENCONTRADO, None

    try:
        seguindo.remove(id_alvo)
    except ValueError:
        pass

    if id_seguidor in alvo.get("seguidores", []):
        try:
            alvo["seguidores"].remove(id_seguidor)
        except ValueError:
            pass

    from controles import perfil_controler
    perfil_controler.salvar_perfis()
    return OK, seguidor


def Listar_Seguidores(id_perfil: int) -> Tuple[int, List[int]]:
    """
    Objetivo:
    - Retornar a lista de ids que seguem o perfil indicado.

    Descrição:
    - Recupera o perfil e devolve o campo 'seguidores' (lista de ids).
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
    return OK, perfil.get("seguidores", [])


def Listar_Seguindo(id_perfil: int) -> Tuple[int, List[int]]:
    """
    Objetivo:
    - Retornar a lista de ids que o perfil indicado está seguindo.

    Descrição:
    - Recupera o perfil e devolve o campo 'seguindo' (lista de ids).
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
    return OK, perfil.get("seguindo", [])


def Is_Seguindo(id_seguidor: int, id_alvo: int) -> bool:
    """
    Objetivo:
    - Verificar se um perfil segue outro.

    Descrição:
    - Retorna True se id_alvo estiver na lista 'seguindo' do perfil id_seguidor, False caso contrário.

    Parâmetros:
    - id_seguidor (int): id do perfil seguidor.
    - id_alvo (int): id do perfil alvo.

    Retorno:
    - bool: True se segue, False caso contrário (ou se perfis inexistentes).
    """
    seguidor = _encontrar_perfil(id_seguidor)
    if seguidor is None:
        return False
    return id_alvo in seguidor.get("seguindo", [])