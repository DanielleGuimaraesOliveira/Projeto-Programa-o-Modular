# controles/jogo_controler.py
"""Lógica de jogos: cadastro, listagem, busca, atualização e remoção.

Mantém as assinaturas públicas (Cadastrar_Jogo, Listar_Jogo, Busca_Jogo,
Atualizar_Jogo, Remover_Jogo) para compatibilidade com o restante do projeto.
"""
from typing import Dict, List, Optional, Tuple, Any
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO

from dados.database import jogos, salvar_jogos, perfis, salvar_perfis

__all__ = [
    "Cadastrar_Jogo", "Listar_Jogo", "Busca_Jogo", "Atualizar_Jogo", "Remover_Jogo"
]


def _proximo_id(jogos_list: List[Dict[str, Any]]) -> int:
    """Retorna próximo id seguro mesmo quando a lista está vazia."""
    return max((j.get("id", 0) for j in jogos_list), default=0) + 1


def _encontrar_por_id(id_jogo: int) -> Optional[Dict[str, Any]]:
    """Retorna o jogo com o id informado ou None se não existir."""
    return next((j for j in jogos if j.get("id") == id_jogo or j.get("id_jogo") == id_jogo), None)


def _titulo_ja_existe(titulo: str, ignorar_id: Optional[int] = None) -> bool:
    """Verifica existência de título (case-insensitive). Pode ignorar um id (útil na atualização)."""
    titulo_norm = (titulo or "").strip().lower()
    if not titulo_norm:
        return False
    return any(
        (j.get("id") != ignorar_id and j.get("id_jogo") != ignorar_id)
        and (j.get("titulo", "").strip().lower() == titulo_norm)
        for j in jogos
    )


def _validar_campos_obrigatorios(titulo: Optional[str], genero: Optional[str]) -> bool:
    """Valida presença dos campos obrigatórios titulo e genero."""
    return bool(titulo and titulo.strip()) and bool(genero and genero.strip())


def _validar_nota(nota: Optional[float]) -> bool:
    """Valida nota_geral (0.0 - 10.0) ou None."""
    if nota is None:
        return True
    try:
        n = float(nota)
    except Exception:
        return False
    return 0.0 <= n <= 10.0


def Cadastrar_Jogo(titulo: str, descricao: Optional[str], genero: str, nota_geral: Optional[float]) -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Cadastra um novo jogo. Verifica campos obrigatórios e unicidade de título (case-insensitive).
    Nota_geral é calculada pelas avaliações e será inicializada como 0.0.
    """
    if not titulo or not genero:
        return DADOS_INVALIDOS, None

    titulo_norm = titulo.strip().lower()
    if any((j.get("titulo") or "").strip().lower() == titulo_norm for j in jogos):
        return CONFLITO, None

    novo_id = max((j.get("id", 0) for j in jogos), default=0) + 1
    jogo = {
        "id": novo_id,
        "titulo": titulo,
        "descricao": descricao or "",
        "genero": genero,
        "nota_geral": 0.0
    }
    jogos.append(jogo)
    salvar_jogos()
    return OK, jogo


def Listar_Jogo() -> Tuple[int, List[Dict[str, Any]]]:
    """Retorna a lista completa de jogos."""
    return OK, jogos


def Busca_Jogo(id_jogo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Busca um jogo por id."""
    jogo = _encontrar_por_id(id_jogo)
    if jogo is None:
        return NAO_ENCONTRADO, None
    return OK, jogo


def Atualizar_Jogo(id_jogo: int, titulo: str, descricao: Optional[str], genero: str, nota_geral: Optional[float]) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Atualiza campos de um jogo existente.

    Assinatura: (id_jogo: int, titulo: str, descricao: str, genero: str, nota_geral: float)
    """
    jogo = _encontrar_por_id(id_jogo)
    if jogo is None:
        return NAO_ENCONTRADO, None

    if not _validar_campos_obrigatorios(titulo, genero):
        return DADOS_INVALIDOS, None

    if not _validar_nota(nota_geral):
        return DADOS_INVALIDOS, None

    if _titulo_ja_existe(titulo, ignorar_id=id_jogo):
        return CONFLITO, None

    jogo["titulo"] = titulo.strip()
    jogo["descricao"] = (descricao or "").strip()
    jogo["genero"] = genero.strip()
    jogo["nota_geral"] = float(nota_geral or jogo.get("nota_geral", 0.0))
    salvar_jogos()
    return OK, jogo


def Remover_Jogo(id_jogo: int) -> Tuple[int, Optional[None]]:
    """Remove um jogo por id e limpa referências em perfis (favoritos e biblioteca)."""
    jogo = _encontrar_por_id(id_jogo)
    if jogo is None:
        return NAO_ENCONTRADO, None

    # limpar referências em todos os perfis: favoritos e biblioteca
    for p in perfis:
        # remover favoritos
        if "favoritos" in p and id_jogo in p["favoritos"]:
            try:
                p["favoritos"].remove(id_jogo)
            except ValueError:
                pass
        # remover entradas da biblioteca relacionadas ao jogo
        if "biblioteca" in p:
            bibli = p["biblioteca"]
            nova_bibli = [e for e in bibli if e.get("jogo_id") != id_jogo]
            if len(nova_bibli) != len(bibli):
                p["biblioteca"] = nova_bibli
                # recalcula contadores derivados
                p["jogando"] = sum(1 for e in nova_bibli if e.get("status") == "jogando")
                p["jogados"] = sum(1 for e in nova_bibli if e.get("status") == "jogado")
                p["platinados"] = sum(1 for e in nova_bibli if e.get("status") == "platinado")

    jogos.remove(jogo)
    salvar_jogos()
    salvar_perfis()
    return OK, None
