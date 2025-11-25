import pytest
from utils.codigos import OK, DADOS_INVALIDOS, NAO_ENCONTRADO
import dados.database as db
import controles.avaliacao_controler as aval_ctrl
import controles.perfil_controler as perfil_ctrl

# FIX 1: Atualizar a fixture para limpar a lista global de avaliações
@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    monkeypatch.setattr(db, "salvar_perfis", lambda: True)
    monkeypatch.setattr(db, "salvar_jogos", lambda: True)
    monkeypatch.setattr(db, "salvar_avaliacoes", lambda: True) # Mock do salvar avaliações
    
    db.perfis.clear()
    db.jogos.clear()
    db.avaliacoes.clear() # Limpa a lista global
    
    # Seed inicial
    db.jogos.extend([
        {"id": 1, "titulo": "God of War", "genero": "Ação", "descricao": "", "nota_geral": 0.0},
    ])
    yield

def test_avaliar_criar_e_recalcula_media():
    _, p1 = perfil_ctrl.Criar_Perfil("a1")
    _, p2 = perfil_ctrl.Criar_Perfil("a2")
    
    # FIX 2: A ordem dos parâmetros mudou para (id_jogo, nota, descricao, id_perfil)
    c1, _ = aval_ctrl.Avaliar_jogo(1, 9.0, "ótimo", p1["id"])
    c2, _ = aval_ctrl.Avaliar_jogo(1, 7.0, "bom", p2["id"])
    
    assert c1 == OK and c2 == OK
    
    jogo = next(j for j in db.jogos if j["id"] == 1)
    # Média: (9 + 7) / 2 = 8.0
    assert jogo["nota_geral"] == pytest.approx(8.0)

def test_avaliar_nota_invalida_e_jogo_inexistente():
    _, p = perfil_ctrl.Criar_Perfil("a3")
    
    # FIX 2: Ordem dos parâmetros corrigida
    c_bad, _ = aval_ctrl.Avaliar_jogo(1, 20, "x", p["id"])
    assert c_bad == DADOS_INVALIDOS
    
    c_nf, _ = aval_ctrl.Avaliar_jogo(999, 5, "", p["id"])
    assert c_nf == NAO_ENCONTRADO

def test_remover_avaliacao_atualiza_media():
    _, p1 = perfil_ctrl.Criar_Perfil("r1")
    _, p2 = perfil_ctrl.Criar_Perfil("r2")
    
    aval_ctrl.Avaliar_jogo(1, 10.0, "ótimo", p1["id"])
    
    # Capturamos o retorno para saber o ID da avaliação criada
    c, avaliacao_criada = aval_ctrl.Avaliar_jogo(1, 6.0, "bom", p2["id"])
    
    jogo = next(j for j in db.jogos if j["id"] == 1)
    assert jogo["nota_geral"] == pytest.approx(8.0) # (10+6)/2
    
    # FIX 3: A remoção agora é pelo ID da AVALIAÇÃO[cite: 323], não pelo ID do perfil
    c_rm, _ = aval_ctrl.Remover_avaliacao(avaliacao_criada["id"])
    
    assert c_rm == OK
    
    # Deve sobrar apenas a nota 10.0 do p1
    assert jogo["nota_geral"] == pytest.approx(10.0)