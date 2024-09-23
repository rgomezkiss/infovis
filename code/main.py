import pandas as pd
import os

# Ruta a la carpeta dataset
dataset_dir = '../Datasets'

# Mapeo de días de la semana a nombres completos
dias_semana_nombre = {
    'l': 'Lunes',
    'm': 'Martes',
    'x': 'Miércoles',
    'j': 'Jueves',
    'v': 'Viernes',
    's': 'Sábado',
    'd': 'Domingo'
}

# Función para procesar un solo archivo CSV
def procesar_csv(ruta_archivo):
    df = pd.read_csv(ruta_archivo)
    df['Total Recibido'] = df[['Meme Recibido', 'Reel Recibido', 'Tweet Recibido', 'Tiktok Recibido']].sum(axis=1)
    df['Total Enviado'] = df[['Meme Enviado', 'Reel Enviado', 'Tweet Enviado', 'Tiktok Enviado']].sum(axis=1)
    return df

def main():
    # Inicializar diccionarios para los resúmenes
    resumen_dia = {}
    resumen_semana = {dia: {'Recibido': 0, 'Enviado': 0} for dia in dias_semana_nombre}
    resumen_categoria = {'Recibido': {'Meme': 0, 'Reel': 0, 'Tweet': 0, 'Tiktok': 0}, 
                         'Enviado': {'Meme': 0, 'Reel': 0, 'Tweet': 0, 'Tiktok': 0}}
    resumen_persona = {}
    
    # Nuevo diccionario para el conteo de personas por día
    resumen_conteo_dia = {}
    
    # Nuevo diccionario para el conteo de personas por día de la semana
    resumen_conteo_semana = {dia: {'Recibido': set(), 'Enviado': set()} for dia in dias_semana_nombre}

    # Recorrer las subcarpetas de días de la semana
    for dia_semana in os.listdir(dataset_dir):
        dia_semana_dir = os.path.join(dataset_dir, dia_semana)
        
        if os.path.isdir(dia_semana_dir):  # Verificar si es un directorio
            # Recorrer los archivos CSV en la carpeta del día
            for archivo_csv in os.listdir(dia_semana_dir):
                ruta_archivo = os.path.join(dia_semana_dir, archivo_csv)
                
                # Procesar el CSV
                df = procesar_csv(ruta_archivo)

                # Obtener la fecha del archivo (basado en el nombre del archivo)
                fecha = archivo_csv.split('.')[0]
                if fecha not in resumen_dia:
                    resumen_dia[fecha] = {'Recibido': 0, 'Enviado': 0}
                    resumen_conteo_dia[fecha] = {'Recibido': set(), 'Enviado': set()}

                # Sumar totales por día
                resumen_dia[fecha]['Recibido'] += df['Total Recibido'].sum()
                resumen_dia[fecha]['Enviado'] += df['Total Enviado'].sum()

                # Sumar totales por día de la semana (separado en Recibido y Enviado)
                resumen_semana[dia_semana]['Recibido'] += df['Total Recibido'].sum()
                resumen_semana[dia_semana]['Enviado'] += df['Total Enviado'].sum()

                # Sumar totales por categoría
                resumen_categoria['Recibido']['Meme'] += df['Meme Recibido'].sum()
                resumen_categoria['Recibido']['Reel'] += df['Reel Recibido'].sum()
                resumen_categoria['Recibido']['Tweet'] += df['Tweet Recibido'].sum()
                resumen_categoria['Recibido']['Tiktok'] += df['Tiktok Recibido'].sum()
                resumen_categoria['Enviado']['Meme'] += df['Meme Enviado'].sum()
                resumen_categoria['Enviado']['Reel'] += df['Reel Enviado'].sum()
                resumen_categoria['Enviado']['Tweet'] += df['Tweet Enviado'].sum()
                resumen_categoria['Enviado']['Tiktok'] += df['Tiktok Enviado'].sum()

                # Sumar totales por persona y agregar al conteo de personas únicas
                for index, row in df.iterrows():
                    nombre = row['Nombre']
                    if nombre not in resumen_persona:
                        resumen_persona[nombre] = {'Recibido': 0, 'Enviado': 0}
                    resumen_persona[nombre]['Recibido'] += row['Total Recibido']
                    resumen_persona[nombre]['Enviado'] += row['Total Enviado']

                    # Agregar al set de personas únicas
                    if row['Total Recibido'] > 0:
                        resumen_conteo_dia[fecha]['Recibido'].add(nombre)
                        resumen_conteo_semana[dia_semana]['Recibido'].add(nombre)
                    if row['Total Enviado'] > 0:
                        resumen_conteo_dia[fecha]['Enviado'].add(nombre)
                        resumen_conteo_semana[dia_semana]['Enviado'].add(nombre)

    # Guardar los resultados en nuevos archivos CSV
    # Total por día, ordenado por fecha
    df_resumen_dia = pd.DataFrame.from_dict(resumen_dia, orient='index').reset_index()
    df_resumen_dia.columns = ['Fecha', 'Recibido', 'Enviado']
    df_resumen_dia = df_resumen_dia.sort_values(by='Fecha')  # Ordenar por fecha
    df_resumen_dia.to_csv('total_por_dia.csv', index=False)

    # Total por día de la semana (con nombres completos)
    df_resumen_semana = pd.DataFrame.from_dict(resumen_semana, orient='index').reset_index()
    df_resumen_semana.columns = ['Día Semana', 'Recibido', 'Enviado']
    df_resumen_semana['Día Semana'] = df_resumen_semana['Día Semana'].map(dias_semana_nombre)  # Mapear nombres completos
    df_resumen_semana.to_csv('total_por_dia_semana.csv', index=False)

    # Total por categoría
    df_resumen_categoria = pd.DataFrame(resumen_categoria).reset_index()
    df_resumen_categoria.columns = ['Categoría', 'Recibido', 'Enviado']
    df_resumen_categoria.to_csv('total_por_categoria.csv', index=False)

    # Total por persona
    df_resumen_persona = pd.DataFrame.from_dict(resumen_persona, orient='index').reset_index()
    df_resumen_persona.columns = ['Nombre', 'Recibido', 'Enviado']
    df_resumen_persona.to_csv('total_por_persona.csv', index=False)

    # Guardar el conteo de personas por día
    df_conteo_dia = pd.DataFrame({
        'Fecha': resumen_conteo_dia.keys(),
        'Recibido': [len(resumen_conteo_dia[fecha]['Recibido']) for fecha in resumen_conteo_dia],
        'Enviado': [len(resumen_conteo_dia[fecha]['Enviado']) for fecha in resumen_conteo_dia]
    })
    df_conteo_dia = df_conteo_dia.sort_values(by='Fecha')  # Ordenar por fecha
    df_conteo_dia.to_csv('total_personas_por_dia.csv', index=False)

    # Guardar el conteo de personas por día de la semana
    df_conteo_semana = pd.DataFrame({
        'Día Semana': resumen_conteo_semana.keys(),
        'Recibido': [len(resumen_conteo_semana[dia]['Recibido']) for dia in resumen_conteo_semana],
        'Enviado': [len(resumen_conteo_semana[dia]['Enviado']) for dia in resumen_conteo_semana]
    })
    df_conteo_semana['Día Semana'] = df_conteo_semana['Día Semana'].map(dias_semana_nombre)  # Mapear nombres completos
    df_conteo_semana.to_csv('total_personas_por_dia_semana.csv', index=False)

    print("¡Archivos generados con éxito!")

# Punto de entrada
if __name__ == "__main__":
    main()
