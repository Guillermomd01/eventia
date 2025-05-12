import pandas as pd
from sklearn.ensemble import IsolationForest

from app.machine_learning.prediccion import transformar_fechas

def detectar_anomalias(csv):
    try:
        df = pd.read_csv(csv)
        transformar_fechas(df)
        df_numerico = df.select_dtypes(include='number')
        if df_numerico.shape[1] == 0:
            raise ValueError("El archivo no contiene columnas numéricas para analizar.")
        modelo_anomalias = IsolationForest(contamination='auto',random_state=42)
        modelo_anomalias.fit(df_numerico)
        prediccion = modelo_anomalias.predict(df_numerico)
        
        df['es_anomalia']= prediccion
        df['es_anomalia'] = df['es_anomalia'].replace({1:'No',-1:'Sí'})
        
        df_usuario = df.loc[df['es_anomalia']== 'Sí']
        
        col_valor = df_numerico.columns[-1]
        datos = {'fecha':df['fecha'],'valores':df_numerico[col_valor],'anomalia': df['es_anomalia']}
        df_grafico = pd.DataFrame(data=datos)
        return df,df_usuario,df_grafico
    except Exception as e:
        raise ValueError(f"Error al procesar el archivo CSV: {str(e)}")
        
    
    