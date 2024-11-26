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


# Inserir datas na tabela dim_timeVisitante
def insert_timeVisitante(conn):
    try:
        cursor = conn.cursor()
        
        # Selecionar datas únicas da tabela stg_jogos
        query_select = """
            SELECT DISTINCT time_visitante, valor_equipe_titular_visitante, idade_media_titular_visitante 
            FROM public.stg_jogos 
            WHERE time_visitante IS NOT NULL;
        """
        cursor.execute(query_select)
        registros = cursor.fetchall()
        
        # Verificar e inserir na tabela dim_timeVisitante
        query_check = "SELECT 1 FROM public.dim_timeVisitante WHERE time_visitante = %s;"
        query_insert = "INSERT INTO public.dim_timeVisitante (time_visitante, valor_equipe_titular_visitante, idade_media_titular_visitante) VALUES (%s, %s, %s);"
        
        for time_visitante, valor_equipe_titular_visitante, idade_media_titular_visitante in registros:
            cursor.execute(query_check, (time_visitante,))
            if cursor.fetchone() is None:  # Se a data não existe, insere o registro completo
                cursor.execute(query_insert, (time_visitante, valor_equipe_titular_visitante, idade_media_titular_visitante))
                print(f"Registro '{time_visitante}, {valor_equipe_titular_visitante}, {idade_media_titular_visitante}' inserido.")
            else:
                print(f"Data '{time_visitante}' já existe na tabela.")

        # Commit das alterações
        conn.commit()
        print("Inserção concluída com sucesso!")

    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir datas: {e}")
    finally:
        cursor.close()

# Execução principal
if __name__ == "__main__":
    conn = connect_to_db()
    try:
        insert_timeVisitante(conn)
    finally:
        conn.close()

    print("Executado com sucesso!")
