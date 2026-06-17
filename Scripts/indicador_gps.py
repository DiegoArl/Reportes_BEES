import pandas as pd


class IndicadorGPS:

    @staticmethod
    def _color(val, thresholds=(30, 50, 70)):
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
        return df.style.map(
            cls._color,
            subset=["% GPS Ok visitas", "% GPS Ok > 2 min visitas"]
        )

    @staticmethod
    def unir_tablas(df_usuarios, df_checkin, df_visitas):
        if df_usuarios is None:
            raise ValueError("df_usuarios no puede ser None")

        df_base = df_usuarios[["Codigo", "Rep. Ventas", "Supervisor"]]

        df_merge = pd.merge(
            df_base,
            df_checkin[["Codigo", "Visitas planificadas", "Visitas completadas", "Primer check-in"]],
            on="Codigo",
            how="left"
        )

        df_merge = pd.merge(
            df_merge,
            df_visitas[[
                "Codigo", "GPS Ok visitas", "% GPS Ok visitas",
                "GPS Ok > 2 min Visitas", "% GPS Ok > 2 min visitas"
            ]],
            on="Codigo",
            how="left"
        )

        df_merge = df_merge[[
            "Supervisor", "Rep. Ventas", "Codigo",
            "Visitas planificadas", "Visitas completadas",
            "GPS Ok visitas", "% GPS Ok visitas",
            "GPS Ok > 2 min Visitas", "% GPS Ok > 2 min visitas",
            "Primer check-in",
        ]]

        df_merge["Rep. Ventas"] = df_merge["Rep. Ventas"].str.upper()
        df_merge = df_merge.sort_values(by="% GPS Ok > 2 min visitas", ascending=False).reset_index(drop=True)

        df_merge["% GPS Ok visitas"] = df_merge["% GPS Ok visitas"].apply(
            lambda x: f"{x*100:.2f}%" if pd.notna(x) and x <= 1 else f"{x:.2f}%" if pd.notna(x) else x
        )
        df_merge["% GPS Ok > 2 min visitas"] = df_merge["% GPS Ok > 2 min visitas"].apply(
            lambda x: f"{x*100:.2f}%" if pd.notna(x) and x <= 1 else f"{x:.2f}%" if pd.notna(x) else x
        )

        for col in ["Visitas planificadas", "Visitas completadas", "GPS Ok visitas", "GPS Ok > 2 min Visitas"]:
            df_merge[col] = pd.to_numeric(df_merge[col], errors="coerce").fillna(0).astype(int)

        return df_merge
