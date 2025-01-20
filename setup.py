'''
Configura o projeto e suas dependencias
'''
import json
import os
import subprocess
from pathlib import Path

def criar_ambiente_virtual():
    """Cria um ambiente virtual para o projeto."""
    print("[INFO] Criando ambiente virtual...")
    venv_path = Path(".venv")
    if not venv_path.exists():
        subprocess.run(["python", "-m", "venv", ".venv"], check=True)
        print("[INFO] Ambiente virtual criado com sucesso!")
    else:
        print("[INFO] Ambiente virtual já existe. Pulando criação.")

def instalar_dependencias():
    """Instala as dependências do projeto no ambiente virtual."""
    print("[INFO] Instalando dependências no ambiente virtual...")

    # Caminho para o pip dentro do ambiente virtual
    pip_path = Path(".venv") / ("Scripts" if os.name == "nt" else "bin") / "pip"
    python_path = Path(".venv") / ("Scripts" if os.name == "nt" else "bin") / "python"
    playwright_path = Path(".venv") / ("Scripts" if os.name == "nt" else "bin") / "playwright"

    try:
        # Atualiza o pip e instala as dependências playwright
        subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        subprocess.run([str(playwright_path), "install"], check=True)
        print("[INFO] Dependências instaladas com sucesso no ambiente virtual!")
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha ao instalar dependências: {e}")
        raise

def configurar_variaveis_ambiente():
    """Configura as variáveis de ambiente necessárias para o projeto."""
    print("[INFO] Configurando variáveis de ambiente...")
    env_path = Path(".env")
    if not env_path.exists():
        with open(env_path, "w") as env_file: # pylint: disable=unspecified-encoding
            env_file.write("# Preencha as credenciais antes de rodar o projeto\n")
            env_file.write("SQL_SERVER=\nSQL_USER=\nSQL_PASSWORD=\nSQL_DATABASE=\n")
            env_file.write("LAWSYSTEM_USERNAME=\nLAWSYSTEM_PASSWORD=\n")
        print("[INFO] Arquivo .env criado. Preencha as credenciais manualmente antes de rodar o projeto.")
    else:
        print("[INFO] Arquivo .env já existe. Pulando criação.")


def criar_launch_json():
    """Cria o arquivo launch.json para o VSCode na pasta .vscode."""
    print("[INFO] Configurando launch.json para VSCode...")
    vscode_path = Path(".vscode")
    vscode_path.mkdir(exist_ok=True)

    launch_json_path = vscode_path / "launch.json"
    if not launch_json_path.exists():
        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Python Debugger: Current File",
                    "type": "python",
                    "request": "launch",
                    "program": "${file}",
                    "console": "integratedTerminal",
                    "justMyCode": True,
                    "python": str(Path(".venv") / "Scripts" / "python.exe" if os.name == "nt" else Path(".venv") / "bin" / "python") # pylint: disable=line-too-long
                }
            ]
        }

        with open(launch_json_path, "w") as launch_file: # pylint: disable=unspecified-encoding
            json.dump(launch_config, launch_file, indent=4)
        print("[INFO] launch.json criado com sucesso!")
    else:
        print("[INFO] launch.json já existe. Pulando criação.")

def instrucoes_finais():
    """Exibe instruções finais para o time."""
    print("\n[INFO] Configuração concluída!")
    print("Siga os passos abaixo para iniciar o ambiente de desenvolvimento:")
    print("1. Ative o ambiente virtual:")
    print("   - No Windows: .venv\\Scripts\\activate")
    print("   - No Linux/Mac: source .venv/bin/activate")
    print("2. Configure o arquivo .env com as credenciais corretas.")
    print("3. Execute o projeto com: python main.py")

def main():
    """Executa o script de configuração."""
    try:
        criar_ambiente_virtual()
        instalar_dependencias()
        configurar_variaveis_ambiente()
        criar_launch_json()
        instrucoes_finais()
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha ao executar o comando: {e}")
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"[ERRO] Erro inesperado: {e}")

if __name__ == "__main__":
    main()
