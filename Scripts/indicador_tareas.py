import pandas as pd

def gradient_colors(values, thresholds=(0.30, 0.60, 0.80)):
        
    t1, t2, t3 = thresholds
    styles = []

    for v in values:
        if pd.isna(v):
            styles.append("")
            continue

        if v < t1:
            styles.append("background-color: rgb(248,105,108)")
        elif v < t2:
            styles.append("background-color: rgb(251,233,130)")
        elif v < t3:
            styles.append("background-color: rgb(251,190,123)")
        else:
            styles.append("background-color: rgb(99,190,123)")
    return styles

def aplicar_estilos_tareas(df):

    alcance_cols = [col for col in df.columns if col[1] == "%Alcance"]
    tarea_cols = [col for col in df.columns if col[1] == "tarea efectiva"]

    formato = {
        **{col: lambda x: f"{x*100:.2f}%" if pd.notna(x) and x <= 1 else (f"{x:.2f}%" if pd.notna(x) else "")
           for col in alcance_cols},
        **{col: lambda x: f"{int(x)}" if pd.notna(x) else ""
           for col in tarea_cols}
    }

    styled = (
        df.style
        .apply(gradient_colors, subset=alcance_cols, axis=0)
        .format(formato)
    )

    return styled

def agregar_equipo(df_tareas, df_usuarios):

    df_usuarios = df_usuarios[["Codigo", "Supervisor", "Rep. Ventas"]]

    df_merge = df_tareas.merge(
        df_usuarios,
        left_on="BDR ID",
        right_on="Codigo",
        how="left"
    ).drop(columns="BDR ID")

    df_merge = df_merge[df_merge["Supervisor"].notna()]


    return df_merge

def tabla_tareas(df_tareas, df_usuarios):

    tarea = agregar_equipo(df_tareas, df_usuarios)

    out = (
        tarea
        .groupby(["Supervisor", "Rep. Ventas", "Task Name"], as_index=False)
        .agg(
            total=("Is Task Effective", "count"),
            true_count=("Is Task Effective", lambda x: (x == 1).sum())
        )
    )

    pivot_true = out.pivot_table(
        index=["Supervisor", "Rep. Ventas"],
        columns="Task Name",
        values="true_count",
        aggfunc="sum"
    ).fillna(0)

    pivot_total = out.pivot_table(
        index=["Supervisor", "Rep. Ventas"],
        columns="Task Name",
        values="total",
        aggfunc="sum"
    ).fillna(0)

    pivot_pct = pivot_true.div(pivot_total).fillna(0)

    pivot_true.columns = pd.MultiIndex.from_tuples(
        [(col, "tarea efectiva") for col in pivot_true.columns]
    )
    pivot_pct.columns = pd.MultiIndex.from_tuples(
        [(col, "%Alcance") for col in pivot_pct.columns]
    )

    result = pd.concat([pivot_true, pivot_pct], axis=1).sort_index(axis=1)

    return result