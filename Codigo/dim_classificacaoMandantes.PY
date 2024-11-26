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
# Inserir dados na tabela dim_classificacaoMandante
def insert_classificacao_mandante(conn):
    try:
        cursor = conn.cursor()

        # Selecionar combinações únicas de colunas da tabela stg_jogos
        query_select = """
            SELECT DISTINCT 
                colocacao_mandante, time_mandante, ano_campeonato, rodada
            FROM public.stg_jogos
            WHERE colocacao_mandante IS NOT NULL 
              AND time_mandante IS NOT NULL 
              AND ano_campeonato IS NOT NULL 
              AND rodada IS NOT NULL;
        """
        cursor.execute(query_select)
        classificacoes = cursor.fetchall()

        # Verificar e inserir na tabela dim_classificacaoMandante
        query_check = """
            SELECT 1 FROM public.dim_classificacaoMandante
            WHERE colocacao_mandante = %s 
              AND time_mandante = %s
              AND ano_campeonato = %s
              AND rodada = %s;
        """
        query_insert = """
            INSERT INTO public.dim_classificacaoMandante (
                colocacao_mandante, time_mandante, ano_campeonato, rodada
            ) VALUES (%s, %s, %s, %s);
        """

        for classificacao in classificacoes:
            cursor.execute(query_check, classificacao)
            if cursor.fetchone() is None:  # Se não existe, insere
                cursor.execute(query_insert, classificacao)
                print(f"Registro {classificacao} inserido.")
            else:
                print(f"Registro {classificacao} já existe na tabela.")

        # Commit das alterações
        conn.commit()
        print(f"Inserção concluída com sucesso!")

    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir dados: {e}")
    finally:
        cursor.close()


# Execução principal
if __name__ == "__main__":
    conn = connect_to_db()
    try:
        insert_classificacao_mandante(conn)
    finally:
        conn.close()

    print("Executado com sucesso!")





