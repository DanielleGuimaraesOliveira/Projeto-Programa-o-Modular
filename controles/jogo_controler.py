# controllers/jogo_controller.py
from dados.database import jogos, salvar_jogos
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO

def Cadastrar_Jogo(titulo, descricao, genero):
    if not titulo or not genero:
        return DADOS_INVALIDOS, None

    if any(j["titulo"].lower() == titulo.lower() for j in jogos):
        return CONFLITO, None

    novo_id = max([j["id"] for j in jogos]) + 1 if jogos else 1
    novo_jogo = {
        "id": novo_id,
        "titulo": titulo,
        "descricao": descricao or "",
        "genero": genero,
        "nota_geral": 0.0
    }
    jogos.append(novo_jogo)
    salvar_jogos()
    return OK, novo_jogo


def Listar_Jogo():
    return OK, jogos


def Busca_Jogo(id_jogo):
    jogo = next((j for j in jogos if j["id"] == id_jogo), None)
    if not jogo:
        return NAO_ENCONTRADO, None
    return OK, jogo


def Atualizar_Jogo(id_jogo, titulo, descricao, genero):
    jogo = next((j for j in jogos if j["id"] == id_jogo), None)
    if not jogo:
        return NAO_ENCONTRADO, None

    if not titulo or not genero:
        return DADOS_INVALIDOS, None

    jogo["titulo"] = titulo
    jogo["descricao"] = descricao or ""
    jogo["genero"] = genero
    salvar_jogos()
    return OK, jogo


def Remover_Jogo(id_jogo):
    global jogos
    jogo = next((j for j in jogos if j["id"] == id_jogo), None)
    if not jogo:
        return NAO_ENCONTRADO, None
    jogos.remove(jogo)
    salvar_jogos()
    return OK, None
