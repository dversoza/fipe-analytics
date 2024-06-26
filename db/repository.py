def insert_price(conn, car_price: dict):
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO car_price (
            marca,
            modelo,
            ano_modelo,
            combustivel,
            codigo_fipe,
            mes_referencia,
            ref_date,
            autenticacao,
            tipo_veiculo,
            sigla_combustivel,
            data_consulta,
            valor
        ) VALUES (
            %(Marca)s,
            %(Modelo)s,
            %(AnoModelo)s,
            %(Combustivel)s,
            %(CodigoFipe)s,
            %(MesReferencia)s,
            %(RefDate)s,
            %(Autenticacao)s,
            %(TipoVeiculo)s,
            %(SiglaCombustivel)s,
            %(DataConsulta)s,
            %(Valor)s
        ) ON CONFLICT (autenticacao) DO UPDATE SET
            ano_modelo = EXCLUDED.ano_modelo,
            codigo_fipe = EXCLUDED.codigo_fipe,
            mes_referencia = EXCLUDED.mes_referencia,
            ref_date = EXCLUDED.ref_date,
            autenticacao = EXCLUDED.autenticacao,
            data_consulta = EXCLUDED.data_consulta,
            valor = EXCLUDED.valor
        """,
        car_price,
    )

    conn.commit()

    cur.close()

    return conn
