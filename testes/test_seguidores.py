import pytest
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO
import dados.database as db
import controles.seguidores_controler as seg_ctrl
import controles.perfil_controler as perfil_ctrl

@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    # evita escrita em disco durante os testes
    monkeypatch.setattr(db, "salvar_perfis", lambda: True)
    db.perfis.clear()
    yield

def test_seguir_e_parar_de_seguir():
    _, a = perfil_ctrl.Criar_Perfil("uA")
    _, b = perfil_ctrl.Criar_Perfil("uB")
    c1, _ = seg_ctrl.Seguir_Perfil(a["id"], b["id"])
    assert c1 == OK
    # seguir novamente -> conflito
    c_conf, _ = seg_ctrl.Seguir_Perfil(a["id"], b["id"])
    assert c_conf == CONFLITO
    # seguindo aparece em Listar_Seguindo
    c_list, seguindo = seg_ctrl.Listar_Seguindo(a["id"])
    assert c_list == OK and b["id"] in seguindo
    # parar de seguir
    c_stop, _ = seg_ctrl.Parar_de_Seguir(a["id"], b["id"])
    assert c_stop == OK
    c_list2, seguindo2 = seg_ctrl.Listar_Seguindo(a["id"])
    assert c_list2 == OK and b["id"] not in seguindo2

def test_proibir_auto_seguimento():
    _, p = perfil_ctrl.Criar_Perfil("selfie")
    c, _ = seg_ctrl.Seguir_Perfil(p["id"], p["id"])
    assert c == DADOS_INVALIDOS

def test_desativar_remove_referencias():
    _, p1 = perfil_ctrl.Criar_Perfil("x1")
    _, p2 = perfil_ctrl.Criar_Perfil("x2")
    seg_ctrl.Seguir_Perfil(p1["id"], p2["id"])
    # desativar p2 deve remover referência em p1.seguindo
    c_rm, _ = perfil_ctrl.Desativar_Conta(p2["id"])
    assert c_rm == OK
    c_list, seguindo = seg_ctrl.Listar_Seguindo(p1["id"])
    assert c_list == OK and p2["id"] not in seguindo