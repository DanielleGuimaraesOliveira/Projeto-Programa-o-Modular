import pytest
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO
import dados.database as db
import controles.jogo_controler as jogo_ctrl

@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    monkeypatch.setattr(db, "salvar_jogos", lambda: True)
    db.jogos.clear()
    db.jogos.extend([
        {"id": 1, "titulo": "God of War", "genero": "Ação", "descricao": "", "nota_geral": 0.0},
        {"id": 2, "titulo": "Portal 2", "genero": "Puzzle", "descricao": "", "nota_geral": 0.0},
    ])
    yield

def test_cadastrar_jogo_sucesso():
    code, jogo = jogo_ctrl.Cadastrar_Jogo("Hades", "rogue-lite", "Ação", 0.0)
    assert code == OK
    assert jogo["titulo"] == "Hades"
    assert any(j["titulo"] == "Hades" for j in db.jogos)

def test_cadastrar_jogo_campos_invalidos():
    code, _ = jogo_ctrl.Cadastrar_Jogo("", None, "", None)
    assert code == DADOS_INVALIDOS

def test_cadastrar_jogo_conflito_titulo():
    code, _ = jogo_ctrl.Cadastrar_Jogo("God of War", None, "Ação", None)
    assert code == CONFLITO

def test_busca_atualiza_remove_jogo():
    code, jogo = jogo_ctrl.Busca_Jogo(1)
    assert code == OK and jogo["titulo"] == "God of War"

    code_up, jogo_up = jogo_ctrl.Atualizar_Jogo(1, "God of War Remake", "nova", "Ação", 9.5)
    assert code_up == OK
    assert jogo_up["titulo"] == "God of War Remake"

    code_rm, _ = jogo_ctrl.Remover_Jogo(1)
    assert code_rm == OK
    code_busca, _ = jogo_ctrl.Busca_Jogo(1)
    assert code_busca == NAO_ENCONTRADO