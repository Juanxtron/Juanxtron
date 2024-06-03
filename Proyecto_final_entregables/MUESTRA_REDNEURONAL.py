import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import numpy as np
import psycopg2
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler




# Conexión a la base de datos
engine = psycopg2.connect(
    dbname="icfes",
    user="postgres",
    password="proyecto2",
    host="proyecto-2.cjgscwkesde4.us-east-1.rds.amazonaws.com",
    port="5432"
)

cursor = engine.cursor()

query = """
SELECT * 
FROM resultados 
WHERE (cole_depto_ubicacion = 'BOGOTÁ' AND periodo IN ('20194', '20191')) OR (cole_depto_ubicacion = 'BOGOTA' AND periodo IN ('20194', '20191'));"""

df = pd.read_sql_query(query, engine) 

# Eliminar filas nulas y columnas no deseadas
df_sin_nulos = df.dropna()
columnas_a_eliminar = [
    'estu_tipodocumento',
    'estu_consecutivo',
    'cole_cod_dane_establecimiento',
    'cole_cod_dane_sede',
    'cole_cod_depto_ubicacion',
    'cole_cod_mcpio_ubicacion',
    'cole_codigo_icfes',
    'estu_cod_depto_presentacion',
    'estu_cod_mcpio_presentacion',
    'estu_cod_reside_depto',
    'estu_cod_reside_mcpio',
    'desemp_ingles',
    'cole_depto_ubicacion',
    "estu_privado_libertad",
    "estu_estudiante",
    "punt_global"
]
df_sin_nulos.drop(columns=columnas_a_eliminar, inplace=True)

# Convertir columnas a numéricas y calcular la edad
puntaje_columnas = ['punt_ingles', 'punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica']
for col in puntaje_columnas:
    df_sin_nulos[col] = pd.to_numeric(df_sin_nulos[col], errors='coerce')

df_sin_nulos['estu_fechanacimiento'] = pd.to_datetime(df_sin_nulos['estu_fechanacimiento'], format='%d/%m/%Y')
anio_referencia = 2019
df_sin_nulos['edad'] = anio_referencia - df_sin_nulos['estu_fechanacimiento'].dt.year
df_sin_nulos.drop(columns=['estu_fechanacimiento'], inplace=True)

# Preparar los datos
columnas_a_excluir = ['punt_ingles','punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica','cole_mcpio_ubicacion','cole_nombre_sede','periodo']
X = df_sin_nulos.drop(columns=columnas_a_excluir, axis=1)
import pandas as pd
import numpy as np



# Dividir en X e Y
Y = df_sin_nulos['punt_ingles']
columnas_a_excluir = ['punt_ingles','punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica','cole_mcpio_ubicacion','cole_nombre_sede','periodo']
#'punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica'
X = df_sin_nulos.drop(columns=columnas_a_excluir, axis=1)
# Convertir las columnas categóricas en variables dummy
X_dummies = pd.get_dummies(X)
X_dummies = X_dummies.astype(int)


# Convertir a arrays de numpy
X_dummies = np.array(X_dummies)
Y = np.array(Y)




X_dummies = X_dummies[:30000]
Y = Y[:30000]

X_train_full, X_test, y_train_full, y_test = train_test_split(
    X_dummies, Y, test_size=0.3, random_state=42)
X_train, X_valid, y_train, y_valid = train_test_split(
    X_train_full, y_train_full, test_size=0.3, random_state=42)

# Escalar los datos (opcional, pero es común en redes neuronales)
std_scl = StandardScaler()
std_scl.fit(X_train)


X_train = std_scl.transform(X_train)

X_valid = std_scl.transform(X_valid)
X_test = std_scl.transform(X_test)

#####################################################Ingles#############################################################


model = tf.keras.Sequential()
model.add(tf.keras.layers.InputLayer(input_shape=(1311,)))
model.add(tf.keras.layers.Dense(500, activation="relu"))
model.add(tf.keras.layers.Dropout(0.3))  # Agregar Dropout con probabilidad de 0.3
model.add(tf.keras.layers.Dense(1, activation='softplus'))

from tensorflow.keras.losses import MeanSquaredError
model.compile(loss=MeanSquaredError(),  
                  optimizer="adam",
                  metrics=["mean_absolute_error"])

history = model.fit(X_train, y_train, epochs=10,
                    validation_data=(X_valid, y_valid))



########################################################################################################################

#####################################################Lectura critica#############################################################
# Dividir en X e Y
Y = df_sin_nulos['punt_lectura_critica']
columnas_a_excluir = ['punt_ingles','punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica','cole_mcpio_ubicacion','cole_nombre_sede','periodo']
#'punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica'
X = df_sin_nulos.drop(columns=columnas_a_excluir, axis=1)
# Convertir las columnas categóricas en variables dummy
X_dummies = pd.get_dummies(X)
X_dummies = X_dummies.astype(int)


