# dados/database.py

import json
import os

BASE_DIR = os.path.dirname(__file__)
PERFIS_FILE = os.path.join(BASE_DIR, "perfis.json")
JOGOS_FILE = os.path.join(BASE_DIR, "jogos.json")
AVALIACOES_FILE = os.path.join(BASE_DIR, 'avaliacoes.json')

# Lista global de avaliações
avaliacoes = []

# perfis padrão
default_perfis = [
    {"id": 1, "nome": "Danielle", "descricao": "Amante de RPGs", "avatar": "avatar1.png", "favoritos": []},
    {"id": 2, "nome": "Luis", "descricao": "Jogador retrô", "avatar": "avatar2.png", "favoritos": []}
]

# jogos padrão
default_jogos = [
    {"id": 1, "titulo": "The Witcher 3", "descricao": "", "genero": "RPG", "nota_geral": 0.0},
    {"id": 2, "titulo": "Celeste", "descricao": "", "genero": "Plataforma", "nota_geral": 0.0},
    {"id": 3, "titulo": "Stardew Valley", "descricao": "", "genero": "Simulação", "nota_geral": 0.0}
]

# --- CARREGAMENTO DE PERFIS ---
try:
    with open(PERFIS_FILE, "r", encoding="utf-8") as f:
        perfis = json.load(f)
except Exception:
    perfis = default_perfis.copy()
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        with open(PERFIS_FILE, "w", encoding="utf-8") as f:
            json.dump(perfis, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# --- CARREGAMENTO DE JOGOS ---
try:
    with open(JOGOS_FILE, "r", encoding="utf-8") as f:
        jogos = json.load(f)
except Exception:
    jogos = default_jogos.copy()
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        with open(JOGOS_FILE, "w", encoding="utf-8") as f:
            json.dump(jogos, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# --- FUNÇÕES DE SALVAMENTO ---

def salvar_perfis():
    """Persiste a lista `perfis` em dados/perfis.json"""
    try:
        with open(PERFIS_FILE, "w", encoding="utf-8") as f:
            json.dump(perfis, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def salvar_jogos():
    """Persiste a lista `jogos` em dados/jogos.json"""
    try:
        with open(JOGOS_FILE, "w", encoding="utf-8") as f:
            json.dump(jogos, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# --- LÓGICA DE AVALIAÇÕES (CORRIGIDA) ---

def carregar_avaliacoes():
    if os.path.exists(AVALIACOES_FILE):
        # FIX: encoding="utf-8" é obrigatório para não quebrar com acentos
        with open(AVALIACOES_FILE, 'r', encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def salvar_avaliacoes():
    try:
        # FIX: encoding="utf-8" e ensure_ascii=False
        with open(AVALIACOES_FILE, 'w', encoding="utf-8") as f:
            json.dump(avaliacoes, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False

# Inicializa a lista carregando do arquivo
avaliacoes = carregar_avaliacoes()