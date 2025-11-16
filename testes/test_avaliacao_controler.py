import pytest
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO
import dados.database as db
import controles.avaliacao_controler as aval_ctrl
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
    ])
    yield

def test_avaliar_criar_e_recalcula_media():
    _, p1 = perfil_ctrl.Criar_Perfil("a1")
    _, p2 = perfil_ctrl.Criar_Perfil("a2")
    c1, _ = aval_ctrl.Avaliar_Jogo(p1["id"], 1, 9.0, "ótimo")
    c2, _ = aval_ctrl.Avaliar_Jogo(p2["id"], 1, 7.0, "bom")
    assert c1 == OK and c2 == OK
    jogo = next(j for j in db.jogos if j["id"] == 1)
    assert jogo["nota_geral"] == pytest.approx(8.0)

def test_avaliar_nota_invalida_e_jogo_inexistente():
    _, p = perfil_ctrl.Criar_Perfil("a3")
    c_bad, _ = aval_ctrl.Avaliar_Jogo(p["id"], 1, 20, "x")
    assert c_bad == DADOS_INVALIDOS
    c_nf, _ = aval_ctrl.Avaliar_Jogo(p["id"], 999, 5, "")
    assert c_nf == NAO_ENCONTRADO

def test_remover_avaliacao_atualiza_media():
    _, p1 = perfil_ctrl.Criar_Perfil("r1")
    _, p2 = perfil_ctrl.Criar_Perfil("r2")
    aval_ctrl.Avaliar_Jogo(p1["id"], 1, 10.0, "ótimo")
    aval_ctrl.Avaliar_Jogo(p2["id"], 1, 6.0, "bom")
    jogo = next(j for j in db.jogos if j["id"] == 1)
    assert jogo["nota_geral"] == pytest.approx(8.0)
    c_rm, _ = aval_ctrl.Remover_Avaliacao(p2["id"], 1)
    assert c_rm == OK
    assert jogo["nota_geral"] == pytest.approx(10.0)