# Convertir a arrays de numpy
X_dummies = np.array(X_dummies)
Y = np.array(Y)




X_dummies = X_dummies[:30000]
Y = Y[:30000]

X_train_full, X_test, y_train_full, y_test = train_test_split(
    X_dummies, Y, test_size=0.3, random_state=42)
X_train, X_valid, y_train, y_valid = train_test_split(
    X_train_full, y_train_full, test_size=0.3, random_state=42)

# Escalar los datos (opcional, pero es común en redes neuronales)
std_scl = StandardScaler()
std_scl.fit(X_train)


X_train = std_scl.transform(X_train)

X_valid = std_scl.transform(X_valid)
X_test = std_scl.transform(X_test)



model1 = tf.keras.Sequential()
model1.add(tf.keras.layers.InputLayer(input_shape=(1311,)))
model1.add(tf.keras.layers.Dense(500, activation="relu"))
model1.add(tf.keras.layers.Dropout(0.3))  # Agregar Dropout con probabilidad de 0.3
model1.add(tf.keras.layers.Dense(1, activation='softplus'))

from tensorflow.keras.losses import MeanSquaredError
model1.compile(loss=MeanSquaredError(),  
                  optimizer="adam",
                  metrics=["mean_absolute_error"])

history1 = model.fit(X_train, y_train, epochs=10,
                    validation_data=(X_valid, y_valid))



########################################################################################################################

#####################################################Naturales#############################################################
# Dividir en X e Y
Y = df_sin_nulos['punt_c_naturales']
columnas_a_excluir = ['punt_ingles','punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica','cole_mcpio_ubicacion','cole_nombre_sede','periodo']
#'punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica'
X = df_sin_nulos.drop(columns=columnas_a_excluir, axis=1)
# Convertir las columnas categóricas en variables dummy
X_dummies = pd.get_dummies(X)
X_dummies = X_dummies.astype(int)


# Convertir a arrays de numpy
X_dummies = np.array(X_dummies)
Y = np.array(Y)




X_dummies = X_dummies[:30000]
Y = Y[:30000]

X_train_full, X_test, y_train_full, y_test = train_test_split(
    X_dummies, Y, test_size=0.3, random_state=42)
X_train, X_valid, y_train, y_valid = train_test_split(
    X_train_full, y_train_full, test_size=0.3, random_state=42)

# Escalar los datos (opcional, pero es común en redes neuronales)
std_scl = StandardScaler()
std_scl.fit(X_train)


X_train = std_scl.transform(X_train)

X_valid = std_scl.transform(X_valid)
X_test = std_scl.transform(X_test)



model2 = tf.keras.Sequential()
model2.add(tf.keras.layers.InputLayer(input_shape=(1311,)))
model2.add(tf.keras.layers.Dense(500, activation="relu"))
model2.add(tf.keras.layers.Dropout(0.3))  # Agregar Dropout con probabilidad de 0.3
model2.add(tf.keras.layers.Dense(1, activation='softplus'))

from tensorflow.keras.losses import MeanSquaredError
model2.compile(loss=MeanSquaredError(),  
                  optimizer="adam",
                  metrics=["mean_absolute_error"])

history2 = model.fit(X_train, y_train, epochs=10,
                    validation_data=(X_valid, y_valid))



########################################################################################################################

#####################################################cienciassociales#############################################################
# Dividir en X e Y
Y = df_sin_nulos['punt_sociales_ciudadanas']
columnas_a_excluir = ['punt_ingles','punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica','cole_mcpio_ubicacion','cole_nombre_sede','periodo']
#'punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica'
X = df_sin_nulos.drop(columns=columnas_a_excluir, axis=1)
# Convertir las columnas categóricas en variables dummy
X_dummies = pd.get_dummies(X)
X_dummies = X_dummies.astype(int)


# Convertir a arrays de numpy
X_dummies = np.array(X_dummies)
Y = np.array(Y)




X_dummies = X_dummies[:30000]
Y = Y[:30000]

X_train_full, X_test, y_train_full, y_test = train_test_split(
    X_dummies, Y, test_size=0.3, random_state=42)
X_train, X_valid, y_train, y_valid = train_test_split(
    X_train_full, y_train_full, test_size=0.3, random_state=42)

# Escalar los datos (opcional, pero es común en redes neuronales)
std_scl = StandardScaler()
std_scl.fit(X_train)


X_train = std_scl.transform(X_train)

X_valid = std_scl.transform(X_valid)
X_test = std_scl.transform(X_test)



