# controles/perfil_controler.py
"""
Lógica de perfis: criação, busca, atualização e desativação.
Gerencia dados do usuário e garante integridade referencial.
"""
from typing import Tuple, Optional, Dict, Any, List
# Importa módulos relacionados para limpeza e delegação
from controles import avaliacao_controler
from controles import seguidores_controler as seguidores_ctrl

# Importa avaliacoes/salvar para limpeza direta ao deletar perfil
from dados.database import perfis, salvar_perfis, avaliacoes, salvar_avaliacoes
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO

__all__ = [
    "Criar_Perfil", "Listar_Perfil", "Busca_Perfil", "Busca_Perfil_por_nome",
    "Atualizar_Dados", "Atualizar_Perfil", "Desativar_Conta", "Remover_Perfil",
    "Adicionar_Avaliacao", "Avaliar_Jogo", "Remover_Avaliacao", 
    "Seguir_Perfil", "Parar_de_Seguir", "Listar_Seguidores", "Listar_Seguindo"
]

def _proximo_id(perfis_list: List[Dict[str, Any]]) -> int:
    return max((p.get("id", 0) for p in perfis_list), default=0) + 1

def _encontrar_por_id(id_perfil: int) -> Optional[Dict[str, Any]]:
    return next((p for p in perfis if p.get("id") == id_perfil), None)

def _nome_do_perfil(perfil: Dict[str, Any]) -> str:
    return (perfil.get("nome_usuario") or perfil.get("nome") or "").strip()

def _nome_ja_existe(nome: str, ignorar_id: Optional[int] = None) -> bool:
    nome_norm = nome.strip().lower()
    return any(
        p.get("id") != ignorar_id and _nome_do_perfil(p).lower() == nome_norm
        for p in perfis
    )

def _validar_nome(nome: Optional[str]) -> bool:
    return bool(nome and nome.strip())

def _criar_estrutura_perfil(id_val: int, nome: str, descricao: Optional[str], avatar: Optional[str]) -> Dict[str, Any]:
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
        "biblioteca": []
    }

def Criar_Perfil(nome: str, descricao: Optional[str] = None, avatar: Optional[str] = None) -> Tuple[int, Optional[Dict[str, Any]]]:
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
    return OK, perfis

def Busca_Perfil(id_perfil: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    perfil = _encontrar_por_id(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None
    return OK, perfil

def Busca_Perfil_por_nome(nome: str) -> Tuple[int, Optional[Dict[str, Any]]]:
    if not _validar_nome(nome):
        return DADOS_INVALIDOS, None
    nome_norm = nome.strip().lower()
    perfil = next((p for p in perfis if _nome_do_perfil(p).lower() == nome_norm), None)
    if perfil is None:
        return NAO_ENCONTRADO, None
    return OK, perfil

def Atualizar_Dados(id_perfil: int, nome: Optional[str] = None, descricao: Optional[str] = None, avatar: Optional[str] = None) -> Tuple[int, Optional[Dict[str, Any]]]:
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

def Atualizar_Perfil(id_perfil: int, nome: Optional[str] = None, descricao: Optional[str] = None, avatar: Optional[str] = None) -> Tuple[int, Optional[Dict[str, Any]]]:
    return Atualizar_Dados(id_perfil, nome, descricao, avatar)

def Desativar_Conta(id_perfil: int) -> Tuple[int, Optional[None]]:
    """Desativa perfil, remove referências de seguidores e AVALIAÇÕES feitas pelo usuário."""
    perfil = _encontrar_por_id(id_perfil)
    if perfil is None:
        return NAO_ENCONTRADO, None

    # 1. Limpar seguidores/seguindo em outros perfis
    for p in perfis:
        alterado = False
        if p.get("id") == id_perfil:
            continue
        if "seguindo" in p and id_perfil in p["seguindo"]:
            try:
                p["seguindo"].remove(id_perfil)
                alterado = True
            except ValueError:
                pass
        if "seguidores" in p and id_perfil in p["seguidores"]:
            try:
                p["seguidores"].remove(id_perfil)
                alterado = True
            except ValueError:
                pass
    
    # 2. FIX: Remover avaliações feitas por este perfil
    # Isso garante que a média dos jogos seja recalculada sem o "fantasma"
    global avaliacoes
    # Identifica IDs das avaliações do usuário para removê-las
    avaliacoes_do_usuario = [a for a in avaliacoes if a.get("id_perfil") == id_perfil]
    
    # Remove as avaliações da lista global
    for av in avaliacoes_do_usuario:
        # Usa o controller de avaliação para garantir recálculo da nota do jogo
        avaliacao_controler.Remover_avaliacao(av["id"])

    # 3. Remover o perfil
    perfis.remove(perfil)
    salvar_perfis()
    return OK, None

def Remover_Perfil(id_perfil: int) -> Tuple[int, Optional[None]]:
    return Desativar_Conta(id_perfil)

# --- WRAPPERS DE SEGUIDORES (Delegação direta) ---
def Seguir_Perfil(id_seguidor: int, id_alvo: int):
    return seguidores_ctrl.Seguir_Perfil(id_seguidor, id_alvo)

def Parar_de_Seguir(id_seguidor: int, id_alvo: int):
    return seguidores_ctrl.Parar_de_Seguir(id_seguidor, id_alvo)

def Listar_Seguidores(id_perfil: int):
    return seguidores_ctrl.Listar_Seguidores(id_perfil)

def Listar_Seguindo(id_perfil: int):
    return seguidores_ctrl.Listar_Seguindo(id_perfil)

# --- WRAPPERS DE AVALIAÇÃO (Correção de Assinatura) ---
def Avaliar_Jogo(id_perfil: int, id_jogo: int, nota: float, opiniao: Optional[str] = "") -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Wrapper corrigido.
    Modulo Avaliação espera: Avaliar_jogo(id_jogo, score, descricao, id_perfil)
    """
    return avaliacao_controler.Avaliar_jogo(id_jogo, nota, opiniao, id_perfil)

def Adicionar_Avaliacao(id_perfil: int, id_jogo: int, nota: float, opiniao: Optional[str] = "") -> Tuple[int, Optional[Dict[str, Any]]]:
    return Avaliar_Jogo(id_perfil, id_jogo, nota, opiniao)

def Remover_Avaliacao(id_perfil: int, id_jogo: int) -> Tuple[int, Optional[None]]:
    """
    Wrapper corrigido.
    O módulo Avaliação remove por ID da avaliação. 
    Aqui precisamos descobrir o ID da avaliação baseada no par (perfil, jogo).
    """
    # Busca a avaliação correspondente na lista global
    avaliacao = next((a for a in avaliacoes if a.get("id_perfil") == id_perfil and a.get("id_jogo") == id_jogo), None)
    
    if avaliacao:
        return avaliacao_controler.Remover_avaliacao(avaliacao["id"])
    else:
        return NAO_ENCONTRADO, None