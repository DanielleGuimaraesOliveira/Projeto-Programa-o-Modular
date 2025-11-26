# controles/jogo_controler.py
import os
import json
from typing import Dict, List, Optional, Tuple, Any
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO
from dados.database import JOGOS_FILE

__all__ = [
    "Cadastrar_Jogo", "Listar_Jogo", "Busca_Jogo", "Atualizar_Jogo", "Remover_Jogo",
    "_get_jogos", "salvar_jogos", "flush_jogos"
]

# --- TAD interno de jogos ---
_jogos: Optional[List[Dict[str, Any]]] = None
_jogos_dirty: bool = False

def _load_jogos() -> None:
    global _jogos
    if _jogos is not None:
        return
    if os.path.exists(JOGOS_FILE):
        try:
            with open(JOGOS_FILE, "r", encoding="utf-8") as f:
                _jogos = json.load(f)
        except Exception:
            _jogos = []
    else:
        _jogos = []

def _get_jogos() -> List[Dict[str, Any]]:
    _load_jogos()
    return _jogos  # type: ignore

def salvar_jogos() -> None:
    global _jogos_dirty
    _jogos_dirty = True

def flush_jogos() -> None:
    global _jogos_dirty, _jogos
    if _jogos_dirty and _jogos is not None:
        os.makedirs(os.path.dirname(JOGOS_FILE), exist_ok=True)
        with open(JOGOS_FILE, "w", encoding="utf-8") as f:
            json.dump(_jogos, f, ensure_ascii=False, indent=2)
        _jogos_dirty = False

def _encontrar_por_id(id_jogo: int) -> Optional[Dict[str, Any]]:
    return next((j for j in _get_jogos() if j.get("id") == id_jogo), None)

def _titulo_ja_existe(titulo: str, ignorar_id: Optional[int] = None) -> bool:
    titulo_norm = (titulo or "").strip().lower()
    if not titulo_norm:
        return False
    return any(
        j.get("id") != ignorar_id and (j.get("titulo", "").strip().lower() == titulo_norm)
        for j in _get_jogos()
    )

def _validar_campos_obrigatorios(titulo: Optional[str], genero: Optional[str]) -> bool:
    return bool(titulo and titulo.strip()) and bool(genero and genero.strip())

def Cadastrar_Jogo(titulo: str, descricao: Optional[str], genero: str, nota_geral: Optional[float]) -> Tuple[int, Optional[Dict[str, Any]]]:
    if not _validar_campos_obrigatorios(titulo, genero):
        return DADOS_INVALIDOS, None

    if _titulo_ja_existe(titulo):
        return CONFLITO, None

    novo_id = max((j.get("id", 0) for j in _get_jogos()), default=0) + 1
    
    jogo = {
        "id": novo_id,
        "titulo": titulo.strip(),
        "descricao": (descricao or "").strip(),
        "genero": genero.strip(),
        "nota_geral": 0.0 
    }
    _get_jogos().append(jogo)
    salvar_jogos()
    return OK, jogo

def Listar_Jogo() -> Tuple[int, List[Dict[str, Any]]]:
    return OK, _get_jogos()

def Busca_Jogo(id_jogo: int) -> Tuple[int, Optional[Dict[str, Any]]]:
    jogo = _encontrar_por_id(id_jogo)
    if jogo is None:
        return NAO_ENCONTRADO, None
    return OK, jogo

def Atualizar_Jogo(id_jogo: int, titulo: str, descricao: Optional[str], genero: str, nota_geral: Optional[float]) -> Tuple[int, Optional[Dict[str, Any]]]:
    jogo = _encontrar_por_id(id_jogo)
    if jogo is None:
        return NAO_ENCONTRADO, None

    if not _validar_campos_obrigatorios(titulo, genero):
        return DADOS_INVALIDOS, None

    if _titulo_ja_existe(titulo, ignorar_id=id_jogo):
        return CONFLITO, None

    jogo["titulo"] = titulo.strip()
    jogo["descricao"] = (descricao or "").strip()
    jogo["genero"] = genero.strip()
    salvar_jogos()
    return OK, jogo

def Remover_Jogo(id_jogo: int) -> Tuple[int, Optional[None]]:
    jogo = _encontrar_por_id(id_jogo)
    if jogo is None:
        return NAO_ENCONTRADO, None

    # atualiza avaliacoes via avaliacao_controler (import local)
    from controles import avaliacao_controler
    # remove avaliações do jogo
    avals = list(avaliacao_controler.Listar_avaliacao()[1])
    alvo_ids = [a["id"] for a in avals if a.get("id_jogo") == id_jogo]
    for aid in alvo_ids:
        avaliacao_controler.Remover_avaliacao(aid)

    # limpar referências em perfis (import local)
    from controles import perfil_controler
    perfis = perfil_controler._get_perfis()
    perfis_alterados = False
    for p in perfis:
        alterou = False
        if "favoritos" in p and id_jogo in p["favoritos"]:
            try:
                p["favoritos"].remove(id_jogo)
                alterou = True
            except ValueError:
                pass
        if "biblioteca" in p:
            bibli = p["biblioteca"]
            nova_bibli = [e for e in bibli if e.get("id_jogo") != id_jogo]
            if len(nova_bibli) != len(bibli):
                p["biblioteca"] = nova_bibli
                p["jogando"] = sum(1 for e in nova_bibli if e.get("status") == "jogando")
                p["jogados"] = sum(1 for e in nova_bibli if e.get("status") == "jogado")
                p["platinados"] = sum(1 for e in nova_bibli if e.get("status") == "platinado")
                alterou = True
        if alterou:
            perfis_alterados = True

    if perfis_alterados:
        perfil_controler.salvar_perfis()

    _get_jogos().remove(jogo)
    salvar_jogos()
    return OK, None