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


# Inserir datas na tabela dim_timeMandante   
def insert_timeMandante(conn):
    try:
        cursor = conn.cursor()
        
        # Selecionar datas únicas da tabela stg_jogos
        query_select = """
            SELECT DISTINCT time_mandante, valor_equipe_titular_mandante, idade_media_titular_mandante 
            FROM public.stg_jogos 
            WHERE time_mandante IS NOT NULL;
        """
        cursor.execute(query_select)
        registros = cursor.fetchall()
        
        # Verificar e inserir na tabela dim_timeMandante
        query_check = "SELECT 1 FROM public.dim_timeMandante WHERE time_mandante = %s;"
        query_insert = "INSERT INTO public.dim_timeMandante (time_mandante, valor_equipe_titular_mandante, idade_media_titular_mandante) VALUES (%s, %s, %s);"
        
        for time_mandante, valor_equipe_titular_mandante, idade_media_titular_mandante in registros:
            cursor.execute(query_check, (time_mandante,))
            if cursor.fetchone() is None:  # Se a data não existe, insere o registro completo
                cursor.execute(query_insert, (time_mandante, valor_equipe_titular_mandante, idade_media_titular_mandante))
                print(f"Registro '{time_mandante}, {valor_equipe_titular_mandante}, {idade_media_titular_mandante}' inserido.")
            else:
                print(f"Data '{time_mandante}' já existe na tabela.")

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
        insert_timeMandante(conn)
    finally:
        conn.close()

    print("Executado com sucesso!")
