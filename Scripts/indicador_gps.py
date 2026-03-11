import pandas as pd
import numpy as np

def color_gps(val, thresholds=(30, 60, 80)):

    if val is None:
        return ""

    try:
        v = float(str(val).replace("%",""))
    except:
        return ""

    t1, t2, t3 = thresholds

    if v < t1:
        color = "rgb(248,105,108)"
    elif v < t2:
        color = "rgb(251,233,130)"
    elif v < t3:
        color = "rgb(251,190,123)"
    else:
        color = "rgb(99,190,123)"

    return f"background-color: {color}"

def aplicar_estilos(df):

    styled = df.style.map(
        color_gps,
        subset=[
            "% GPS Ok visitas",
            "% GPS Ok > 2 min visitas"
        ]
    )

    return styled

def unir_tablas(df_usuarios, df_checkin, df_visitas):

    if df_usuarios is None:
        raise ValueError("df_usuarios no puede ser None")

    df_base = df_usuarios[["Codigo", "Rep. Ventas", "Supervisor"]]

    df_merge = pd.merge(
        df_base,
        df_checkin[
            ["Codigo", "Visitas planificadas", "Visitas completadas", "Primer check-in"]
        ],
        on="Codigo",
        how="left"
    )

    df_merge = pd.merge(
        df_merge,
        df_visitas[
            ["Codigo", "GPS Ok visitas", "% GPS Ok visitas", "GPS Ok > 2 min Visitas", "% GPS Ok > 2 min visitas"]
        ],
        on="Codigo",
        how="left"
    )

    df_merge = df_merge[
        [
            "Supervisor",
            "Rep. Ventas",
            "Codigo",
            "Visitas planificadas",
            "Visitas completadas",
            "GPS Ok visitas",
            "% GPS Ok visitas",
            "GPS Ok > 2 min Visitas",
            "% GPS Ok > 2 min visitas",
            "Primer check-in",
        ]
    ]

    df_merge["Rep. Ventas"] = df_merge["Rep. Ventas"].str.upper()

    df_merge["% GPS Ok visitas"] = df_merge["% GPS Ok visitas"].apply(
        lambda x: f"{x*100:.2f}%" if pd.notna(x) and x <= 1 else f"{x:.2f}%" if pd.notna(x) else x
    )

    df_merge["% GPS Ok > 2 min visitas"] = df_merge["% GPS Ok > 2 min visitas"].apply(
        lambda x: f"{x*100:.2f}%" if pd.notna(x) and x <= 1 else f"{x:.2f}%" if pd.notna(x) else x
    )

    for col in [
        "Visitas planificadas",
        "Visitas completadas",
        "GPS Ok visitas",
        "GPS Ok > 2 min Visitas",
    ]:
        df_merge[col] = pd.to_numeric(df_merge[col], errors="coerce").fillna(0)

    return df_merge