# data/database.py

import json
import os

BASE_DIR = os.path.dirname(__file__)
PERFIS_FILE = os.path.join(BASE_DIR, "perfis.json")

# perfis padrão (usados na primeira execução)
default_perfis = [
    {"id": 1, "nome": "Danielle", "descricao": "Amante de RPGs", "avatar": "avatar1.png", "favoritos": []},
    {"id": 2, "nome": "Luis", "descricao": "Jogador retrô", "avatar": "avatar2.png", "favoritos": []}
]

# tenta carregar perfis do arquivo; se não existir, usa o default e cria o arquivo
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

# jogos de exemplo (permanece inalterado)
jogos = [
    {"id": 1, "titulo": "The Witcher 3", "genero": "RPG"},
    {"id": 2, "titulo": "Celeste", "genero": "Plataforma"},
    {"id": 3, "titulo": "Stardew Valley", "genero": "Simulação"}
]

def salvar_perfis():
    """Persiste a lista `perfis` em dados/perfis.json"""
    try:
        with open(PERFIS_FILE, "w", encoding="utf-8") as f:
            json.dump(perfis, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
