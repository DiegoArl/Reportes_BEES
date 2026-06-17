import pandas as pd


ENCABEZADO = [
    'fecha', 'nombrecliente', 'vendedor', 'nombrevendedor',
    'vtadvo', 'canal', 'tipo_pedido', 'numero_pedido',
    'DescripcionCategoria', 'codigoproducto', 'descrpcionproducto',
    'cajas', 'soles'
]


class IndicadorAdopcion:

    @staticmethod
    def _codigo_standard(df_usuarios):
        if df_usuarios is None:
            raise ValueError("df_usuarios no puede ser None")
        partes = df_usuarios["Codigo"].str.split("-", expand=True)
        if partes.shape[1] != 2:
            return False
        return ((partes[0].str.len() == 6) & (partes[1].str.len() == 5)).all()

    @staticmethod
    def _procesar_modulo(df, codigos_permitidos=None):
        df = df.copy()[ENCABEZADO]
        df['tipo_pedido'] = df['tipo_pedido'].apply(
            lambda x: 'NON BEES' if not isinstance(x, str) or x[:3] != 'B2B' else x
        )

        mask_producto = (
            ~df["codigoproducto"].astype(str).str.startswith("70") &
            ~df["codigoproducto"].astype(str).str.startswith("90")
        )
        if codigos_permitidos is not None:
            mask_producto |= df["codigoproducto"].astype(str).isin(codigos_permitidos)

        df = df[(df["vtadvo"] == "V") & mask_producto]
        df["fecha"] = pd.to_datetime(df["fecha"], format="%Y/%m/%d", errors="coerce")
        df["mes"] = df["fecha"].dt.to_period("M").astype(str)
        df["mes_n"] = df['mes'].astype(str).str[-2:]
        return df

    @staticmethod
    def _modelar(df_modulo):
        df = df_modulo.groupby(["Codigo", "Rep. Ventas", "Supervisor", "tipo_pedido"]).agg(
            pedidos=("numero_pedido", "nunique")
        ).reset_index()

        df = df.pivot_table(
            index=["Codigo", "Rep. Ventas", "Supervisor"],
            columns=["tipo_pedido"],
            values=["pedidos"],
            aggfunc="sum",
            fill_value=0
        ).reset_index()

        df.columns = [
            f"{col1}_{col2}" if col2 != "" else col1
            for col1, col2 in df.columns.to_flat_index()
        ]

        df['pedidos_total'] = 0
        for c in df.columns:
            partes = c.split("_")
            if len(partes) > 1 and partes[0] == "pedidos" and partes[1] != 'total':
                df['pedidos_total'] += df[c]

        cols_b2b = df.filter(like='B2B').columns
        df['Adopción BEES'] = df[cols_b2b].sum(axis=1) / df['pedidos_total']
        df = df.sort_values(by='Adopción BEES', ascending=False).reset_index(drop=True)
        df["Adopción BEES"] = df["Adopción BEES"].apply(
            lambda x: f"{x*100:.2f}%" if x <= 1 else f"{x:.2f}%"
        )
        return df

    @staticmethod
    def _color(val, thresholds=(30, 60, 80)):
        if val is None:
            return ""
        try:
            v = float(str(val).replace("%", ""))
        except Exception:
            return ""
        t1, t2, t3 = thresholds
        if v < t1:
            return "background-color: rgb(248,105,108)"
        elif v < t2:
            return "background-color: rgb(251,233,130)"
        elif v < t3:
            return "background-color: rgb(251,190,123)"
        return "background-color: rgb(99,190,123)"

    @classmethod
    def aplicar_estilos(cls, df):
        return df.style.map(cls._color, subset=["Adopción BEES"])

    @classmethod
    def calcular(cls, df_usuarios, df_modulo, fecha_inicio=None, fecha_fin=None):
        val_standard = cls._codigo_standard(df_usuarios)

        if fecha_inicio:
            df_modulo = df_modulo[df_modulo["fecha"] >= pd.to_datetime(fecha_inicio)]
        if fecha_fin:
            df_modulo = df_modulo[df_modulo["fecha"] <= pd.to_datetime(fecha_fin)]

        df_user = df_usuarios[["Codigo", "Rep. Ventas", "Supervisor"]].copy()
        df_modulo = cls._procesar_modulo(df_modulo)

        if val_standard:
            df_user["vendedor"] = df_user["Codigo"].astype(int)
        else:
            df_user["vendedor"] = df_user["Codigo"].str.split("-").str[-1].str[2:].astype(int)

        df_modulo_filtrado = df_modulo[df_modulo["vendedor"].isin(df_user["vendedor"])]
        df_modulo_filtrado = df_user.merge(
            df_modulo_filtrado, on="vendedor", how="left"
        ).drop(columns=["vendedor"])

        return cls._modelar(df_modulo_filtrado)