model3 = tf.keras.Sequential()
model3.add(tf.keras.layers.InputLayer(input_shape=(1311,)))
model3.add(tf.keras.layers.Dense(500, activation="relu"))
model3.add(tf.keras.layers.Dropout(0.3))  # Agregar Dropout con probabilidad de 0.3
model3.add(tf.keras.layers.Dense(1, activation='softplus'))

from tensorflow.keras.losses import MeanSquaredError
model3.compile(loss=MeanSquaredError(),  
                  optimizer="adam",
                  metrics=["mean_absolute_error"])

history3 = model.fit(X_train, y_train, epochs=10,
                    validation_data=(X_valid, y_valid))



########################################################################################################################

#####################################################Matematicas#############################################################
# Dividir en X e Y
Y = df_sin_nulos['punt_matematicas']
columnas_a_excluir = ['punt_ingles','punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica','cole_mcpio_ubicacion','cole_nombre_sede','periodo']
#'punt_matematicas', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica'
X = df_sin_nulos.drop(columns=columnas_a_excluir, axis=1)
# Convertir las columnas categóricas en variables dummy
X_dummies = pd.get_dummies(X)
X_dummies = X_dummies.astype(int)


# Convertir a arrays de numpy
X_dummies = np.array(X_dummies)
Y = np.array(Y)




X_dummies = X_dummies[:30000]
Y = Y[:30000]

X_train_full, X_test, y_train_full, y_test = train_test_split(
    X_dummies, Y, test_size=0.3, random_state=42)
X_train, X_valid, y_train, y_valid = train_test_split(
    X_train_full, y_train_full, test_size=0.3, random_state=42)

# Escalar los datos (opcional, pero es común en redes neuronales)
std_scl = StandardScaler()
std_scl.fit(X_train)


X_train = std_scl.transform(X_train)

X_valid = std_scl.transform(X_valid)
X_test = std_scl.transform(X_test)



model4 = tf.keras.Sequential()
model4.add(tf.keras.layers.InputLayer(input_shape=(1311,)))
model4.add(tf.keras.layers.Dense(500, activation="relu"))
model4.add(tf.keras.layers.Dropout(0.3))  # Agregar Dropout con probabilidad de 0.3
model4.add(tf.keras.layers.Dense(1, activation='softplus'))

from tensorflow.keras.losses import MeanSquaredError
model2.compile(loss=MeanSquaredError(),  
                  optimizer="adam",
                  metrics=["mean_absolute_error"])

history4 = model.fit(X_train, y_train, epochs=10,
                    validation_data=(X_valid, y_valid))



########################################################################################################################

# Cargar los modelos
model_paths = {
    'Matemáticas': model4,
    'Ciencias Sociales': model3,
    'Ciencias Naturales': model2,
    'Lectura Crítica': model1,
    'Inglés': model
}
models = {name: path for name, path in model_paths.items()}

# Ponderaciones para cada carrera
ponderaciones_puntaje = {
    "Arquitectura": {
        "Lectura Crítica": "27%",
        "Ciencias Naturales": "25%",
        "Ciencias Sociales": "26%",
        "Matemáticas": "22%",
        "Total": "100%"
    },
    "Derecho": {
        "Lectura Crítica": "45%",
        "Ciencias Naturales": "10%",
        "Ciencias Sociales": "35%",
        "Matemáticas": "10%",
        "Total": "100%"
    },
    "Medicina Veterinaria y Zootecnia": {
        "Lectura Crítica": "20%",
        "Ciencias Naturales": "45%",
        "Ciencias Sociales": "20%",
        "Matemáticas": "15%",
        "Total": "100%"
    },
    "Biología": {
        "Lectura Crítica": "25%",
        "Ciencias Naturales": "40%",
        "Ciencias Sociales": "15%",
        "Matemáticas": "20%",
        "Total": "100%"
    },
    "Contaduría Pública": {
        "Lectura Crítica": "35%",
        "Ciencias Naturales": "10%",
        "Ciencias Sociales": "30%",
        "Matemáticas": "25%",
        "Total": "100%"
    },
    "Economía": {
        "Lectura Crítica": "30%",
        "Ciencias Naturales": "10%",
        "Ciencias Sociales": "30%",
        "Matemáticas": "30%",
        "Total": "100%"
    },
    "Ingeniería Agroforestal": {
        "Lectura Crítica": "25%",
        "Ciencias Naturales": "30%",
        "Ciencias Sociales": "10%",
        "Matemáticas": "35%",
        "Total": "100%"
    },
    "Ingeniería Civil": {
        "Lectura Crítica": "25%",
        "Ciencias Naturales": "30%",
        "Ciencias Sociales": "10%",
        "Matemáticas": "35%",
        "Total": "100%"
    },
    "Ingeniería Agroindustrial": {
        "Lectura Crítica": "25%",
        "Ciencias Naturales": "30%",
        "Ciencias Sociales": "10%",
        "Matemáticas": "35%",
        "Total": "100%"
    },
    "Administración de Empresas": {
        "Lectura Crítica": "40%",
        "Ciencias Naturales": "0%",
        "Ciencias Sociales": "35%",
        "Matemáticas": "25%",
        "Total": "100%"
    }
}

