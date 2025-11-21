import pytest
from utils.codigos import OK, NAO_ENCONTRADO, CONFLITO
import dados.database as db
import controles.favoritos_controler as fav_ctrl
import controles.perfil_controler as perfil_ctrl

@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    monkeypatch.setattr(db, "salvar_perfis", lambda: True)
    monkeypatch.setattr(db, "salvar_jogos", lambda: True)
    db.perfis.clear()
    db.jogos.clear()
    db.jogos.extend([
        {"id": 1, "titulo": "God of War", "genero": "Ação", "descricao": "", "nota_geral": 0.0},
    ])
    yield

def test_favoritar_desfavoritar_listar():
    _, p = perfil_ctrl.Criar_Perfil("favuser")
    code, _ = fav_ctrl.Favoritar_Jogo(p["id"], 1)
    assert code == OK
    # duplicação
    code_dup, _ = fav_ctrl.Favoritar_Jogo(p["id"], 1)
    assert code_dup == CONFLITO
    # listar
    code_list, favs = fav_ctrl.Listar_Favoritos(p["id"])
    assert code_list == OK and favs == [1]
    # desfavoritar
    code_des, _ = fav_ctrl.Desfavoritar_Jogo(p["id"], 1)
    assert code_des == OK
    code_des_again, _ = fav_ctrl.Desfavoritar_Jogo(p["id"], 1)
    assert code_des_again == NAO_ENCONTRADO