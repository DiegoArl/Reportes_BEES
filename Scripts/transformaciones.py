def procesar_df(df):
    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()
    return df