# Rangos de puntaje
rangos_puntaje = {
    "Medicina": {"min": 350, "max": 450},
    "Ingeniería": {"min": 300, "max": 400},
    "Derecho": {"min": 280, "max": 380},
    "Administración": {"min": 270, "max": 370},
    "Psicología": {"min": 260, "max": 360},
    "Comunicación": {"min": 250, "max": 350},
    "Educación": {"min": 240, "max": 340},
    "Artes": {"min": 230, "max": 330}
}

# Inicializar la app
app = Dash(__name__)

# Crear dropdowns
dropdowns = []
for col in X.columns:
    dropdowns.append(html.Div([
        html.Label(f'Seleccione {col}'),
        dcc.Dropdown(
            id=f'dropdown-{col}',
            options=[{'label': i, 'value': i} for i in X[col].unique()],
            multi=True
        )
    ]))

# Layout de la aplicación
app.layout = html.Div([
    html.H1("Seleccionar Valores para cada Categoría"),
    html.Div(dropdowns),
    html.Button('Guardar Selección', id='save-button', n_clicks=0),
    html.Div(id='selected-values'),
    html.Div(id='aptitudes-carrera')
])

# Callback para guardar los valores seleccionados y hacer las predicciones
@app.callback(
    [Output('selected-values', 'children'),
     Output('aptitudes-carrera', 'children')],
    [Input('save-button', 'n_clicks')],
    [State(f'dropdown-{col}', 'value') for col in X.columns]
)
def save_selections(n_clicks, *values):
    if n_clicks > 0:
        selected_data = {col: val for col, val in zip(X.columns, values)}
        selected_df = pd.DataFrame(selected_data)
        
        # Asegurarse de que selected_df tenga el mismo formato que X
        selected_df = pd.concat([X, selected_df], ignore_index=True)
        # Convertir a dummies y escalar los datos
        selected_dummies = pd.get_dummies(selected_df).astype(int)
        selected_dummies = np.array(selected_dummies)
        selected_dummies = selected_dummies[:30000]
        selected_dummies = selected_dummies[:, :-2].copy()
        std_scl = StandardScaler()
        std_scl.fit(selected_dummies)

        selected_scaled = std_scl.transform(selected_dummies)
        
        # Hacer predicciones con todos los modelos
        predictions = {name: model.predict(selected_scaled).flatten()[-1] for name, model in models.items()}
        
        # Crear el DataFrame para la gráfica
        df_result = pd.DataFrame({
            'Competencia': list(predictions.keys()),
            'Predicción': list(predictions.values())
        }).sort_values(by='Predicción', ascending=False)

        # Crear gráfica de barras
        colors = ['green' if val == max(df_result['Predicción']) else 'red' if val == min(df_result['Predicción']) else 'blue' for val in df_result['Predicción']]
        fig = go.Figure(go.Bar(
            x=df_result['Predicción'],
            y=df_result['Competencia'],
            orientation='h',
            marker=dict(color=colors)
        ))
        fig.update_layout(title='Predicciones por Competencia')
        
        # Calcular puntajes ponderados por carrera
        puntajes_ponderados = {}
        for carrera, ponderaciones in ponderaciones_puntaje.items():
            puntaje = 0
            for competencia, porcentaje in ponderaciones.items():
                if competencia != 'Total':
                    puntaje += predictions[competencia] * (float(porcentaje.strip('%')) / 100)
            puntajes_ponderados[carrera] = puntaje
        
        # Evaluar si los puntajes entran en alguno de los rangos
        carreras_aptitud = []
        for carrera, puntaje in puntajes_ponderados.items():
            for rango_carrera, rango in rangos_puntaje.items():
                if rango['min'] <= puntaje <= rango['max']:
                    carreras_aptitud.append(rango_carrera)
        
        if carreras_aptitud:
            aptitudes_message = f"El estudiante podría tener opciones para las siguientes carreras: {', '.join(carreras_aptitud)}"
        else:
            aptitudes_message = "El estudiante tiene opción para unirse a la carrera de música"
        
        return html.Div([
            dcc.Graph(figure=fig)
        ]), html.Div([
            html.H3(aptitudes_message)
        ])
    return '', ''

if __name__ == '__main__':
    app.run_server(debug=True)