import pandas as pd


class DeliveryBuilder:

    CODIGO_EMPRESA = {
        "D'onofrio": "001",
        "Nestlé": "002"
    }

    DIAS_SEMANA = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]

    MAPA_DIAS = {
        "LUNES": 1, "MARTES": 2, "MIERCOLES": 3,
        "JUEVES": 4, "VIERNES": 5, "SABADO": 6, "DOMINGO": 7
    }

    MAPA_COLUMNAS = {
        1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu",
        5: "Fri", 6: "Sat", 7: "Sun"
    }

    COLUMNAS_SALIDA = [
        "UNB", "ClientCode", "Document", "Exception",
        "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun",
        "MinValueMon", "MinValueTue", "MinValueWed", "MinValueThu", "MinValueFri", "MinValueSat", "MinValueSun",
        "AddAmountMon", "AddAmountTue", "AddAmountWed", "AddAmountThu", "AddAmountFri", "AddAmountSat", "AddAmountSun",
        "DeliveryFrequency", "ClickAndCollectActive"
    ]

    @classmethod
    def _generar_codigos(cls, df, empresa):
        valor = str(df["empresa"].iloc[0]).strip()
        ajuste = -1 if valor.lstrip("0") == "22" else 0

        columnas_longitud = {
            'empresa': 3 + ajuste,
            'division': 3 + ajuste,
            'oficina': 3 + ajuste,
            'domicilio': 3,
            'codigo_cliente': 6
        }

        for columna, longitud in columnas_longitud.items():
            df[columna] = df[columna].astype(str).str.zfill(longitud)

        if "COD CLIENTE BEES" not in df.columns:
            df["COD CLIENTE BEES"] = (
                cls.CODIGO_EMPRESA.get(empresa, "000")
                + "-"
                + df['empresa']
                + df['division']
                + df['oficina']
                + "-"
                + df['codigo_cliente']
                + df['domicilio']
            )

        return df

    @classmethod
    def _normalizar_dias(cls, df_filtrado):
        df_filtrado["dia_visita"] = (
            df_filtrado["dia_visita"]
            .astype(str)
            .str.replace(" ", "", regex=False)
            .str.replace("SEMANA1", "", regex=False)
            .str.replace("SEMANA2", "", regex=False)
            .str.upper()
        )

        df_filtrado["dia_visita"] = df_filtrado["dia_visita"].apply(
            lambda x: cls.DIAS_SEMANA if "TODOSLOSDIAS" in str(x) else str(x)
        )
        df_filtrado["dia_visita"] = df_filtrado["dia_visita"].apply(
            lambda x: x if isinstance(x, list) else str(x).replace(",", "Y")
        )
        df_filtrado["dia_visita"] = df_filtrado["dia_visita"].apply(
            lambda x: x if isinstance(x, list) else str(x).split("Y")
        )

        df_filtrado = df_filtrado.explode("dia_visita", ignore_index=True)
        df_filtrado["dia_visita"] = df_filtrado["dia_visita"].str.strip().str.upper()
        return df_filtrado.drop_duplicates().reset_index(drop=True)

    @classmethod
    def _construir_base_csv(cls, df_base):
        df_csv = pd.DataFrame(columns=cls.COLUMNAS_SALIDA)
        df_csv["UNB"] = df_base["COD CLIENTE BEES"].str[2:10]
        df_csv["ClientCode"] = df_base["codigo_cliente"]
        df_csv["Document"] = df_base["COD CLIENTE BEES"]
        df_csv["Exception"] = True
        df_csv[["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]] = 0
        df_csv[[
            "MinValueMon", "MinValueTue", "MinValueWed", "MinValueThu",
            "MinValueFri", "MinValueSat", "MinValueSun",
            "AddAmountMon", "AddAmountTue", "AddAmountWed", "AddAmountThu",
            "AddAmountFri", "AddAmountSat", "AddAmountSun"
        ]] = 0
        df_csv["DeliveryFrequency"] = 7
        df_csv["ClickAndCollectActive"] = False
        return df_csv

    @classmethod
    def _asignar_dias(cls, df_csv, df_filtrado):
        df_filtrado["dia_num"] = df_filtrado["dia_visita"].map(cls.MAPA_DIAS)
        df_filtrado["dia_sumado"] = df_filtrado["dia_num"] + 1
        df_filtrado.loc[df_filtrado["dia_sumado"] >= 7, "dia_sumado"] = 1

        df_dias = df_filtrado.groupby("COD CLIENTE BEES")["dia_sumado"].apply(list).reset_index()

        df_csv.set_index("Document", inplace=True)
        for _, row in df_dias.iterrows():
            doc = row["COD CLIENTE BEES"]
            for d in row["dia_sumado"]:
                if doc in df_csv.index:
                    col = cls.MAPA_COLUMNAS.get(d)
                    if col:
                        df_csv.at[doc, col] = 1
        df_csv.reset_index(inplace=True)
        return df_csv

    @classmethod
    def construir(cls, df, empresa):
        df = df.copy()
        df = cls._generar_codigos(df, empresa)

        df_filtrado = df[["COD CLIENTE BEES", "dia_visita"]].copy()
        df_filtrado = cls._normalizar_dias(df_filtrado)

        df_base = df[["codigo_cliente", "COD CLIENTE BEES"]].drop_duplicates().reset_index(drop=True)
        df_csv = cls._construir_base_csv(df_base)
        df_csv = cls._asignar_dias(df_csv, df_filtrado)

        return df_csv[cls.COLUMNAS_SALIDA]
