import pytest
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO, CONFLITO
import dados.database as db
import controles.perfil_controler as perfil_ctrl

@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    # Mock das funções de salvar
    monkeypatch.setattr(db, "salvar_perfis", lambda: True)
    monkeypatch.setattr(db, "salvar_jogos", lambda: True)
    monkeypatch.setattr(db, "salvar_avaliacoes", lambda: True) # Necessário agora

    # Limpeza COMPLETA (incluindo avaliações globais)
    db.perfis.clear()
    db.jogos.clear()
    db.avaliacoes.clear() # FIX: Limpa avaliações anteriores

    # Dados iniciais
    db.jogos.extend([
        {"id": 1, "titulo": "God of War", "genero": "Ação", "descricao": "", "nota_geral": 0.0},
        {"id": 2, "titulo": "Portal 2", "genero": "Puzzle", "descricao": "", "nota_geral": 0.0},
    ])
    yield

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
    # Testa se o wrapper do perfil chama corretamente a avaliação global
    _, p1 = perfil_ctrl.Criar_Perfil("p1")
    _, p2 = perfil_ctrl.Criar_Perfil("p2")
    
    # Wrapper: (id_perfil, id_jogo, nota, op)
    code1, _ = perfil_ctrl.Adicionar_Avaliacao(p1["id"], 1, 8.0, "bom")
    code2, _ = perfil_ctrl.Adicionar_Avaliacao(p2["id"], 1, 6.0, "ok")
    
    assert code1 == OK and code2 == OK
    
    # Verifica se a nota do jogo atualizou (Média: 7.0)
    jogo = next(j for j in db.jogos if j["id"] == 1)
    assert jogo["nota_geral"] == pytest.approx(7.0)

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
    
    # Remover avaliação via wrapper do perfil
    code, _ = perfil_ctrl.Remover_Avaliacao(p2["id"], 2)
    
    assert code == OK
    # Média deve subir para 10.0 (só sobrou p1)
    assert jogo["nota_geral"] == pytest.approx(10.0)

def test_desativar_conta_remove_avaliacoes():
    """
    TESTE NOVO: Verifica se deletar o usuário apaga as notas que ele deu.
    Isso valida a correção de 'Exclusão em Cascata' no Perfil.
    """
    # Cenário: Jogo com nota 10 (User1) e nota 0 (User2). Média = 5.0
    _, p1 = perfil_ctrl.Criar_Perfil("User1")
    _, p2 = perfil_ctrl.Criar_Perfil("User2")
    
    perfil_ctrl.Adicionar_Avaliacao(p1["id"], 1, 10.0, "top")
    perfil_ctrl.Adicionar_Avaliacao(p2["id"], 1, 0.0, "ruim")
    
    jogo = next(j for j in db.jogos if j["id"] == 1)
    assert jogo["nota_geral"] == 5.0
    
    # Ação: Desativar conta do User2 (que deu nota 0)
    perfil_ctrl.Desativar_Conta(p2["id"])
    
    # Verificação: A nota do jogo deve subir para 10.0, pois a nota 0 foi apagada
    assert jogo["nota_geral"] == 10.0
    
    # Verifica se o perfil sumiu
    assert p2 not in db.perfis