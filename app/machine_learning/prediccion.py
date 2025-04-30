from sklearn.linear_model import LinearRegression
import pandas as pd
from sklearn.model_selection import train_test_split

def transformar_fechas(df):
    df = df.copy()
    df = df.sort_values('fecha')  # por si viene desordenado
    df['mes_num'] = range(len(df))
    return df

def prediccion(csv):
    try:
        df = pd.read_csv(csv)

        columna_requerida= ['fecha']
        if not all(col in df.columns for col in columna_requerida):
            raise ValueError("El archivo subido no tiene la columna fecha requerida.")
        df = transformar_fechas(df)
        
        if 'ventas' in df.columns:
            y = df['ventas']
            X = df.drop(columns=['ventas'])
            
            modelo_linear = LinearRegression()
            modelo_linear.fit(X,y)
            

            fecha_max = df['mes_num'].max()
            nuevas_fechas = list(range(fecha_max+1,fecha_max+16))
            columnas_extra = [col for col in X.columns if col != 'mes_num']
            datos ={
                'mes_num':nuevas_fechas,  
            }
            df_prediccion =  pd.DataFrame(datos)  
            
            for columna in columnas_extra:
                df_prediccion[columna] = df[columna].mean()
                
            prediccion = modelo_linear.predict(df_prediccion)
            
            return pd.DataFrame({
                'mes_num': nuevas_fechas,
                'prediccion': prediccion
            })
        else:
            y = df.iloc[:,-1]
            X = df.iloc[:,0:-1]
            
            modelo_linear = LinearRegression()
            modelo_linear.fit(X,y)
            
            fecha_max = df['mes_num'].max()
            nuevas_fechas = list(range(fecha_max+1,fecha_max+16))
            columnas_extra = [col for col in X.columns if col != 'mes_num']
            
            datos ={
                'mes_num':nuevas_fechas,  
            }
            df_prediccion =  pd.DataFrame(datos)  
            
            for columna in columnas_extra:
                df_prediccion[columna] = df[columna].mean()
                
            prediccion = modelo_linear.predict(df_prediccion)
            
            return pd.DataFrame({
                'mes_num': nuevas_fechas,
                'prediccion': prediccion
            })
            
    except:
        raise ValueError("Error al procesar el archivo CSV.")