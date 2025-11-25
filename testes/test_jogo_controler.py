import pytest
from utils.codigos import OK, DADOS_INVALIDOS, CONFLITO, NAO_ENCONTRADO
import dados.database as db
import controles.jogo_controler as jogo_ctrl

@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    # Mock de todas as funções de salvar para evitar escrita em disco
    monkeypatch.setattr(db, "salvar_jogos", lambda: True)
    monkeypatch.setattr(db, "salvar_perfis", lambda: True)     # Necessário para Remover_Jogo
    monkeypatch.setattr(db, "salvar_avaliacoes", lambda: True)  # Necessário para Remover_Jogo

    # Limpa todas as listas globais para garantir que Remover_Jogo não falhe
    db.jogos.clear()
    db.perfis.clear()
    db.avaliacoes.clear() 

    # Dados iniciais
    db.jogos.extend([
        {"id": 1, "titulo": "God of War", "genero": "Ação", "descricao": "", "nota_geral": 0.0},
        {"id": 2, "titulo": "Portal 2", "genero": "Puzzle", "descricao": "", "nota_geral": 0.0},
    ])
    yield

def test_cadastrar_jogo_sucesso():
    # Teste de cadastro [cite: 77-80]
    code, jogo = jogo_ctrl.Cadastrar_Jogo("Hades", "rogue-lite", "Ação", 0.0)
    assert code == OK
    assert jogo["titulo"] == "Hades"
    assert any(j["titulo"] == "Hades" for j in db.jogos)

def test_cadastrar_jogo_campos_invalidos():
    # Teste de campos obrigatórios [cite: 85-87]
    code, _ = jogo_ctrl.Cadastrar_Jogo("", None, "", None)
    assert code == DADOS_INVALIDOS

def test_cadastrar_jogo_conflito_titulo():
    # Teste de unicidade [cite: 82-84]
    code, _ = jogo_ctrl.Cadastrar_Jogo("God of War", None, "Ação", None)
    assert code == CONFLITO

def test_busca_atualiza_remove_jogo():
    # 1. Busca [cite: 96-99]
    code, jogo = jogo_ctrl.Busca_Jogo(1)
    assert code == OK and jogo["titulo"] == "God of War"

    # 2. Atualização [cite: 105-106]
    # Tentamos passar 9.5 na nota, mas o sistema DEVE ignorar
    code_up, jogo_up = jogo_ctrl.Atualizar_Jogo(1, "God of War Remake", "nova", "Ação", 9.5)
    assert code_up == OK
    assert jogo_up["titulo"] == "God of War Remake"
    
    # VERIFICAÇÃO EXTRA: Garante que a nota NÃO mudou manualmente
    assert jogo_up["nota_geral"] == 0.0 

    # 3. Remoção [cite: 119-122]
    code_rm, _ = jogo_ctrl.Remover_Jogo(1)
    assert code_rm == OK
    
    # 4. Busca após remover (Erro 4) [cite: 124-126]
    code_busca, _ = jogo_ctrl.Busca_Jogo(1)
    assert code_busca == NAO_ENCONTRADO