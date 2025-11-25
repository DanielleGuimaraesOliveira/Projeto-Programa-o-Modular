import pytest
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO
import dados.database as db
import controles.seguidores_controler as seg_ctrl
import controles.perfil_controler as perfil_ctrl

@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    # Mock de todas as funções de persistência
    monkeypatch.setattr(db, "salvar_perfis", lambda: True)
    monkeypatch.setattr(db, "salvar_jogos", lambda: True)
    monkeypatch.setattr(db, "salvar_avaliacoes", lambda: True) # Necessário pois Desativar_Conta acessa isso

    # Limpeza completa de todas as tabelas
    db.perfis.clear()
    db.jogos.clear()
    db.avaliacoes.clear() 
    yield

def test_seguir_e_parar_de_seguir():
    """Testa o fluxo básico de seguir e deixar de seguir."""
    _, a = perfil_ctrl.Criar_Perfil("uA")
    _, b = perfil_ctrl.Criar_Perfil("uB")
    
    # 1. Seguir (Sucesso)
    c1, _ = seg_ctrl.Seguir_Perfil(a["id"], b["id"])
    assert c1 == OK
    
    # 2. Tentar seguir novamente (Conflito)
    # Nota: Se o seu sistema usasse "Toggle" (alternar), aqui ele pararia de seguir.
    # Como seu teste espera CONFLITO, assume-se que há funções separadas para Seguir/Parar.
    c_conf, _ = seg_ctrl.Seguir_Perfil(a["id"], b["id"])
    assert c_conf == CONFLITO
    
    # 3. Verificar listagem
    c_list, seguindo = seg_ctrl.Listar_Seguindo(a["id"])
    assert c_list == OK and b["id"] in seguindo
    
    # 4. Parar de Seguir
    c_stop, _ = seg_ctrl.Parar_de_Seguir(a["id"], b["id"])
    assert c_stop == OK
    
    # 5. Verificar remoção
    c_list2, seguindo2 = seg_ctrl.Listar_Seguindo(a["id"])
    assert c_list2 == OK and b["id"] not in seguindo2

def test_proibir_auto_seguimento():
    """Testa a regra: O sistema deve impedir que um perfil siga a si mesmo."""
    _, p = perfil_ctrl.Criar_Perfil("selfie")
    
    # Dado: Perfil_1 = Perfil_2 -> Retorna 1 (Dados Inválidos)
    c, _ = seg_ctrl.Seguir_Perfil(p["id"], p["id"])
    assert c == DADOS_INVALIDOS

def test_desativar_remove_referencias():
    """Testa se excluir um usuário remove ele da lista de 'seguindo' dos outros."""
    _, p1 = perfil_ctrl.Criar_Perfil("x1")
    _, p2 = perfil_ctrl.Criar_Perfil("x2")
    
    seg_ctrl.Seguir_Perfil(p1["id"], p2["id"])
    
    # P1 segue P2. Vamos apagar P2.
    c_rm, _ = perfil_ctrl.Desativar_Conta(p2["id"])
    assert c_rm == OK
    
    # A lista de "Seguindo" do P1 não deve mais ter o ID do P2
    c_list, seguindo = seg_ctrl.Listar_Seguindo(p1["id"])
    assert c_list == OK and p2["id"] not in seguindo