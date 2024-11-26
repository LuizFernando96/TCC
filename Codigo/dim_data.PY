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


# Inserir datas na tabela dim_data   
def insert_datas(conn):
    try:
        cursor = conn.cursor()
        
        # Selecionar datas únicas da tabela stg_jogos
        query_select = """
            SELECT DISTINCT data, ano_campeonato 
            FROM public.stg_jogos 
            WHERE data IS NOT NULL;
        """
        cursor.execute(query_select)
        registros = cursor.fetchall()
        
        # Verificar e inserir na tabela dim_data
        query_check = "SELECT 1 FROM public.dim_data WHERE data = %s;"
        query_insert = "INSERT INTO public.dim_data (data, ano_campeonato) VALUES (%s, %s);"
        
        for data, ano_campeonato in registros:
            cursor.execute(query_check, (data,))
            if cursor.fetchone() is None:  # Se a data não existe, insere o registro completo
                cursor.execute(query_insert, (data, ano_campeonato))
                print(f"Registro '{data}, {ano_campeonato}' inserido.")
            else:
                print(f"Data '{data}' já existe na tabela.")

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
        insert_datas(conn)
    finally:
        conn.close()

    print("Executado com sucesso!")
