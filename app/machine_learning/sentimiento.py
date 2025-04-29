#creamos funcion que lee los archivos csv y usa el modelo de prediccion
import joblib
import pandas as pd

def analisis_sentimientos(csv):
    
    modelo = joblib.load('modelo_entrenado_sentimientos.pkl')
    tfidf = joblib.load('vectorizador_entrenado.pkl')
    
    df = pd.read_csv(csv)
    
    X = df['texto']
    X_vector = tfidf.transform(X)    
    
    prediccion = modelo.predict(X_vector)
    
    resumen = pd.Series(prediccion).value_counts()
    return resumen.to_dict()
    
    
    