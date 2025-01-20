'''Automatiza o login no LawSystem, consulta ao banco de dados e preenche informações.'''
# pylint: disable=line-too-long
# pylint: disable=broad-exception-caught

import os
import json
from datetime import datetime, timedelta
import time
import logging
from pathlib import Path
import pymssql
from playwright.sync_api import sync_playwright
import pandas as pd

def carregar_de_para(caminho_arquivo):
    """
    Carrega o arquivo Excel com a tabela de-para em um DataFrame.
    """
    return pd.read_excel(caminho_arquivo)

def buscar_dados(df, pessoa_responsavel):
    """
    Busca os dados correspondentes ao Resposnável do Escritório no DataFrame.
    """
    resultado = df[df['Responsável'] == pessoa_responsavel]
    if resultado.empty:
        return None  # Retorna None se não houver correspondência
    return resultado.iloc[0].to_dict()

def log_step(message):
    ''' Exibe mensagens de log formatadas '''
    print(f"[INFO] {message}")
    logging.info(message)

def configurar_playwright():
    """Garante que os navegadores do Playwright estão instalados."""
    if not Path.home().joinpath("AppData", "Local", "ms-playwright").exists():
        log_step("Instalando navegadores do Playwright...")
        try:
            from playwright.__main__ import main as playwright_main # pylint: disable=import-outside-toplevel
            import sys # pylint: disable=import-outside-toplevel
            sys.argv = ["", "install"]
            playwright_main()
            log_step("Navegadores instalados com sucesso!")
        except Exception as e:
            log_step(f"[ERRO] Falha ao instalar navegadores: {e}")
            raise
    else:
        log_step("Navegadores do Playwright já estão instalados.")

def get_curso_data_from_db():
    """
    Consulta o banco de dados SQL Server usando pymssql e retorna os resultados.
    """
    server = os.getenv("SQL_SERVER")
    user = os.getenv("SQL_USER")
    password = os.getenv("SQL_PASSWORD")
    database = os.getenv("SQL_DATABASE")

    if not all([server, user, password, database]):
        raise pymssql.Error("[ERRO] As credenciais do DB não foram encontradas nas variáveis de ambiente.")
    try:
        return pymssql.connect(server, user, password, database) # pylint: disable=no-member
    except pymssql.Error as e:
        raise pymssql.Error(f"[ERRO] {e}")

def fetch_data_from_db():
    """
    Consulta o banco de dados SQL Server usando pymssql e retorna os resultados.
    """
    query = """
    SELECT 
        CABECALHO, TEXTO, DATA_PUB, DATA_DIV, 
        IS_TAREFA, ID_LAWSYSTEM, PROCESSO, CAST(METADADOS) AS VARBINARY(MAX)) as METADADOS
    FROM 
        dbo.RECORTES 
    WHERE 
        BO_SINCRONIZADO = 'S' AND 
        NU_ESTADO = 2 AND 
        IS_TAREFA = 'N' AND
        CAST(METADADOS as VARCHAR(MAX)) not like '' AND 
        (UPPER(CAST(TEXTO as VARCHAR(MAX)))  like '%LISTA DE INTIMAÇÕES%' OR
         (UPPER(CAST(TEXTO as VARCHAR(MAX)))  like '%EXPEDIÇÃO ELETRÔNICA%'
         AND UPPER(CAST(TEXTO as VARCHAR(MAX)))  not like '%O SISTEMA REGISTROU CIÊNCIA%'
         AND UPPER(CAST(TEXTO as VARCHAR(MAX)))  not like '%VOCÊ TOMOU CIÊNCIA EM%')) AND 
        DATA_DIV >= '2022-01-01 08:00:00.000'
    """
    try:
        conn = get_curso_data_from_db() # pylint: disable=no-member
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query)
        results = cursor.fetchall()

        # Corrigir encoding nos resultados
        for row in results:
            value = row['METADADOS']
            row['METADADOS'] = value.decode('850')

        log_step(f"{len(results)} registros encontrados na consulta.")
        return results
    except pymssql.Error as e:
        log_step(f"[ERRO] Erro ao consultar o banco de dados: {e}")
        return []
    finally:
        conn.close()

