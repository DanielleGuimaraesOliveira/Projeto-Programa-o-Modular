# controles/perfil_controler.py
"""Lógica de perfis: criação, busca, atualização e avaliações.

Agora o perfil contém os campos esperados pelo diagrama:
- nome_usuario, descricao, avatar, seguidores, seguindo,
  jogando, jogados, platinados, id (ID_perfil como alias).
Mantém compatibilidade com chaves antigas ('nome') e com as funções
anteriores (Atualizar_Perfil, Remover_Perfil) como aliases.
"""
from typing import Dict, List, Optional, Tuple, Any

from dados.database import perfis, salvar_perfis
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO

# delega funções de biblioteca para o módulo especializado
# Tentamos suportar implementações diferentes sem quebrar a importação.
try:
    # implementação onde as funções de avaliação já existem com esses nomes
    from controles.biblioteca_controler import Adicionar_Avaliacao, Remover_Avaliacao  # type: ignore
except (ImportError, ModuleNotFoundError):
    try:
        # implementação alternativa que usa nomes centrados em "biblioteca"
        from controles.biblioteca_controler import Adicionar_Jogo, Remover_Jogo  # type: ignore
        # criamos aliases esperados pelo restante do código
        Adicionar_Avaliacao = Adicionar_Jogo  # type: ignore
        Remover_Avaliacao = Remover_Jogo  # type: ignore
    except (ImportError, ModuleNotFoundError):
        # fallback: stubs que levantam erro claro apenas quando chamados
        def _biblioteca_missing_stub(*args, **kwargs):
            raise ModuleNotFoundError(
                "Módulo 'controles.biblioteca_controler' não exporta funções de avaliação/biblioteca esperadas. "
                "Crie 'Adicionar_Avaliacao'/'Remover_Avaliacao' ou 'Adicionar_Jogo'/'Remover_Jogo'."
            )
        Adicionar_Avaliacao = _biblioteca_missing_stub  # type: ignore
        Remover_Avaliacao = _biblioteca_missing_stub  # type: ignore

# Se houver um módulo de avaliações separado, importe suas funções (opcional).
try:
    from controles.avaliacao_controler import Avaliar_Jogo, Remover_Avaliacao as Remover_Avaliacao_de_avaliacao  # type: ignore
except (ImportError, ModuleNotFoundError):
    # não é obrigatório — continuamos funcionando com as funções da biblioteca
    Avaliar_Jogo = None  # type: ignore
    Remover_Avaliacao_de_avaliacao = None  # type: ignore

__all__ = [
    "Criar_Perfil", "Listar_Perfil", "Busca_Perfil", "Busca_Perfil_por_nome",
    "Atualizar_Dados", "Atualizar_Perfil", "Desativar_Conta", "Remover_Perfil",
    "Avaliar_Jogo", "Remover_Avaliacao", "Seguir_Perfil", "Parar_de_Seguir",
    "Listar_Seguidores", "Listar_Seguindo"
]


def _proximo_id(perfis_list: List[Dict[str, Any]]) -> int:
    """Retorna o próximo id disponível (seguro mesmo com lista vazia)."""
    return max((p.get("id", 0) for p in perfis_list), default=0) + 1


def _encontrar_por_id(id_perfil: int) -> Optional[Dict[str, Any]]:
    """Retorna o perfil com o id informado ou None se não existir."""
    return next((p for p in perfis if p.get("id") == id_perfil), None)


def _nome_do_perfil(perfil: Dict[str, Any]) -> str:
    """Retorna o nome efetivo do perfil (compatibilidade: nome_usuario ou nome)."""
    return (perfil.get("nome_usuario") or perfil.get("nome") or "").strip()


def _nome_ja_existe(nome: str, ignorar_id: Optional[int] = None) -> bool:
    """Verifica existência de nome (case-insensitive). Pode ignorar um id."""
    nome_norm = nome.strip().lower()
    return any(
        p.get("id") != ignorar_id and _nome_do_perfil(p).lower() == nome_norm
        for p in perfis
    )


def _validar_nome(nome: Optional[str]) -> bool:
    """Valida presença e conteúdo do nome."""
    return bool(nome and nome.strip())


def _criar_estrutura_perfil(id_val: int, nome: str, descricao: Optional[str], avatar: Optional[str]) -> Dict[str, Any]:
    """Cria a estrutura de dicionário do perfil com todos os campos do diagrama."""
    nome_clean = nome.strip()
    descricao_clean = (descricao or "").strip()
    avatar_clean = (avatar or "").strip()
    perfil = {
        "id": id_val,
        "ID_perfil": id_val,              # alias explicito
        "nome_usuario": nome_clean,
        "nome": nome_clean,               # compatibilidade com código legado
        "descricao": descricao_clean,
        "avatar": avatar_clean,
        "seguidores": [],                 # lista de ids de perfis que seguem
        "seguindo": [],                   # lista de ids de perfis seguidos
        "jogando": 0,
        "jogados": 0,
        "platinados": 0,
        "favoritos": [],
        "biblioteca": []
    }
    return perfil


