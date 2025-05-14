from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def transformar_fechas(df):
    df = df.copy()
    df['mes_num'] = range(len(df))
    df['mes'] = df['fecha'].dt.month
    df['dia_semana'] = df['fecha'].dt.weekday
    df['es_fin_de_semana'] = df['dia_semana'].isin([5,6]).astype(int)
    df['semana'] = df['fecha'].dt.isocalendar().week
    df['dia_mes'] = df['fecha'].dt.day
    df['trimestre'] = df['fecha'].dt.quarter
    df['año'] = df['fecha'].dt.year
    return df

def convertir_valor(valor):
    try:
        if isinstance(valor, str):
            if ',' in valor and '.' in valor:
                valor = valor.replace('.', '').replace(',', '.')
            elif ',' in valor:
                valor = valor.replace(',', '.')
        return float(valor)
    except:
        return np.nan

def detectar_tendencia(y):
    """Detecta si hay una tendencia fuerte en los datos"""
    # Calculamos la correlación entre el índice (tiempo) y las ventas
    correlacion = np.corrcoef(np.arange(len(y)), y)[0, 1]
    return abs(correlacion)

def detectar_estacionalidad(y):
    """Detecta si hay estacionalidad en los datos"""
    # Calcula la autocorrelación con diferentes desfases
    autocorr = [np.corrcoef(y[:-i], y[i:])[0, 1] for i in range(1, min(13, len(y)//2))]
    # Si hay picos altos en la autocorrelación, puede haber estacionalidad
    return np.max(np.abs(autocorr)) if len(autocorr) > 0 else 0

def seleccionar_mejor_modelo(X, y):
    """Selecciona el mejor modelo basado en los datos y sus características"""
    # Dividir datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalizar los datos para mejorar el rendimiento del modelo
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Entrenar modelo de regresión lineal
    modelo_linear = LinearRegression()
    modelo_linear.fit(X_train_scaled, y_train)
    y_pred_linear = modelo_linear.predict(X_test_scaled)
    mse_linear = mean_squared_error(y_test, y_pred_linear)
    r2_linear = r2_score(y_test, y_pred_linear)
    
    # Entrenar modelo RandomForest
    modelo_rf = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo_rf.fit(X_train_scaled, y_train)
    y_pred_rf = modelo_rf.predict(X_test_scaled)
    mse_rf = mean_squared_error(y_test, y_pred_rf)
    r2_rf = r2_score(y_test, y_pred_rf)
    
    # Análisis de tendencia y estacionalidad
    tendencia = detectar_tendencia(y)
    estacionalidad = detectar_estacionalidad(y)
    
    # Lógica de selección basada en métricas y características de los datos
    if tendencia > 0.7:  # Fuerte tendencia lineal
        if r2_linear >= r2_rf * 0.95:  # Si la regresión lineal es casi tan buena como RF
            mejor_modelo = "LinearRegression"
            modelo_final = modelo_linear
            mse_final = mse_linear
            r2_final = r2_linear
        else:
            mejor_modelo = "RandomForest"
            modelo_final = modelo_rf
            mse_final = mse_rf
            r2_final = r2_rf
    elif estacionalidad > 0.5:  # Patrones estacionales
        # RandomForest suele manejar mejor patrones estacionales
        mejor_modelo = "RandomForest"
        modelo_final = modelo_rf
        mse_final = mse_rf
        r2_final = r2_rf
    else:
        # Elegir el modelo con mejor r2
        if r2_linear > r2_rf:
            mejor_modelo = "LinearRegression"
            modelo_final = modelo_linear
            mse_final = mse_linear
            r2_final = r2_linear
        else:
            mejor_modelo = "RandomForest"
            modelo_final = modelo_rf
            mse_final = mse_rf
            r2_final = r2_rf
    
    return {
        'modelo': modelo_final, 
        'nombre': mejor_modelo, 
        'mse': mse_final, 
        'r2': r2_final,
        'scaler': scaler
    }

def prediccion(csv):
    try:
        df = pd.read_csv(csv)

        # Convertir columna fecha
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        if df['fecha'].isnull().any():
            raise ValueError("Error: algunas fechas no se han podido convertir correctamente.")

        # Convertir columna ventas
        if 'ventas' in df.columns:
            df['ventas'] = df['ventas'].apply(convertir_valor)
            df['ventas'] = df['ventas'].interpolate(method='linear').fillna(method='bfill').fillna(method='ffill')
        else:
            raise ValueError("No se encontró la columna 'ventas' en el archivo CSV.")

        # Convertir cualquier otra columna de tipo object (menos fecha)
        for col in df.columns:
            if col.lower() != 'fecha' and col.lower() != 'ventas' and df[col].dtype == object:
                df[col] = df[col].apply(convertir_valor)

        # Preparar datos
        df = df.sort_values('fecha')
        df = transformar_fechas(df)
        df_original = df.copy()

        y = df['ventas']
        X = df.drop(columns=['fecha', 'ventas', 'mes_num'])
        X = X.fillna(method='bfill').fillna(method='ffill')
        if X.isnull().any().any():
            raise ValueError("X contiene valores nulos incluso después de la limpieza.")

        # Seleccionar el mejor modelo
        resultado_modelo = seleccionar_mejor_modelo(X, y)
        modelo_final = resultado_modelo['modelo']
        nombre_modelo = resultado_modelo['nombre']
        scaler = resultado_modelo['scaler']
        
        print(f"Modelo seleccionado: {nombre_modelo}")
        print(f"MSE: {resultado_modelo['mse']:.4f}")
        print(f"R²: {resultado_modelo['r2']:.4f}")

        # Escalar los datos para la predicción
        X_scaled = scaler.transform(X)
        
        # Reentrenar el modelo con todos los datos para predicciones futuras
        modelo_final.fit(X_scaled, y)

        # Fechas futuras
        fecha_max = df['mes_num'].max()
        fecha_base = df['fecha'].max()
        fechas_futuras = pd.date_range(start=fecha_base + pd.Timedelta(days=1), periods=len(df))

        df_prediccion = pd.DataFrame({'fecha': fechas_futuras})
        df_prediccion = transformar_fechas(df_prediccion)
        df_prediccion['mes_num'] = range(fecha_max + 1, fecha_max + len(df) + 1)

        X_pred = df_prediccion.drop(columns=['fecha', 'mes_num'])
        X_pred_scaled = scaler.transform(X_pred)
        prediccion = modelo_final.predict(X_pred_scaled).round(2)

        df_resultado = pd.DataFrame({
            'fecha': df_prediccion['fecha'],
            'prediccion': prediccion
        })

        return df_original, df_resultado

    except Exception as e:
        raise ValueError(f"Error al procesar el archivo CSV: {str(e)}")
