from psycopg import connect


def create_db_connection():
    postgres_conn = connect(
        dbname="mydb",
        user="myuser",
        password="mypassword",
        host="localhost",
        port="5432",
    )

    return postgres_conn


def create_db(conn):

    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tabela_referencia (
            fipe_id VARCHAR(10) PRIMARY KEY,
            display_name VARCHAR(255),
            mes INTEGER,
            ano INTEGER
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS marca (
            fipe_id VARCHAR(10) PRIMARY KEY,
            display_name VARCHAR(255)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS modelo (
            fipe_id VARCHAR(10),
            marca_id VARCHAR(10) REFERENCES marca(fipe_id),
            display_name VARCHAR(255),
            tipo_veiculo INTEGER,

            CONSTRAINT modelo_pk PRIMARY KEY (fipe_id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ano_modelo (
            modelo_id VARCHAR(10) REFERENCES modelo(fipe_id),
            fipe_id VARCHAR(10),
            ano INTEGER,
            tipo_combustivel INTEGER,
            display_name VARCHAR(255),

            CONSTRAINT ano_modelo_pk PRIMARY KEY (modelo_id, fipe_id)
        )

        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS preco (
            id SERIAL PRIMARY KEY,
            marca_id VARCHAR(10) REFERENCES marca(fipe_id),
            modelo_id VARCHAR(10) REFERENCES modelo(fipe_id),
            ano_modelo_id VARCHAR(10),
            codigo_tipo_veiculo INTEGER,
            codigo_tabela_referencia VARCHAR(10) REFERENCES tabela_referencia(fipe_id),
            autenticacao VARCHAR(255) UNIQUE,
            data_consulta VARCHAR(255),
            mes_referencia VARCHAR(255),
            valor FLOAT,
            codigo_fipe_veiculo VARCHAR(10),
            raw_data JSON,

            FOREIGN KEY (modelo_id, ano_modelo_id) REFERENCES ano_modelo(modelo_id, fipe_id)
        )
        """
    )

    conn.commit()

    cur.close()

    return conn
