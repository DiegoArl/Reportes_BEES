import pandas as pd

encabezado = [
    'fecha',
    'nombrecliente',
    'vendedor',
    'nombrevendedor',
    'vtadvo',
    'canal',
    'tipo_pedido',
    'numero_pedido',
    'DescripcionCategoria',
    'codigoproducto',
    'descrpcionproducto', 
    'cajas',
    'soles'
]

def codigo_standard(df_usuarios):
    if df_usuarios is None:
        raise ValueError("df_usuarios no puede ser None")
    partes = df_usuarios["Codigo"].str.split("-", expand=True)

    if partes.shape[1] != 2:
        return False
    
    antes_guion = partes[0]
    despues_guion = partes[1]

    es_estandar = (antes_guion.str.len() == 6) & (despues_guion.str.len() == 5)

    return es_estandar.all()

def procesar_modulo(df, codigos_permitidos=None):
    df = df.copy()
    df = df[encabezado]
    df['tipo_pedido'] = df['tipo_pedido'].apply(lambda x: 'NON BEES' if not isinstance(x, str) or x[:3] != 'B2B' else x)

    mask_producto = (
            ~df["codigoproducto"].astype(str).str.startswith("70") &
            ~df["codigoproducto"].astype(str).str.startswith("90")
    )
    if codigos_permitidos is not None:
            mask_producto |= df["codigoproducto"].astype(str).isin(codigos_permitidos)

    df = df[
        #(df["tipo_pedido"] != "B2B_WEB") &
        (df["vtadvo"] == "V") &
        #(df["canal"] == "BODEGA") &
        mask_producto
    ]
    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y/%m/%d", errors="coerce")
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    df["mes_n"] = df['mes'].astype(str).str[-2:]
    return df

def modelar_modulo(df_modulo):

    df_modelado = df_modulo.groupby(["Codigo", "Rep. Ventas", "Supervisor", "tipo_pedido"]).agg(
        pedidos=("numero_pedido", "nunique")
    ).reset_index()

    df_modelado = df_modelado.pivot_table(
        index=["Codigo", "Rep. Ventas", "Supervisor"],
        columns=["tipo_pedido"],
        values=["pedidos"],
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    df_modelado.columns = [
        f"{col1}_{col2}" if col2 != "" else col1
        for col1, col2 in df_modelado.columns.to_flat_index()
    ]

    df_modelado['pedidos_total'] = 0

    for c in df_modelado.columns:
        map = c.split("_")
        if len(map) > 1 and map[0] == "pedidos" and map[1] != 'total':
            df_modelado['pedidos_total'] += df_modelado[c]

    cols_b2b = df_modelado.filter(like='B2B').columns

    df_modelado['Adopción BEES'] = ( 
        df_modelado[cols_b2b].sum(axis=1) / 
        df_modelado['pedidos_total'] 
    ) 

    df_modelado = df_modelado.sort_values(by='Adopción BEES',ascending=False).reset_index(drop=True) 
    df_modelado["Adopción BEES"] = df_modelado["Adopción BEES"].apply( 
        lambda x: f"{x*100:.2f}%" if x <= 1 else f"{x:.2f}%" 
    ) 
    
    return df_modelado

def color_adopcion(val, thresholds=(30, 60, 80)):

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

def aplicar_estilos_ado(df):

    styled = df.style.map(
        color_adopcion,
        subset=[
            "Adopción BEES"
        ]
    )

    return styled

def adopcion_tabla(df_usuarios, df_modulo):
    val_standard = codigo_standard(df_usuarios)

    df_user = df_usuarios[["Codigo", "Rep. Ventas", "Supervisor"]].copy()
    df_modulo = procesar_modulo(df_modulo)

    if val_standard:
        df_user["vendedor"] = df_user["Codigo"].astype(int)
    else:
        df_user["vendedor"] = df_user["Codigo"].str.split("-").str[-1].str[2:].astype(int)

    df_modulo_filtrado = df_modulo[df_modulo["vendedor"].isin(df_user["vendedor"])]

    df_modulo_filtrado = df_user.merge(
        df_modulo_filtrado,
        on="vendedor",
        how="left"
    ).drop(columns=["vendedor"])


    df_modulo_modelado = modelar_modulo(df_modulo_filtrado)

    
    return df_modulo_modelado