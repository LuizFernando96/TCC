import psycopg2
print("Mensagem de teste", flush=True)
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


# Inserir árbitros na tabela dim_arbitros
def insert_arbitros(conn):
    try:
        cursor = conn.cursor()
        
        # Selecionar árbitros únicos da tabela stg_jogos
        query_select = "SELECT DISTINCT arbitro FROM public.stg_jogos WHERE arbitro IS NOT NULL;"
        cursor.execute(query_select)
        arbitros = cursor.fetchall()
        
        # Verificar e inserir na tabela dim_arbitros
        query_check = "SELECT 1 FROM public.dim_arbitros WHERE arbitro = %s;"
        query_insert = "INSERT INTO public.dim_arbitros (arbitro) VALUES (%s);"
        
        for (arbitro,) in arbitros:
            cursor.execute(query_check, (arbitro,))
            if cursor.fetchone() is None:  # Se não existe, insere
                cursor.execute(query_insert, (arbitro,))
                print(f"Árbitro '{arbitro}' inserido.")
            else:
                print(f"Árbitro '{arbitro}' já existe na tabela.")

        # Commit das alterações
        conn.commit()
        print(f"Inserção concluída com sucesso!")

    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir árbitros: {e}")
    finally:
        cursor.close()

# Execução principal
if __name__ == "__main__":
    conn = connect_to_db()
    try:
        insert_arbitros(conn)
    finally:
        conn.close()

    print("Executado com sucesso!")


