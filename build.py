"""Cria o executável do projeto."""
# pylint: disable=broad-exception-caught
# pylint: disable=line-too-long

import shutil
import subprocess
from pathlib import Path
from dotenv import dotenv_values

def criar_app_py(app_script):
    """Cria dinamicamente um app.py para rodar como entrada do executável."""
    print("[INFO] Criando arquivo temporário 'app.py'...")

    # Lê o .env e converte para dicionário
    env_vars = dotenv_values(".env")

    # Constrói o conteúdo do app.py
    app_content = '''"""Utilizado para iniciar o projeto quando executado via exe."""\n'''
    app_content += "import os\nimport main\n\n"
    app_content += "if __name__ == \"__main__\":\n"
    app_content += "    main.log_step(\"Definindo variáveis de ambiente\")\n"

    # Adiciona as variáveis de ambiente de forma dinâmica
    for key, value in env_vars.items():
        app_content += f"    os.environ[\"{key}\"] = \"{value}\"\n"

    # Configura o caminho do Playwright
    app_content += "    localappdata = os.getenv(\"LOCALAPPDATA\")\n"
    app_content += "    os.environ[\"PLAYWRIGHT_BROWSERS_PATH\"] = f\"{localappdata}\\\\ms-playwright\"\n"

    # Inicializa o projeto
    app_content += "    main.log_step(\"Iniciando o projeto\")\n"
    app_content += "    main.init()\n"

    # Salva o arquivo temporário
    with open(app_script, "w", encoding="utf-8") as f:
        f.write(app_content)

    print("[INFO] Arquivo 'app.py' criado com sucesso!")

def build():
    """Cria o executável do projeto."""
    print("[INFO] Iniciando o empacotamento do projeto...")

    # Caminhos e arquivos necessários
    main_script = "app/app.py"  # Script principal do projeto
    output_name = "autotask"  # Nome do executável
    resource_dir = "app/resource"  # Pasta de recursos
    de_para_file = f"{resource_dir}/DE_PARA_ESCRITORIO_RESPONSAVEL.xlsx"  # Arquivo de-para
    icon_file = "icon.ico"  # Ícone do executável (opcional)# Caminhos e arquivos

    # Verifica se os arquivos e pastas necessários existem
    if not Path(de_para_file).exists():
        print(f"[ERRO] Arquivo de-para '{de_para_file}' não encontrado.")
        return

    # Monta o comando do PyInstaller
    command = [
        "pyinstaller",
        "--onefile",  # Gera um único arquivo executável
        "--name", output_name,  # Nome do executável
        "--add-data", f"{de_para_file};resource",  # Adiciona o arquivo de-para direto na pasta 'resource' pois o arquivo é lido por um módulo no app
        "--noconfirm"  # Evita prompts de confirmação
    ]

    # Inclui o ícone, se existir
    if Path(icon_file).exists():
        command.extend(["--icon", icon_file])

    # Adiciona o script principal ao comando
    command.append(main_script)

    # Executa o comando
    try:
        criar_app_py(main_script)  # Cria o app.py dinâmico antes de empacotar
        if not Path(main_script).exists():
            print(f"[ERRO] Arquivo principal '{main_script}' não encontrado.")
            return
        subprocess.run(command, check=True)
        print("[INFO] Empacotamento concluído com sucesso!")
        print("[INFO] Verifique o executável na pasta 'dist/'.")
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha no empacotamento: {e}")
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
    finally:
        # Remove o arquivo temporário app.py
        if Path(main_script).exists():
            Path(main_script).unlink()
            print("[INFO] Arquivo temporário 'app.py' removido após o empacotamento.")
        if Path("build").exists():
            shutil.rmtree("build")

if __name__ == "__main__":
    build()
