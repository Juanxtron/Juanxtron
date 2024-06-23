import pandas as pd


# Especifica la ruta de tu archivo Excel
ruta_excel = "C:/Users/jpcan/OneDrive/Documentos/Andes Universidad/Analitica computacional/Proyecto 2/Copia de default of credit card clients.xls"

# Lee el archivo Excel en un DataFrame de pandas
datos_excel = pd.read_excel(ruta_excel, sheet_name="Data")

datos_excel.columns = datos_excel.iloc[0]

# Elimina la primera fila, ya que ahora son los nombres de las columnas
datos_excel = datos_excel[1:]


import pandas as pd

# Supongamos que 'df' es tu DataFrame
# df = pd.read_excel("ruta/a/tu/archivo.xlsx")

# Verifica si hay valores faltantes en cada columna
valores_faltantes_por_columna = datos_excel.isna().sum()

# También puedes usar df.isnull().sum() para el mismo propósito

import pandas as pd

# Supongamos que 'datos_excel' es tu DataFrame
# datos_excel = pd.read_excel("ruta/a/tu/archivo.xlsx")

# Eliminar filas con valores atípicos en la columna "EDUCATION"
datos_excel = datos_excel[datos_excel['EDUCATION'].isin([1, 2, 3, 4])]

# Eliminar filas con valores atípicos en la columna "MARRIAGE"
datos_excel = datos_excel[datos_excel['MARRIAGE'].isin([1, 2, 3])]

# Reindexar el DataFrame si es necesario
datos_excel.reset_index(drop=True, inplace=True)

# Cambiar el nombre de la columna "PAY_0" a "PAY_1"
datos_excel = datos_excel.rename(columns={"PAY_0": "PAY_1"})

# Convertir todas las columnas a tipos de datos numéricos
datos_excel = datos_excel.apply(pd.to_numeric, errors='coerce')


# Lista de valores permitidos
#valores_permitidos = [0,-1, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Contador para el total de filas con valores atípicos
#total_filas_atipicas = 0

# Verificar valores fuera de los límites en las columnas PAY_0 a PAY_6
#for columna in ['PAY_1', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']:
    # Eliminar filas con valores atípicos en la columna
    #datos_excel = datos_excel[datos_excel[columna].isin(valores_permitidos)]


for columna in ['PAY_1', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']:
    # Reemplazar el valor 0 por -1 en la columna
    datos_excel[columna] = datos_excel[columna].replace(0, -1)

# Mapeo para las variables categóricas
mapeo_sex = {1: 'Male', 2: 'Female'}
mapeo_education = {1: 'Graduate School', 2: 'University', 3: 'High School', 4: 'Others'}
mapeo_marriage = {1: 'Married', 2: 'Single', 3: 'Others'}

# Reemplazar los valores en las variables categóricas con su representación de texto
datos_excel['SEX'] = datos_excel['SEX'].replace(mapeo_sex)
datos_excel['EDUCATION'] = datos_excel['EDUCATION'].replace(mapeo_education)
datos_excel['MARRIAGE'] = datos_excel['MARRIAGE'].replace(mapeo_marriage)

mapeo__pay= {-2:'Advance in credit 1 month',-1: 'pay duly;',1: 'payment delay for one month', 2: 'payment delay for two month', 3: 'payment delay for three month',4: 'payment delay for four month',5: 'payment delay for fife month',6: 'payment delay for six month',7: 'payment delay for seven month',8: 'payment delay for eigth month',9: 'payment delay for nine month'}

for columna in ['PAY_1', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']:
    datos_excel[columna] = datos_excel[columna].replace(mapeo__pay)



df = pd.DataFrame(datos_excel)

# Convertir variables categóricas en variables dummy
df_dummies = pd.get_dummies(df, columns=['SEX', 'EDUCATION', 'MARRIAGE','PAY_1', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6'])

# Convertir todas las columnas a tipos de datos numéricos
df_dummies = df_dummies.astype(int)




df_dummies.drop("ID",axis=1,inplace=True)

print(df_dummies)