def Criar_Perfil(nome: str, descricao: Optional[str] = None, avatar: Optional[str] = None) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Cria um novo perfil caso o nome seja válido e não exista."""
    if not _validar_nome(nome):
        return DADOS_INVALIDOS, None

    if _nome_ja_existe(nome):
        return CONFLITO, None

    novo_id = _proximo_id(perfis)
    novo_perfil = _criar_estrutura_perfil(novo_id, nome, descricao, avatar)
    perfis.append(novo_perfil)
    salvar_perfis()
    return OK, novo_perfil


def Listar_Perfil() -> Tuple[int, List[Dict[str, Any]]]:
    """Retorna todos os perfis cadastrados."""
    return OK, perfis


def Busca_Perfil(id_perfil: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Busca um perfil pelo ID (id ou ID_perfil)."""
    perfil = _encontrar_por_id(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None
    return OK, perfil


def Busca_Perfil_por_nome(nome: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Busca um perfil pelo nome (case-insensitive)."""
    if not _validar_nome(nome):
        return DADOS_INVALIDOS, None

    nome_norm = nome.strip().lower()
    perfil = next((p for p in perfis if _nome_do_perfil(p).lower() == nome_norm), None)
    if perfil is None:
        return NAO_ENCONTRADO, None
    return OK, perfil


def Atualizar_Dados(id_perfil: int, nome: Optional[str] = None, descricao: Optional[str] = None, avatar: Optional[str] = None) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Atualiza os campos fornecidos do perfil e salva as mudanças.
    - nome: se fornecido, valida não vazio e sem conflito com outro perfil.
    - descricao, avatar: se fornecidos, substituem/limpam o valor atual.
    """
    perfil = _encontrar_por_id(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    if nome is not None:
        if not _validar_nome(nome):
            return DADOS_INVALIDOS, None
        if _nome_ja_existe(nome, ignorar_id=id_perfil):
            return CONFLITO, None
        perfil["nome_usuario"] = nome.strip()
        perfil["nome"] = nome.strip()  # compatibilidade

    if descricao is not None:
        perfil["descricao"] = descricao.strip()

    if avatar is not None:
        perfil["avatar"] = avatar.strip()

    salvar_perfis()
    return OK, perfil


def Atualizar_Perfil(id_perfil: int, nome: Optional[str] = None, descricao: Optional[str] = None, avatar: Optional[str] = None) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Atualiza os dados do perfil."""
    return Atualizar_Dados(id_perfil, nome, descricao, avatar)


def Desativar_Conta(id_perfil: int) -> Tuple[int, Optional[None]]:
    """Desativa/Remove um perfil e limpa referências em outros perfis."""
    perfil = _encontrar_por_id(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    # remover referências em outros perfis (seguidores / seguindo)
    for p in list(perfis):  # itera sobre cópia para segurança
        if p.get("id") == id_perfil:
            continue
        if "seguindo" in p and id_perfil in p["seguindo"]:
            try:
                p["seguindo"].remove(id_perfil)
            except ValueError:
                pass
        if "seguidores" in p and id_perfil in p["seguidores"]:
            try:
                p["seguidores"].remove(id_perfil)
            except ValueError:
                pass

    # agora remove o perfil da lista
    perfis.remove(perfil)
    salvar_perfis()
    return OK, None



def Remover_Perfil(id_perfil: int) -> Tuple[int, Optional[None]]:

    return Desativar_Conta(id_perfil)


def Seguir_Perfil(id_seguidor: int, id_alvo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Faz id_seguidor seguir id_alvo. Atualiza listas 'seguindo' e 'seguidores'."""
    if id_seguidor == id_alvo:
        return DADOS_INVALIDOS, None

    seguidor = _encontrar_por_id(id_seguidor)
    alvo = _encontrar_por_id(id_alvo)
    if seguidor is None or alvo is None:
        return NAO_ENCONTRADO, None

    if id_alvo in seguidor.get("seguindo", []):
        return CONFLITO, None

    seguidor.setdefault("seguindo", []).append(id_alvo)
    alvo.setdefault("seguidores", []).append(id_seguidor)
    salvar_perfis()
    return OK, seguidor


def Parar_de_Seguir(id_seguidor: int, id_alvo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Faz id_seguidor parar de seguir id_alvo."""
    seguidor = _encontrar_por_id(id_seguidor)
    alvo = _encontrar_por_id(id_alvo)
    if seguidor is None or alvo is None:
        return NAO_ENCONTRADO, None

    if id_alvo not in seguidor.get("seguindo", []):
        return NAO_ENCONTRADO, None

    seguidor["seguindo"].remove(id_alvo)
    if id_seguidor in alvo.get("seguidores", []):
        alvo["seguidores"].remove(id_seguidor)
    salvar_perfis()
    return OK, seguidor


def Listar_Seguidores(id_perfil: int) -> Tuple[int, List[int]]:
    perfil = _encontrar_por_id(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, []
    return OK, perfil.get("seguidores", [])


def Listar_Seguindo(id_perfil: int) -> Tuple[int, List[int]]:
    perfil = _encontrar_por_id(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, []
    return OK, perfil.get("seguindo", [])
