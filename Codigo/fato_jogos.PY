import psycopg2

# Configurações do banco de dados
db_config = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "123"
}

# Conexão com o banco de dados
def connect_to_db():
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        raise

# Inserir dados na tabela fato_jogos
def insert_fato_jogos(conn):
    try:
        cursor = conn.cursor()

        # Selecionar combinações únicas de colunas da tabela stg_jogos
        query_select = """
            SELECT DISTINCT 
                ano_campeonato, rodada, time_mandante, time_visitante,
                arbitro, chutes_bola_parada_mandante, chutes_bola_parada_visitante,
                chutes_fora_mandante, chutes_fora_visitante, chutes_mandante, chutes_visitante,
                colocacao_mandante, colocacao_visitante, data, defesas_mandante, defesas_visitante,
                escanteios_mandante, escanteios_visitante, estadio, faltas_mandante, faltas_visitante,
                gols_1_tempo_mandante, gols_1_tempo_visitante, gols_mandante, gols_visitante,
                idade_media_titular_mandante, idade_media_titular_visitante, impedimentos_mandante,
                impedimentos_visitante, publico, tecnico_mandante, tecnico_visitante,
                valor_equipe_titular_mandante, valor_equipe_titular_visitante
            FROM public.stg_jogos
            WHERE ano_campeonato IS NOT NULL 
              AND rodada IS NOT NULL 
              AND time_mandante IS NOT NULL 
              AND time_visitante IS NOT NULL;
        """
        cursor.execute(query_select)
        jogos = cursor.fetchall()

        # Verificar e inserir na tabela fato_jogos
        query_check = """
            SELECT 1 FROM public.fato_jogos
            WHERE ano_campeonato = %s 
              AND rodada = %s
              AND time_mandante = %s
              AND time_visitante = %s;
        """
        query_insert = """
            INSERT INTO public.fato_jogos (
                ano_campeonato, rodada, time_mandante, time_visitante, arbitro, 
                chutes_bola_parada_mandante, chutes_bola_parada_visitante, chutes_fora_mandante, 
                chutes_fora_visitante, chutes_mandante, chutes_visitante, colocacao_mandante, 
                colocacao_visitante, data, defesas_mandante, defesas_visitante, escanteios_mandante, 
                escanteios_visitante, estadio, faltas_mandante, faltas_visitante, gols_1_tempo_mandante, 
                gols_1_tempo_visitante, gols_mandante, gols_visitante, idade_media_titular_mandante, 
                idade_media_titular_visitante, impedimentos_mandante, impedimentos_visitante, publico, 
                tecnico_mandante, tecnico_visitante, valor_equipe_titular_mandante, 
                valor_equipe_titular_visitante
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        for jogo in jogos:
            # Verifica duplicidade com base nas colunas chave
            cursor.execute(query_check, jogo[:4])
            if cursor.fetchone() is None:  # Se não existe, insere
                cursor.execute(query_insert, jogo)
                print(f"Registro {jogo[:4]} inserido.")
            else:
                print(f"Registro {jogo[:4]} já existe na tabela.")

        # Commit das alterações
        conn.commit()
        print("Inserção concluída com sucesso!")

    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir dados: {e}")
    finally:
        cursor.close()


# Execução principal
if __name__ == "__main__":
    conn = connect_to_db()
    try:
        insert_fato_jogos(conn)
    finally:
        conn.close()

    print("Executado com sucesso!")
