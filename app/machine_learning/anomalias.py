import pandas as pd
from sklearn.ensemble import IsolationForest

def detectar_anomalias(csv):
    try:
        df = pd.read_csv(csv)

        df_numerico = df.select_dtypes(include='number')
        if df_numerico.shape[1] == 0:
            raise ValueError("El archivo no contiene columnas numéricas para analizar.")
        modelo_anomalias = IsolationForest(contamination='auto',random_state=42)
        modelo_anomalias.fit(df_numerico)
        prediccion = modelo_anomalias.predict(df_numerico)
        
        df['es_anomalia']= prediccion
        df['es_anomalia'] = df['es_anomalia'].replace({1:'No',-1:'Sí'})
        
        df_usuario = df.loc[df['es_anomalia']== 'Sí']
        
        return df,df_usuario
    except:
        raise ValueError('Error al procesar el archivo')
        
    
    