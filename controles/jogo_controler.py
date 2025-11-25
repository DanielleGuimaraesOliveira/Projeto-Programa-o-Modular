# controles/jogo_controler.py
from typing import Dict, List, Optional, Tuple, Any
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO
from dados.database import jogos, salvar_jogos, perfis, salvar_perfis, avaliacoes, salvar_avaliacoes

__all__ = [
    "Cadastrar_Jogo", "Listar_Jogo", "Busca_Jogo", "Atualizar_Jogo", "Remover_Jogo"
]

def _encontrar_por_id(id_jogo: int) -> Optional[Dict[str, Any]]:
    return next((j for j in jogos if j.get("id") == id_jogo), None)

def _titulo_ja_existe(titulo: str, ignorar_id: Optional[int] = None) -> bool:
    titulo_norm = (titulo or "").strip().lower()
    if not titulo_norm:
        return False
    return any(
        j.get("id") != ignorar_id and (j.get("titulo", "").strip().lower() == titulo_norm)
        for j in jogos
    )

def _validar_campos_obrigatorios(titulo: Optional[str], genero: Optional[str]) -> bool:
    return bool(titulo and titulo.strip()) and bool(genero and genero.strip())

def Cadastrar_Jogo(titulo: str, descricao: Optional[str], genero: str, nota_geral: Optional[float]) -> Tuple[int, Optional[Dict[str, Any]]]:
    if not _validar_campos_obrigatorios(titulo, genero):
        return DADOS_INVALIDOS, None

    if _titulo_ja_existe(titulo):
        return CONFLITO, None

    novo_id = max((j.get("id", 0) for j in jogos), default=0) + 1
    
    # Nota geral é calculada automaticamente, inicializa com 0.0
    jogo = {
        "id": novo_id,
        "titulo": titulo.strip(),
        "descricao": (descricao or "").strip(),
        "genero": genero.strip(),
        "nota_geral": 0.0 
    }
    jogos.append(jogo)
    salvar_jogos()
    return OK, jogo

def Listar_Jogo() -> Tuple[int, List[Dict[str, Any]]]:
    return OK, jogos

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
    # Nota geral NÃO é alterada manualmente aqui
    
    salvar_jogos()
    return OK, jogo

def Remover_Jogo(id_jogo: int) -> Tuple[int, Optional[None]]:
    jogo = _encontrar_por_id(id_jogo)
    if jogo is None:
        return NAO_ENCONTRADO, None

    # 1. Remover avaliações deste jogo (Cascata)
    global avaliacoes
    tamanho_inicial = len(avaliacoes)
    avaliacoes[:] = [a for a in avaliacoes if a.get("id_jogo") != id_jogo]
    
    if len(avaliacoes) != tamanho_inicial:
        salvar_avaliacoes()

    # 2. Remover referências nos perfis (Biblioteca e Favoritos)
    perfis_alterados = False
    for p in perfis:
        alterou_perfil = False
        
        # Remove dos favoritos
        if "favoritos" in p and id_jogo in p["favoritos"]:
            try:
                p["favoritos"].remove(id_jogo)
                alterou_perfil = True
            except ValueError:
                pass
        
        # Remove da biblioteca
        if "biblioteca" in p:
            bibli = p["biblioteca"]
            nova_bibli = [e for e in bibli if e.get("id_jogo") != id_jogo]
            
            if len(nova_bibli) != len(bibli):
                p["biblioteca"] = nova_bibli
                # Recalcula contadores obrigatórios
                p["jogando"] = sum(1 for e in nova_bibli if e.get("status") == "jogando")
                p["jogados"] = sum(1 for e in nova_bibli if e.get("status") == "jogado")
                p["platinados"] = sum(1 for e in nova_bibli if e.get("status") == "platinado")
                alterou_perfil = True
        
        if alterou_perfil:
            perfis_alterados = True

    if perfis_alterados:
        salvar_perfis()
    
    jogos.remove(jogo)
    salvar_jogos()
    return OK, None