# controles/perfil_controler.py
"""
Lógica de perfis: criação, busca, atualização e desativação.
Gerencia dados do usuário e garante integridade referencial.
"""
import os
import json
from typing import Tuple, Optional, Dict, Any, List

from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO
from dados.database import PERFIS_FILE, default_perfis

__all__ = [
    "Criar_Perfil", "Listar_Perfil", "Busca_Perfil", "Busca_Perfil_por_nome",
    "Atualizar_Dados", "Atualizar_Perfil", "Desativar_Conta", "Remover_Perfil",
    "Adicionar_Avaliacao", "Avaliar_Jogo", "Remover_Avaliacao",
    "Seguir_Perfil", "Parar_de_Seguir", "Listar_Seguidores", "Listar_Seguindo",
    # TAD funcs
    "_get_perfis", "salvar_perfis", "flush_perfis"
]

# --- TAD interno de perfis ---
_perfis: Optional[List[Dict[str, Any]]] = None
_perfis_dirty: bool = False

def _load_perfis() -> None:
    """
    Objetivo:
    - Carregar a lista de perfis do arquivo JSON para a TAD interna `_perfis`.

    Descrição:
    - Se `_perfis` já estiver carregado, não faz nada (lazy load).
    - Em caso de arquivo ausente, inicializa com `default_perfis` ou lista vazia.

    Parâmetros:
    - nenhum

    Retorno:
    - None (efeito colateral: popula a variável `_perfis`).
    """
    global _perfis
    if _perfis is not None:
        return
    if os.path.exists(PERFIS_FILE):
        try:
            with open(PERFIS_FILE, "r", encoding="utf-8") as f:
                _perfis = json.load(f)
        except Exception:
            _perfis = []
    else:
        _perfis = list(default_perfis) if default_perfis is not None else []

def _get_perfis() -> List[Dict[str, Any]]:
    """
    Objetivo:
    - Fornecer acesso à lista de perfis em memória.

    Descrição:
    - Garante que os perfis estejam carregados chamando `_load_perfis()` e retorna a lista.

    Parâmetros:
    - nenhum

    Retorno:
    - List[Dict]: lista de perfis em memória.
    """
    _load_perfis()
    return _perfis  # type: ignore

def salvar_perfis() -> None:
    """
    Objetivo:
    - Marcar perfis como modificados (dirty) para gravação posterior.

    Descrição:
    - Não realiza I/O; apenas seta flag interna `_perfis_dirty` para True.

    Parâmetros:
    - nenhum

    Retorno:
    - None (efeito colateral: marcação de dirty).
    """
    global _perfis_dirty
    _perfis_dirty = True

def flush_perfis() -> None:
    """
    Objetivo:
    - Persistir no JSON as modificações feitas em `_perfis`, se houver.

    Descrição:
    - Verifica flag `_perfis_dirty` e grava o arquivo `PERFIS_FILE` somente quando necessário.

    Parâmetros:
    - nenhum

    Retorno:
    - None (efeito colateral: gravação em disco).
    """
    global _perfis_dirty, _perfis
    if _perfis_dirty and _perfis is not None:
        os.makedirs(os.path.dirname(PERFIS_FILE), exist_ok=True)
        with open(PERFIS_FILE, "w", encoding="utf-8") as f:
            json.dump(_perfis, f, ensure_ascii=False, indent=2)
        _perfis_dirty = False

# --- helpers adaptados para usar _get_perfis() ---
def _proximo_id(perfis_list: List[Dict[str, Any]]) -> int:
    """
    Objetivo:
    - Calcular próximo id disponível para criação de novo perfil.

    Descrição:
    - Analisa os ids existentes e retorna max+1.

    Parâmetros:
    - perfis_list: lista de perfis a ser considerada.

    Retorno:
    - int: próximo id.
    """
    return max((p.get("id", 0) for p in perfis_list), default=0) + 1

def _encontrar_por_id(id_perfil: int) -> Optional[Dict[str, Any]]:
    """
    Objetivo:
    - Localizar um perfil na TAD por seu id.

    Parâmetros:
    - id_perfil (int): id procurado.

    Retorno:
    - Dict do perfil se encontrado, caso contrário None.
    """
    return next((p for p in _get_perfis() if p.get("id") == id_perfil), None)

def _nome_do_perfil(perfil: Dict[str, Any]) -> str:
    """
    Objetivo:
    - Padronizar extração do nome de usuário de um dicionário de perfil.

    Retorno:
    - str: nome limpo.
    """
    return (perfil.get("nome_usuario") or perfil.get("nome") or "").strip()

def _nome_ja_existe(nome: str, ignorar_id: Optional[int] = None) -> bool:
    """
    Objetivo:
    - Verificar se um nome de usuário já existe em outro perfil.

    Parâmetros:
    - nome (str): nome a verificar.
    - ignorar_id (Optional[int]): id a ser ignorado na verificação (útil em atualizações).

    Retorno:
    - bool: True se já existir outro perfil com o mesmo nome.
    """
    nome_norm = nome.strip().lower()
    return any(
        p.get("id") != ignorar_id and _nome_do_perfil(p).lower() == nome_norm
        for p in _get_perfis()
    )

