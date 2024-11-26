from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import os
import pandas as pd
import os
import psycopg2

#Caminhos
planilha = r"E:\Luiz\Cursos\SistemasDeInformacao\8Periodo\TCC2\Arquivos"
repositorio = planilha + r"\Repositorio/"

 
#VARIÁVEIS E ARGUMENTOS PARA O CHROME
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
 
#CONFIGURANDO O NAVEGADOR
chrome_options.add_experimental_option("prefs", {"download.default_directory" : repositorio}) #CONFIGURANTDO DIRETÓRIO DOS DOWNLOADS DO CHROME
service = ChromeService(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=service, options=chrome_options)
w2 = WebDriverWait(navegador, 30)  #TEMPO EM SEGUNDOS QUE O SCRIPT AGUARDARÁ O ELEMENTE FICAR DISPONÍVEL
url = 'https://basedosdados.org/dataset/c861330e-bca2-474d-9073-bc70744a1b23?table=18835b0d-233e-4857-b454-1fa34a81b4fa'

# Configurações do banco de dados
db_config = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "123"
}

#Função para scrolar página
def Scrolando(IdInput): #Scrolando a página até que o elemento fique visível
    element = navegador.find_element(By.XPATH, IdInput)
    navegador.execute_script("arguments[0].scrollIntoView();", element)
    sleep(2)

def ApagandoArquivosPasta(repositorio):
    # Verificar se a pasta existe
    if os.path.exists(repositorio):
        # Listar todos os arquivos na pasta
        arquivos = [os.path.join(repositorio, arquivo) for arquivo in os.listdir(repositorio) if os.path.isfile(os.path.join(repositorio, arquivo))]

        # Excluir cada arquivo
        for arquivo in arquivos:
            try:
                os.remove(arquivo)
            except Exception as e:
                print(f"Erro ao excluir o arquivo {arquivo}: {e}")
    else:
        print(f"A pasta {repositorio} não foi encontrada.")

def BaixandoArquivo(navegador, url, w2):
    #FAZER LOGIN
    navegador.get(url+'login') #ACESSANDO O SITE
    navegador.maximize_window() #MAXIMIZANDO O NAVEGADOR

    sleep(5) #AGUARDANDO 5 SEGUNDOS PARA QUE A PÁGINA CARREGUE TODAS AS INFORMAÇÕES
    w2.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="tabs-69--tabpanel-0"]/div/div[1]/div[1]/div/div[1]/p'))).click() #CLICANDO EM "BRASILEIRÃO SÉRIA A"

    sleep(5) #AGUARDANDO 5 SEGUNDOS PARA QUE A PÁGINA CARREGUE TODAS AS INFORMAÇÕES
    Scrolando('//*[@id="tabs-59--tab-1"]') #DESCENDO A PÁGINA WEB ATÉ QUE "DOWNLOAD" FIQUE VISÍVEL
    w2.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="tabs-59--tab-1"]'))).click() #CLICANDO EM "DOWNLOAD"

    sleep(5) #AGUARDANDO 5 SEGUNDOS PARA QUE A PÁGINA CARREGUE TODAS AS INFORMAÇÕES
    Scrolando('//*[@id="download_table"]/div/div[2]/p/a') #DESCENDO A PÁGINA WEB ATÉ QUE "DOWNLOAD DA TABELA" FIQUE VISÍVEL
    w2.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="download_table"]/a'))).click() #CLICANDO EM "DOWNLOAD DA TABELA"
    
    sleep(10) #AGUARDANDO 10 SEGUNDOS PARA QUE A PÁGINA CARREGUE TODAS AS INFORMAÇÕES
    navegador.quit() # FECHANDO O NAVEGADORT

