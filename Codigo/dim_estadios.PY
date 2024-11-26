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


# Inserir datas na tabela dim_estadios   
def insert_estadios(conn):
    try:
        cursor = conn.cursor()
        
        # Selecionar datas únicas da tabela stg_jogos
        query_select = """
            SELECT DISTINCT estadio, publico_max 
            FROM public.stg_jogos 
            WHERE estadio IS NOT NULL;
        """
        cursor.execute(query_select)
        registros = cursor.fetchall()
        
        # Verificar e inserir na tabela dim_data
        query_check = "SELECT 1 FROM public.dim_estadios WHERE estadio = %s;"
        query_insert = "INSERT INTO public.dim_estadios (estadio, publico_max) VALUES (%s, %s);"
        
        for estadio, publico_max in registros:
            cursor.execute(query_check, (estadio,))
            if cursor.fetchone() is None:  # Se a estadio não existe, insere o registro completo
                cursor.execute(query_insert, (estadio, publico_max))
                print(f"Registro '{estadio}, {publico_max}' inserido.")
            else:
                print(f"Dado '{estadio}' já existe na tabela.")

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
        insert_estadios(conn)
    finally:
        conn.close()

    print("Executado com sucesso!")
