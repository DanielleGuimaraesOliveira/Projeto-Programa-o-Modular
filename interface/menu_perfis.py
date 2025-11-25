from typing import Optional, Dict
from controles import perfil_controler
from utils.codigos import OK, CONFLITO, DADOS_INVALIDOS, NAO_ENCONTRADO

def _input_strip(prompt: str) -> str:
    return input(prompt).strip()

def _print_header(titulo: str) -> None:
    print(f"\n=== {titulo} ===")

def exibir_menu_perfis(perfil_ativo: Optional[Dict]) -> bool:
    """
    Exibe menu de perfis.
    Retorna:
      - True  -> usuário permaneceu logado / voltou ao menu principal normalmente.
      - False -> conta desativada / usuário deslogado (o caller deve chamar o menu inicial).
    """
    while True:
        _print_header("PERFIS")
        print("1. Listar perfis")
        print("2. Ver perfil por ID")
        print("3. Atualizar meu perfil")
        print("4. Desativar minha conta")
        print("5. Seguir um perfil")
        print("6. Parar de seguir")
        print("7. Listar meus seguidores")
        print("8. Listar quem sigo")
        print("0. Voltar")
        opcao = _input_strip("Escolha: ")

        if opcao == "1":
            codigo, lista = perfil_controler.Listar_Perfil()
            if codigo == OK:
                for p in lista:
                    nome = p.get('nome_usuario') or p.get('nome') or '(sem nome)'
                    print(f"  {p['id']} - {nome}")
            else:
                print("❌ Erro ao listar perfis.")
        elif opcao == "2":
            try:
                idp = int(_input_strip("ID do perfil: "))
            except ValueError:
                print("⚠️ ID inválido!")
                continue
            codigo, p = perfil_controler.Busca_Perfil(idp)
            if codigo == OK and p:
                print(f"\nID: {p['id']}")
                print(f"Nome: {p.get('nome_usuario', p.get('nome',''))}")
                print(f"Descrição: {p.get('descricao','')}")
                print(f"Seguidores: {len(p.get('seguidores',[]))} | Seguindo: {len(p.get('seguindo',[]))}")
                print(f"🎮 Jogando: {p.get('jogando', 0)}")
                print(f"✅ Jogados: {p.get('jogados', 0)}")
                print(f"🏆 Platinados: {p.get('platinados', 0)}")
            else:
                print("❌ Perfil não encontrado.")
        elif opcao == "3":
            if not perfil_ativo:
                print("❌ Nenhum perfil ativo.")
                continue
            nome = _input_strip("Novo nome (ENTER para manter): ")
            descricao = _input_strip("Nova descrição (ENTER para manter): ")
            avatar = _input_strip("Novo avatar (ENTER para manter): ")
            nome_arg = None if nome == "" else nome
            descricao_arg = None if descricao == "" else descricao
            avatar_arg = None if avatar == "" else avatar
            codigo, p = perfil_controler.Atualizar_Dados(perfil_ativo['id'], nome_arg, descricao_arg, avatar_arg)
            if codigo == OK:
                print("✅ Perfil atualizado.")
                perfil_ativo.update(p)
            elif codigo == DADOS_INVALIDOS:
                print("❌ Dados inválidos.")
            elif codigo == CONFLITO:
                print("❌ Nome já em uso por outro perfil.")
            else:
                print("❌ Erro ao atualizar.")
        elif opcao == "4":
            if not perfil_ativo:
                print("❌ Nenhum perfil ativo.")
                continue
            conf = _input_strip("Tem certeza que quer desativar sua conta? (s/n): ").lower()
            if conf == "s":
                codigo, _ = perfil_controler.Desativar_Conta(perfil_ativo['id'])
                if codigo == OK:
                    print("✅ Conta desativada.")
                    # sinaliza ao chamador que o perfil foi desativado / deslogado
                    return False
                else:
                    print("❌ Erro ao desativar conta.")
            else:
                print("Ação cancelada.")
        elif opcao == "5":
            if not perfil_ativo:
                print("❌ Nenhum perfil ativo.")
                continue
            try:
                codigo, lista = perfil_controler.Listar_Perfil()

                if codigo == OK:
                    print("\nPerfis encontrados:")
                    for p in lista:
                        nome = p.get("nome_usuario") or p.get("nome") or "(sem nome)"
                        print(f"{p['id']} - {nome}")
                else:
                    print("❌ Erro ao listar perfis.")

                id_alvo = int(_input_strip("ID do perfil a seguir: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            codigo, _ = perfil_controler.Seguir_Perfil(perfil_ativo['id'], id_alvo)
            if codigo == OK:
                print("✅ Agora você segue esse perfil.")
            elif codigo == NAO_ENCONTRADO:
                print("❌ Perfil não encontrado.")
            elif codigo == CONFLITO:
                print("❌ Você já segue esse perfil.")
            elif codigo == DADOS_INVALIDOS:
                print("❌ Ação inválida.")
            else:
                print("❌ Erro ao seguir.")
        elif opcao == "6":
            if not perfil_ativo:
                print("❌ Nenhum perfil ativo.")
                continue
            try:
                id_alvo = int(_input_strip("ID do perfil para deixar de seguir: "))
            except ValueError:
                print("⚠️  ID inválido.")
                continue
            codigo, _ = perfil_controler.Parar_de_Seguir(perfil_ativo['id'], id_alvo)
            if codigo == OK:
                print("✅ Você deixou de seguir o perfil.")
            elif codigo == NAO_ENCONTRADO:
                print("❌ Relação não encontrada (ou perfil não existe).")
            else:
                print("❌ Erro ao processar.")
        elif opcao == "7":
            if not perfil_ativo:
                print("❌ Nenhum perfil ativo.")
                continue
            codigo, lista = perfil_controler.Listar_Seguidores(perfil_ativo['id'])
            if codigo == OK:
                # resolve ids para nomes legíveis
                nomes = []
                for pid in lista:
                    c, p = perfil_controler.Busca_Perfil(pid)
                    if c == OK and p:
                        nomes.append(p.get("nome_usuario") or p.get("nome") or f"(#{pid})")
                    else:
                        nomes.append(f"(#{pid})")
                print("Seguidores:", ', '.join(nomes) if nomes else "(nenhum)")
            else:
                print("❌ Erro ao obter seguidores.")
        elif opcao == "8":
            if not perfil_ativo:
                print("❌ Nenhum perfil ativo.")
                continue
            codigo, lista = perfil_controler.Listar_Seguindo(perfil_ativo['id'])
            if codigo == OK:
                # resolve ids para nomes legíveis
                nomes = []
                for pid in lista:
                    c, p = perfil_controler.Busca_Perfil(pid)
                    if c == OK and p:
                        nomes.append(p.get("nome_usuario") or p.get("nome") or f"(#{pid})")
                    else:
                        nomes.append(f"(#{pid})")
                print("Seguindo:", ', '.join(nomes) if nomes else "(nenhum)")
            else:
                print("❌ Erro ao obter lista de seguindo.")
        elif opcao == "0":
            # volta ao menu principal mantendo o perfil ativo
            return True
        else:
            print("❌ Opção inválida.")