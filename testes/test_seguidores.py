import pytest
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO
import dados.database as db
import controles.perfil_controler as perfil_ctrl

@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    monkeypatch.setattr(db, "salvar_perfis", lambda: True)
    db.perfis.clear()
    yield

def test_seguir_e_parar_de_seguir():
    _, a = perfil_ctrl.Criar_Perfil("uA")
    _, b = perfil_ctrl.Criar_Perfil("uB")
    c1, _ = perfil_ctrl.Seguir_Perfil(a["id"], b["id"])
    assert c1 == OK
    # seguir novamente -> conflito
    c_conf, _ = perfil_ctrl.Seguir_Perfil(a["id"], b["id"])
    assert c_conf == CONFLITO
    # is following via Listar_Seguindo
    c_list, seguindo = perfil_ctrl.Listar_Seguindo(a["id"])
    assert c_list == OK and b["id"] in seguindo
    # parar de seguir
    c_stop, _ = perfil_ctrl.Parar_de_Seguir(a["id"], b["id"])
    assert c_stop == OK
    c_list2, seguindo2 = perfil_ctrl.Listar_Seguindo(a["id"])
    assert c_list2 == OK and b["id"] not in seguindo2

def test_proibir_auto_seguimento():
    _, p = perfil_ctrl.Criar_Perfil("selfie")
    c, _ = perfil_ctrl.Seguir_Perfil(p["id"], p["id"])
    assert c == DADOS_INVALIDOS

def test_desativar_remove_referencias():
    _, p1 = perfil_ctrl.Criar_Perfil("x1")
    _, p2 = perfil_ctrl.Criar_Perfil("x2")
    perfil_ctrl.Seguir_Perfil(p1["id"], p2["id"])
    # desativar p2 deve remover referencia em p1.seguindo
    c_rm, _ = perfil_ctrl.Desativar_Conta(p2["id"])
    assert c_rm == OK
    c_list, seguindo = perfil_ctrl.Listar_Seguindo(p1["id"])
    assert c_list == OK and p2["id"] not in seguindo