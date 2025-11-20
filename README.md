# Letterbox Games (Projeto de Programação Modular)

Plataforma inspirada no Letterboxd, adaptada para videogames. Usuários podem criar perfis, manter uma biblioteca pessoal, avaliar jogos, deixar opiniões, favoritar títulos e seguir outros perfis.

Disciplina: INF1301 — Programação Modular  
Professor: Flávio Bevilacqua

Integrantes:
- 2320584 - Luis Felipe da Silva Gomes  
- 2320336 - Danielle Guimarães Cruz de Oliveira  
- 2311136 - Walter  
- 2210458 - Vinícius Lucena  
- 2011832 - Antônio Pedro Siqueira

Sumário
- Introdução
- Tecnologias
- Estrutura do projeto
- Requisitos implementados (resumo)
- Como usar / executar
- Arquivos de dados
- Notas

Introdução
O objetivo é desenvolver um sistema para registrar jogos jogados, avaliar e compartilhar opiniões, com foco em modularidade e persistência simples em arquivos JSON.

Tecnologias
- Linguagem: Python 3 (recomendado 3.10+)
- Persistência: arquivos JSON em dados/
- Execução local em container de desenvolvimento (Ubuntu 24.04)

Estrutura do projeto (principais diretórios)
- interface/ — menus e interação CLI
- controles/ — lógica de aplicação (perfis, jogos, avaliações)
- dados/ — arquivos JSON (perfis.json, jogos.json)
- utils/ — códigos de retorno, utilitários
- main.py — ponto de entrada

Requisitos / Funcionalidades (implementadas)
- Perfis com nome único, descrição e avatar opcionais.
- Catálogo fixo de jogos (base de 10 jogos famosos) em dados/jogos.json.
- Busca inteligente por nome (substring, iniciais, subsequence).
- Avaliações: usuário pode adicionar/editar/remover nota e opinião.
- Biblioteca pessoal: lista de jogos avaliados; editar ou remover itens.
- Nota geral do jogo calculada a partir de todas as avaliações (exibida dinamicamente).
- Persistência: alterações em perfis e avaliações gravadas em dados/perfis.json; jogos em dados/jogos.json.

Como executar
1. Abra o workspace no container/development environment (Ubuntu 24.04).
2. Execute no terminal:
   ````bash
   python3 main.py
````
Como executar os testes:
1. Abra o workspace no container/development environment (Ubuntu 24.04).
2. Execute no terminal:
````
python3 -m pytest -q testes
````