def set_data_from_db(id_lawsystem):
    """
    Atualiza a tabela de andamentos, indicando o sucesso da operação de
    criação da tarefa.
    """
    query = """
        UPDATE dbo.RECORTES SET IS_TAREFA=%s 
        WHERE ID_LAWSYSTEM = %s
    """

    try:
        conn = get_curso_data_from_db() # pylint: disable=no-member
        cursor = conn.cursor()
        cursor.execute(query, ("S", id_lawsystem))
        if cursor.rowcount <= 0:
            log_step(f"[ERRO] Nenhum registro foi atualizado para id andamento={id_lawsystem}.")
        conn.commit()
    except pymssql.Error as e:
        log_step(f"[ERRO] Erro ao atualizar o andamento de id andamento={id_lawsystem}: {e}")
    finally:
        conn.close()

def faz_login(logi_page):
    ''' Realiza o login e cria a sessão '''
    try:
        # Obter credenciais do ambiente
        username = os.getenv("LAWSYSTEM_USERNAME")
        password = os.getenv("LAWSYSTEM_PASSWORD")
        if not username or not password:
            raise ValueError("Credenciais de login não encontradas nas variáveis de ambiente.")

        # Acessando a página de login
        logi_page.goto('https://example.com/login')

        # Verificar se a página carregou e os campos estão disponíveis
        logi_page.wait_for_load_state("networkidle", timeout=15000)
        if not (logi_page.is_visible("input#Username") and logi_page.is_visible("input#Password")):
            raise ValueError("Campos de login não encontrados.")

        # Preenchendo os campos de login
        logi_page.fill("input#Username", username)
        logi_page.fill("input#Password", password)

        # Clicando no botão de login
        logi_page.click("button[type='submit']")

        # Aguarde o carregamento da próxima página ou resposta
        time.sleep(2)

        # Verificar se o login falhou
        if logi_page.is_visible("#form0 > div > div"):
            error_message = logi_page.text_content("#form0 > div > div")
            raise ValueError(f"Login não realizado: {error_message}")

        # Verificar se o login foi realizado com sucesso
        if not "firm.lawsystem.com.br" in logi_page.url:
            raise ValueError("A página inicial não foi carregada corretamente.")

        # Login realizado com sucesso. Iniciando preenchimento de dados
        return True

    except ValueError as e:
        log_step(f"[ERRO] {str(e)}")
        return False
    except Exception as e:  
        log_step(f"[ERRO] Erro inesperado: {str(e)}")
        return False

def processar_resultados(results, page, de_para_df):
    '''Processa os resultados da consulta ao banco e preenche os dados no LawSystem.'''
    for row in results:
        try:
            # Extrai dados do banco
            idadamento = row["ID_LAWSYSTEM"]
            metadados = row["METADADOS"]
            processo  = row["PROCESSO"]
            data = json.loads(metadados)
            idprocesso = data['idProcesso']

            # Busca escritórios e envolvidos
            envolvido  = 'Advogado Responsável'
            escritorio = 'Escritório de Advocacia e Advogados Associados / Diretoria'
            dados_depara = buscar_dados(de_para_df, data['coordenacao'])

            if dados_depara:
                envolvido = dados_depara.get('Envolvido', envolvido)
                escritorio = dados_depara.get('Escritório', escritorio)
            else:
                log_step(f"[ERRO] Não foi possível encontrar dados de-para para {str(data['coordenacao'])}")

            # Navega para a página de cadastro
            if not navegar_para_pagina_cadastro(page, idadamento, idprocesso):
                continue

            # Preenche o formulário
            preencher_formulario(page, escritorio, envolvido)

            # Verifica se a página de erro foi carregada
            if verificar_pagina_erro(page):
                set_data_from_db(idadamento)
                log_step(f"Tarefa criada com sucesso para o processo={processo}, coordenação={envolvido}, id andamento={idadamento}")
            else:
                log_step(f"[ERRO] Falha ao criar tarefa para id andamento={idadamento}")

        except Exception as e:
            log_step(f"[ERRO] Erro inesperado: {e}")
            if not faz_login(page):
                break


