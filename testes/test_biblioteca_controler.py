import pytest
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO
import dados.database as db
import controles.biblioteca_controler as bib_ctrl
import controles.perfil_controler as perfil_ctrl
import controles.jogo_controler as jogo_ctrl

@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    monkeypatch.setattr(db, "salvar_perfis", lambda: True)
    monkeypatch.setattr(db, "salvar_jogos", lambda: True)
    db.perfis.clear()
    db.jogos.clear()
    db.jogos.extend([
        {"id": 1, "titulo": "God of War", "genero": "Ação", "descricao": "", "nota_geral": 0.0},
        {"id": 2, "titulo": "Portal 2", "genero": "Puzzle", "descricao": "", "nota_geral": 0.0},
    ])
    yield

def test_adicionar_jogo_biblioteca():
    _, p = perfil_ctrl.Criar_Perfil("u1")
    code, _ = bib_ctrl.Adicionar_Jogo(p["id"], 1, "jogado")
    assert code == OK
    code_conf, _ = bib_ctrl.Adicionar_Jogo(p["id"], 1, "jogado")
    assert code_conf == CONFLITO

def test_adicionar_jogo_status_invalido():
    _, p = perfil_ctrl.Criar_Perfil("u2")
    code, _ = bib_ctrl.Adicionar_Jogo(p["id"], 1, "invalid")
    assert code == DADOS_INVALIDOS

def test_atualizar_status():
    _, p = perfil_ctrl.Criar_Perfil("u3")
    bib_ctrl.Adicionar_Jogo(p["id"], 2, "jogando")
    code_up, perfil = bib_ctrl.Atualizar_Status_Jogo(p["id"], 2, "platinado")
    assert code_up == OK
    assert perfil["platinados"] == 1

def test_remover_jogo_biblioteca():
    _, p = perfil_ctrl.Criar_Perfil("u4")
    bib_ctrl.Adicionar_Jogo(p["id"], 1, "jogado")
    code_rm, _ = bib_ctrl.Remover_Jogo(p["id"], 1)
    assert code_rm == OK
    code_rm_again, _ = bib_ctrl.Remover_Jogo(p["id"], 1)
    assert code_rm_again == NAO_ENCONTRADO

def test_listar_por_status():
    _, p = perfil_ctrl.Criar_Perfil("u5")
    bib_ctrl.Adicionar_Jogo(p["id"], 1, "jogando")
    bib_ctrl.Adicionar_Jogo(p["id"], 2, "jogado")
    code, lista = bib_ctrl.Listar_Biblioteca_por_status(p["id"], "jogando")
    assert code == OK and len(lista) == 1