def Descompactando(repositorio):
    #Localizando arquivo
    csv_file = [f for f in os.listdir(repositorio) if f.endswith('.csv.gz')][0]  #LOCALIZANDO O ARQUIVO DO TIPO CSV.GZ NO CAMINHO ESPECIFICADO
    csv_path = os.path.join(repositorio, csv_file) #DEFININDO CAMINHO COMPLETO DO ARQUIVO
    
    df = pd.read_csv(csv_path, sep=',')  #CARREGANDO O ARQUIVO E DESCOMPACTANDO EM UM DATAFRAME UTILIZANDO A BIBLIOTECA PANDAS
    return df #RETORNANDO O DATAFRAME

# Conexão com o banco de dados
def connect_to_db():
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        raise

# Função para inserir dados na tabela
def insert_data(conn, table, data):
    cursor = conn.cursor()
    cols = ", ".join(data.keys())
    vals = ", ".join(["%s"] * len(data))
    #print(f"\ndata: {data}\n")
    query = f"INSERT INTO {table} ({cols}) VALUES ({vals}) ON CONFLICT DO NOTHING"
    try:
        cursor.execute(query, list(data.values()))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao executar query: {e}")
        print(f"\ndata: {data}\n")
    finally:
        cursor.close()

#Converte valores NaN ou None em None para o banco de dados.
def handle_nan(data):
    return {k: (None if pd.isna(v) else v) for k, v in data.items()}

#Apagando arquivos antigos
ApagandoArquivosPasta(repositorio)

#Baixando o arquivo
BaixandoArquivo(navegador, url, w2)

#Tranformando arquivo
DataFrame = Descompactando(repositorio)

# Transformações e carregamento no banco
conn = connect_to_db()

try:
    for index, row in DataFrame.iterrows():
        #stg_jogos
        jogos_row = {
            "arbitro": row["arbitro"],
            "ano_campeonato": row["ano_campeonato"],
            "chutes_bola_parada_mandante": row["chutes_bola_parada_mandante"],
            "chutes_bola_parada_visitante": row["chutes_bola_parada_visitante"],
            "chutes_fora_mandante": row["chutes_fora_mandante"],
            "chutes_fora_visitante": row["chutes_fora_visitante"],
            "chutes_mandante": row["chutes_mandante"],
            "chutes_visitante": row["chutes_visitante"],
            "colocacao_mandante": row["colocacao_mandante"],
            "colocacao_visitante": row["colocacao_visitante"],
            "data": row["data"],
            "defesas_mandante": row["defesas_mandante"],
            "defesas_visitante": row["defesas_visitante"],
            "escanteios_mandante": row["escanteios_mandante"],
            "escanteios_visitante": row["escanteios_visitante"],
            "estadio": row["estadio"],
            "faltas_mandante": row["faltas_mandante"],
            "faltas_visitante": row["faltas_visitante"],
            "gols_1_tempo_mandante": row["gols_1_tempo_mandante"],
            "gols_1_tempo_visitante": row["gols_1_tempo_visitante"],
            "gols_mandante": row["gols_mandante"],
            "gols_visitante": row["gols_visitante"],
            "idade_media_titular_mandante": row["idade_media_titular_mandante"],
            "idade_media_titular_visitante": row["idade_media_titular_visitante"],
            "impedimentos_mandante": row["impedimentos_mandante"],
            "impedimentos_visitante": row["impedimentos_visitante"],
            "publico": row["publico"],
            "publico_max": row["publico_max"],
            "rodada": row["rodada"],
            "tecnico_mandante": row["tecnico_mandante"],
            "tecnico_visitante": row["tecnico_visitante"],
            "time_mandante": row["time_mandante"],
            "time_visitante": row["time_visitante"],
            "valor_equipe_titular_mandante": row["valor_equipe_titular_mandante"],
            "valor_equipe_titular_visitante": row["valor_equipe_titular_visitante"] 
        }
        jogos_row = handle_nan(jogos_row)
        insert_data(conn, "stg_jogos", jogos_row) 

finally:
    conn.close()

print("Executado com sucesso!")