def navegar_para_pagina_cadastro(page, idadamento, idprocesso):
    '''Navega para a página de cadastro de tarefas.'''
    try:
        page.goto(f'https://example.com/tarefas/createFromAndamento?idAnd={idadamento}&pId={idprocesso}', timeout=15000) 
        return True
    except Exception as e:  
        log_step(f"[ERRO] Falha ao navegar para a página de cadastro: {e}")
        return False


def preencher_formulario(page, escritorio, envolvido):
    '''Preenche o formulário no LawSystem.'''
    try:
        # Preenche o campo "SourceOfficeText"
        page.fill("input#SourceOfficeText", escritorio)
        page.keyboard.press("Enter")
        time.sleep(1)
        for _ in range(4):
            page.keyboard.press("ArrowDown")
            time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(1)

        # Preenche o campo "ResponsibleOfficeText"
        page.fill("input#ResponsibleOfficeText", escritorio)
        page.keyboard.press("Enter")
        time.sleep(1)
        for _ in range(4):
            page.keyboard.press("ArrowDown")
            time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(1)

        # Preenche o campo "Descricao"
        page.fill("input#Descricao", "Conferir expediente no PJe")

        # Preenche o campo "TipoText"
        page.fill("input#TipoText", "Prazo Agendado")
        page.keyboard.press("Enter")
        time.sleep(1)
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(1)

        # Preenche o campo "DtInicial" com a data atual
        page.fill("input#DtInicial", datetime.now().strftime("%d/%m/%Y"))

        # Preenche o campo "HrFinal" com um horário padrão
        page.fill("input#HrFinal", "23:00:00")

        # Preenche o campo "DtFinal" com a data de amanhã
        page.fill("input#DtFinal", (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y"))

        # Preenche o campo de envolvidos, navegando por 6 tabs no for
        for _ in range(7):
            page.keyboard.press("Tab")
            time.sleep(0.5)
        # Preencher o input onde o cursor parou
        page.keyboard.type(envolvido)
        page.keyboard.press("Enter")
        time.sleep(1)
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(1)

        # Clicar no botão "Excluir lembrete"
        page.wait_for_selector('span[title="Remover lembrete"]')
        page.click('span[title="Remover lembrete"]')

        # Clicar no botão "Excluir lembrete"
        page.wait_for_selector('span[title="Remover lembrete"]')
        page.click('span[title="Remover lembrete"]')

        # Clicar no checkbox para não manter os dados após salvar
        page.click("input#Maintain")

        # Clicar no botão "Salvar"
        page.click('button[name="ButtonSave"][value="1"]')

    except Exception as e:  
        log_step(f"[ERRO] Erro ao preencher o formulário: {e}")


def verificar_pagina_erro(page):
    '''Verifica se a página de erro foi carregada.'''
    try:
        conteudo_pagina = page.text_content("body")
        return "A página solicitada não foi encontrada." in conteudo_pagina
    except Exception as e:
        log_step(f"[ERRO] Erro ao verificar a página: {e}")
        return False


def main():
    '''Inicia o processo.'''
    try:
        results = fetch_data_from_db()
        if not results:
            log_step("Nenhum registro encontrado. Processo encerrado.")
            return

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            try:
                if not faz_login(page):
                    raise ValueError("Login não foi realizado")

                base_dir = os.path.dirname(os.path.abspath(__file__))
                caminho = os.path.join(base_dir, 'resource', 'DE_PARA_ESCRITORIO_RESPONSAVEL.xlsx')
                if not os.path.exists(caminho):
                    raise FileNotFoundError(f"Arquivo de de-para não encontrado: {caminho}")

                de_para_df = carregar_de_para(caminho)
                processar_resultados(results, page, de_para_df)

            except ValueError as e:
                log_step(f"[ERRO] {e}")
            except Exception as e:
                log_step(f"[ERRO] Erro inesperado: {e}")
            finally:
                browser.close()
    except Exception as e:
        log_step(f"[ERRO] Erro inesperado: {e}")
    finally:
        input("Pressione Enter para encerrar...")

def init():
    '''Função principal de inicialização.'''
    # Configuração do Playwright antes de executar o programa
    configurar_playwright()
    main()

if __name__ == "__main__":
    init()
