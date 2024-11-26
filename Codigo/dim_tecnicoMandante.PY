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


# Inserir tecnicos mandantes na tabela dim_tecnicoMandante
def insert_tecnicoMandante(conn):
    try:
        cursor = conn.cursor()
        
        # Selecionar árbitros únicos da tabela stg_jogos
        query_select = "SELECT DISTINCT tecnico_mandante FROM public.stg_jogos WHERE tecnico_mandante IS NOT NULL;"
        cursor.execute(query_select)
        registros = cursor.fetchall()
        
        # Verificar e inserir na tabela dim_arbitros
        query_check = "SELECT 1 FROM public.dim_tecnicoMandante WHERE tecnico_mandante = %s;"
        query_insert = "INSERT INTO public.dim_tecnicoMandante (tecnico_mandante) VALUES (%s);"
        
        for (registro,) in registros:
            cursor.execute(query_check, (registro,))
            if cursor.fetchone() is None:  # Se não existe, insere
                cursor.execute(query_insert, (registro,))
                print(f"Registro '{registro}' inserido.")
            else:
                print(f"Registro '{registro}' já existe na tabela.")

        # Commit das alterações
        conn.commit()
        print(f"Inserção concluída com sucesso!")

    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir registro: {e}")
    finally:
        cursor.close()

# Execução principal
if __name__ == "__main__":
    conn = connect_to_db()
    try:
        insert_tecnicoMandante(conn)
    finally:
        conn.close()

    print("Executado com sucesso!")


