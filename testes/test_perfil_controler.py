import pytest
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO
import dados.database as db
import controles.perfil_controler as perfil_ctrl
import controles.jogo_controler as jogo_ctrl

@pytest.fixture(autouse=True)
def clean_db(monkeypatch, tmp_path):
    # evita escrita em disco
    monkeypatch.setattr(db, "salvar_perfis", lambda: True)
    monkeypatch.setattr(db, "salvar_jogos", lambda: True)
    # limpar e preparar dados em memória (mesmo objeto referenciado pelos controllers)
    db.perfis.clear()
    db.perfis.extend([])
    db.jogos.clear()
    db.jogos.extend([
        {"id": 1, "titulo": "God of War", "genero": "Ação", "descricao": "", "nota_geral": 0.0},
        {"id": 2, "titulo": "Portal 2", "genero": "Puzzle", "descricao": "", "nota_geral": 0.0},
    ])
    yield
    # no tear down necessário (listas ficam limpas para próximo teste)


def test_criar_perfil_sucesso():
    code, perfil = perfil_ctrl.Criar_Perfil("usuario1", "desc", "avatar.png")
    assert code == OK
    assert perfil["nome"] == "usuario1"
    assert perfil in db.perfis

def test_criar_perfil_nome_vazio():
    code, perfil = perfil_ctrl.Criar_Perfil("", None, None)
    assert code == DADOS_INVALIDOS

def test_criar_perfil_conflito():
    perfil_ctrl.Criar_Perfil("dup", None, None)
    code, _ = perfil_ctrl.Criar_Perfil("dup", None, None)
    assert code == CONFLITO

def test_adicionar_avaliacao_e_media():
    # cria dois perfis e adiciona avaliações ao mesmo jogo
    _, p1 = perfil_ctrl.Criar_Perfil("p1")
    _, p2 = perfil_ctrl.Criar_Perfil("p2")
    code1, _ = perfil_ctrl.Adicionar_Avaliacao(p1["id"], 1, 8.0, "bom")
    code2, _ = perfil_ctrl.Adicionar_Avaliacao(p2["id"], 1, 6.0, "ok")
    assert code1 == OK and code2 == OK
    # recalculo deve atualizar nota_geral no jogo
    jogo = next(j for j in db.jogos if j["id"] == 1)
    assert jogo["nota_geral"] == pytest.approx(7.0, rel=1e-3)

def test_adicionar_avaliacao_nota_invalida():
    _, p = perfil_ctrl.Criar_Perfil("p3")
    code, _ = perfil_ctrl.Adicionar_Avaliacao(p["id"], 1, 20, "x")
    assert code == DADOS_INVALIDOS

def test_adicionar_avaliacao_jogo_inexistente():
    _, p = perfil_ctrl.Criar_Perfil("p4")
    code, _ = perfil_ctrl.Adicionar_Avaliacao(p["id"], 999, 5.0, "")
    assert code == NAO_ENCONTRADO

def test_remover_avaliacao_e_atualiza_media():
    _, p1 = perfil_ctrl.Criar_Perfil("r1")
    _, p2 = perfil_ctrl.Criar_Perfil("r2")
    perfil_ctrl.Adicionar_Avaliacao(p1["id"], 2, 10.0, "ótimo")
    perfil_ctrl.Adicionar_Avaliacao(p2["id"], 2, 6.0, "bom")
    jogo = next(j for j in db.jogos if j["id"] == 2)
    assert jogo["nota_geral"] == pytest.approx(8.0)
    # remover uma avaliação
    code, _ = perfil_ctrl.Remover_Avaliacao(p2["id"], 2)
    assert code == OK
    # média atualizada
    assert jogo["nota_geral"] == pytest.approx(10.0)