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
from controles.biblioteca_controler import Adicionar_Avaliacao, Remover_Avaliacao
from controles.avaliacao_controler import Avaliar_Jogo, Remover_Avaliacao  # novo: funções de avaliação separadas

__all__ = [
    "Criar_Perfil", "Listar_Perfil", "Busca_Perfil", "Busca_Perfil_por_nome",
    "Atualizar_Dados", "Atualizar_Perfil", "Desativar_Conta", "Remover_Perfil",
    "Avaliar_Jogo", "Remover_Avaliacao"
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
    """Desativa/Remove um perfil e salva as alterações na base."""
    perfil = _encontrar_por_id(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None
    perfis.remove(perfil)
    salvar_perfis()
    return OK, None



def Remover_Perfil(id_perfil: int) -> Tuple[int, Optional[None]]:

    return Desativar_Conta(id_perfil)
