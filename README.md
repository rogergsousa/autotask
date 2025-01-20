# Automatização de Tarefas no LawSystem

Este projeto automatiza o processo de preenchimento de formulários em um sistema de escritório externo que não tem API para o cadasto de tarefas para analise de prazos vindo de um sistema terceiro, baseado em dados provenientes de um banco de dados SQL Server. A aplicação utiliza **Python** e a biblioteca **Playwright** para navegação e interação com o site.

---

## **Índice**
- [Automatização de Tarefas no LawSystem](#automatização-de-tarefas-no-lawsystem)
  - [**Índice**](#índice)
  - [**Requisitos**](#requisitos)
    - [Dependências de Software](#dependências-de-software)
    - [Bibliotecas Python](#bibliotecas-python)
  - [**Funcionalidades**](#funcionalidades)
  - [**Configuração do Ambiente**](#configuração-do-ambiente)
    - [1. Clone o Repositório](#1-clone-o-repositório)
    - [2. Execute o Script de Configuração](#2-execute-o-script-de-configuração)
    - [3. Configure as Variáveis de Ambiente](#3-configure-as-variáveis-de-ambiente)
    - [4. Instale o Playwright](#4-instale-o-playwright)
  - [**Execução do Projeto**](#execução-do-projeto)
  - [**Estrutura do Projeto**](#estrutura-do-projeto)
  - [**Contribuições**](#contribuições)
  - [**Licença**](#licença)
  - [**Contato**](#contato)

---

## **Requisitos**

### Dependências de Software
- Python 3.9 ou superior
- Google Chrome ou Microsoft Edge (para execução do Playwright)
- SQL Server

### Bibliotecas Python
- **Playwright**: Navegação e interação com páginas web.
- **Pymssql**: Conexão ao banco de dados SQL Server.
- **Pandas**: Manipulação e análise de dados.
- **Python-dotenv**: Gerenciamento de variáveis de ambiente.

---

## **Funcionalidades**

1. Realiza login automático no sistema LawSystem.
2. Consulta um banco de dados SQL Server para obter informações.
3. Navega para páginas específicas no LawSystem e preenche formulários com os dados da consulta.
4. Valida a operação e atualiza o status no banco de dados.
5. Cria tarefas automatizadas no sistema LawSystem.

---

## **Configuração do Ambiente**

### 1. Clone o Repositório
```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```

### 2. Execute o Script de Configuração
O script `setup.py` configura automaticamente o ambiente virtual, instala as dependências e cria arquivos necessários como `.env` e `launch.json`.

```bash
python setup.py
```

### 3. Configure as Variáveis de Ambiente
No arquivo `.env`, preencha as informações necessárias:
```env
SQL_SERVER=<INSIRA_O_SERVIDOR_SQL>
SQL_USER=<INSIRA_O_USUARIO_SQL>
SQL_PASSWORD=<INSIRA_A_SENHA_SQL>
SQL_DATABASE=<INSIRA_O_NOME_DO_BANCO>
LAWSYSTEM_USERNAME=<INSIRA_O_USUARIO_LAWSYSTEM>
LAWSYSTEM_PASSWORD=<INSIRA_A_SENHA_LAWSYSTEM>
```

### 4. Instale o Playwright
Instale e configure o Playwright:
```bash
python -m playwright install
```

---

## **Execução do Projeto**

1. **Ative o Ambiente Virtual**
   - No Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - No Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

2. **Execute o Script Principal**
```bash
python main.py
```

3. **Debug no VSCode**
   - Abra o projeto no **Visual Studio Code**.
   - Pressione **F5** para iniciar o depurador.

---

## **Estrutura do Projeto**

```plaintext
.
├── .vscode/                # Configurações do Visual Studio Code
│   └── launch.json         # Configurações de depuração
├── resource/               # Arquivos de recurso, como o arquivo de-para
│   └── DE_PARA_ESCRITORIO_RESPONSAVEL.xlsx
├── .env                    # Variáveis de ambiente (criado pelo setup.py)
├── .gitignore              # Arquivos ignorados pelo Git
├── requirements.txt        # Dependências do projeto
├── setup.py                # Script de configuração do ambiente
├── main.py                 # Script principal do projeto
└── README.md               # Documentação do projeto
```

---

## **Contribuições**

Contribuições são bem-vindas! Siga os passos abaixo:

1. Crie um fork do repositório.
2. Crie um branch para sua feature:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça o commit das alterações:
   ```bash
   git commit -m "Minha nova feature"
   ```
4. Envie para o branch principal:
   ```bash
   git push origin minha-feature
   ```
5. Crie um Pull Request no GitLab.

---

## **Licença**

Este projeto é licenciado sob a [MIT License](LICENSE). Consulte o arquivo `LICENSE` para mais detalhes.

---

## **Contato**

Em caso de dúvidas ou problemas, entre em contato com o responsável pelo projeto:
- Nome: **Rogério G. de Sousa**
- E-mail: **rgsousa@gmail.com**