def _validar_nome(nome: Optional[str]) -> bool:
    """
    Objetivo:
    - Validar se o campo nome é não vazio.

    Retorno:
    - bool
    """
    return bool(nome and nome.strip())

def _criar_estrutura_perfil(id_val: int, nome: str, descricao: Optional[str], avatar: Optional[str]) -> Dict[str, Any]:
    """
    Objetivo:
    - Construir o dicionário inicial de um novo perfil com todos os campos esperados.

    Parâmetros:
    - id_val (int): id do novo perfil.
    - nome (str), descricao (Optional[str]), avatar (Optional[str]).

    Retorno:
    - Dict com estrutura completa do perfil.
    """
    nome_clean = nome.strip()
    return {
        "id": id_val,
        "ID_perfil": id_val,
        "nome_usuario": nome_clean,
        "nome": nome_clean,
        "descricao": (descricao or "").strip(),
        "avatar": (avatar or "").strip(),
        "seguidores": [],
        "seguindo": [],
        "jogando": 0,
        "jogados": 0,
        "platinados": 0,
        "favoritos": [],
        "biblioteca": [],
        "avaliacoes": []
    }

def Criar_Perfil(nome: str, descricao: Optional[str] = None, avatar: Optional[str] = None) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Criar um novo perfil com nome de usuário único.

    Descrição:
    - Valida o nome, checa duplicidade, gera id, cria estrutura e marca perfis para gravação.

    Parâmetros:
    - nome (str): nome de usuário (obrigatório).
    - descricao (Optional[str]): texto opcional.
    - avatar (Optional[str]): URL/identificador opcional.

    Assertivas:
    - Pré: nome não vazio.
    - Pós: perfil inserido em `_perfis` e `_perfis_dirty` marcado.

    Retorno:
    - (OK, perfil_dict) — sucesso.
    - (DADOS_INVALIDOS, None) — nome inválido.
    - (CONFLITO, None) — nome já em uso.
    """
    if not _validar_nome(nome):
        return DADOS_INVALIDOS, None

    if _nome_ja_existe(nome):
        return CONFLITO, None

    perfis = _get_perfis()
    novo_id = _proximo_id(perfis)
    novo_perfil = _criar_estrutura_perfil(novo_id, nome, descricao, avatar)
    perfis.append(novo_perfil)
    salvar_perfis()
    return OK, novo_perfil

def Listar_Perfil() -> Tuple[int, List[Dict[str, Any]]]:
    """
    Objetivo:
    - Listar todos os perfis presentes em memória.

    Retorno:
    - (OK, lista_de_perfis)
    """
    return OK, _get_perfis()

def Busca_Perfil(id_perfil: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Recuperar um perfil por id.

    Parâmetros:
    - id_perfil (int)

    Retorno:
    - (OK, perfil_dict) ou (NAO_ENCONTRADO, None)
    """
    perfil = _encontrar_por_id(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None
    return OK, perfil

def Busca_Perfil_por_nome(nome: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Procurar perfil pelo nome de usuário (caso insensível).

    Parâmetros:
    - nome (str)

    Retorno:
    - (OK, perfil_dict) ou (DADOS_INVALIDOS, None) / (NAO_ENCONTRADO, None)
    """
    if not _validar_nome(nome):
        return DADOS_INVALIDOS, None
    nome_norm = nome.strip().lower()
    perfil = next((p for p in _get_perfis() if _nome_do_perfil(p).lower() == nome_norm), None)
    if perfil is None:
        return NAO_ENCONTRADO, None
    return OK, perfil

def Atualizar_Dados(id_perfil: int, nome: Optional[str] = None, descricao: Optional[str] = None, avatar: Optional[str] = None) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Atualizar campos editáveis do perfil (nome, descricao, avatar).

    Descrição:
    - Valida existência do perfil, valida nome se fornecido e checa conflitos.

    Parâmetros:
    - id_perfil (int)
    - nome (Optional[str])
    - descricao (Optional[str])
    - avatar (Optional[str])

    Assertivas:
    - Pré: perfil existe; se nome fornecido, não pode duplicar outro perfil.
    - Pós: perfil atualizado e marcado para gravação.

    Retorno:
    - (OK, perfil_dict) — sucesso.
    - (DADOS_INVALIDOS, None) — nome inválido.
    - (CONFLITO, None) — nome já usado.
    - (NAO_ENCONTRADO, None) — perfil inexistente.
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
        perfil["nome"] = nome.strip()

    if descricao is not None:
        perfil["descricao"] = descricao.strip()

    if avatar is not None:
        perfil["avatar"] = avatar.strip()

    salvar_perfis()
    return OK, perfil

def Desativar_Conta(id_perfil: int) -> Tuple[int, Optional[None]]:
    """
    Objetivo:
    - Desativar/remover um perfil do sistema (eliminação segura).

    Descrição:
    - Limpa referências de seguidores/seguindo, remove avaliações via avaliacao_controler
      e elimina o perfil da lista. Marca perfis para gravação.

    Parâmetros:
    - id_perfil (int)

    Retorno:
    - (OK, None) — sucesso.
    - (NAO_ENCONTRADO, None) — perfil inexistente.
    """
    perfil = _encontrar_por_id(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    # limpar seguidores/seguindo em outros perfis
    for p in _get_perfis():
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

    # remover avaliações deste perfil via avaliacao_controler (import local)
    from controles import avaliacao_controler
    # remover todas avaliações do usuário (avaliacao_controler tratará recalculo)
    avals_ids = [a.get("id") for a in list(avaliacao_controler.Listar_avaliacao()[1]) if a.get("id_perfil") == id_perfil]
    for aid in avals_ids:
        avaliacao_controler.Remover_avaliacao(aid)

    # remover o perfil
    perfis = _get_perfis()
    perfis.remove(perfil)
    salvar_perfis()
    return OK, None

def Remover_Perfil(id_perfil: int) -> Tuple[int, Optional[None]]:
    """
    Objetivo:
    - Interface para remoção de perfil (alias para Desativar_Conta).

    Parâmetros:
    - id_perfil (int)

    Retorno:
    - mesmo de Desativar_Conta
    """
    return Desativar_Conta(id_perfil)

# Wrappers de seguidores (delegam via import local para evitar circular)
def Seguir_Perfil(id_seguidor: int, id_alvo: int):
    """
    Objetivo:
    - Delegar operação de seguir a seguidores_controler evitando import circular.

    Parâmetros:
    - id_seguidor (int), id_alvo (int)

    Retorno:
    - devolve o resultado do seguidores_controler (código, payload)
    """
    from controles import seguidores_controler
    return seguidores_controler.Seguir_Perfil(id_seguidor, id_alvo)

def Parar_de_Seguir(id_seguidor: int, id_alvo: int):
    """
    Objetivo:
    - Delegar operação de parar de seguir a seguidores_controler.

    Retorno:
    - devolve o resultado do seguidores_controler (código, payload)
    """
    from controles import seguidores_controler
    return seguidores_controler.Parar_de_Seguir(id_seguidor, id_alvo)

def Listar_Seguidores(id_perfil: int):
    """
    Objetivo:
    - Delegar listagem de seguidores para o módulo de seguidores.

    Retorno:
    - (OK, lista) ou (NAO_ENCONTRADO, [])
    """
    from controles import seguidores_controler
    return seguidores_controler.Listar_Seguidores(id_perfil)

def Listar_Seguindo(id_perfil: int):
    """
    Objetivo:
    - Delegar listagem de perfis seguidos para o módulo de seguidores.

    Retorno:
    - (OK, lista) ou (NAO_ENCONTRADO, [])
    """
    from controles import seguidores_controler
    return seguidores_controler.Listar_Seguindo(id_perfil)

# Wrappers de avaliacao (delegam com signatures compatíveis)
def Avaliar_Jogo(id_perfil: int, id_jogo: int, nota: float, opiniao: Optional[str] = "") -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Delegar criação/edição de avaliação para avaliacao_controler com assinatura compatível.

    Parâmetros:
    - id_perfil, id_jogo, nota, opiniao

    Retorno:
    - devolve o resultado de avaliacao_controler.Avaliar_jogo
    """
    from controles import avaliacao_controler
    return avaliacao_controler.Avaliar_jogo(id_jogo, nota, opiniao, id_perfil)

def Adicionar_Avaliacao(id_perfil: int, id_jogo: int, nota: float, opiniao: Optional[str] = "") -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Objetivo:
    - Alias para Avaliar_Jogo (compatibilidade de API).

    Retorno:
    - mesmo retorno de Avaliar_Jogo
    """
    return Avaliar_Jogo(id_perfil, id_jogo, nota, opiniao)

def Remover_Avaliacao(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[None]]:
    """
    Objetivo:
    - Remover avaliação por par perfil/jogo (delegando a avaliacao_controler).

    Descrição:
    - Localiza a avaliação correspondente e executa remoção via avaliacao_controler.

    Parâmetros:
    - id_perfil (int), id_jogo (int)

    Retorno:
    - (OK, None) — removido com sucesso.
    - (NAO_ENCONTRADO, None) — avaliação inexistente.
    """
    from controles import avaliacao_controler
    # encontra avaliação por par perfil/jogo
    avals = avaliacao_controler.Listar_avaliacao()[1]
    a = next((x for x in avals if x.get("id_perfil") == id_perfil and x.get("id_jogo") == id_jogo), None)
    if a:
        return avaliacao_controler.Remover_avaliacao(a["id"])
    return NAO_ENCONTRADO, None