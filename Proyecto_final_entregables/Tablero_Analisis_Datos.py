import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from sklearn.preprocessing import StandardScaler
import numpy as np
import psycopg2

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

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Análisis de Puntajes Icfes 2019"),

    html.Div([
        html.Div([
            html.H2("Promedio de Puntajes por Competencia"),
            dcc.Dropdown(
                id='tipo-colegio-dropdown',
                options=[
                    {'label': 'Oficial', 'value': 'OFICIAL'},
                    {'label': 'No Oficial', 'value': 'NO OFICIAL'}
                ],
                value='OFICIAL',
                clearable=False,
                style={"width": "90%"}
            ),
            dcc.Dropdown(
                id='periodo-dropdown',
                options=[
                    {'label': '20191', 'value': '20191'},
                    {'label': '20194', 'value': '20194'}
                ],
                value='20191',
                clearable=False,
                style={"width": "90%"}
            ),
            dcc.Dropdown(
                id='calendario-dropdown',
                options=[
                    {'label': 'Calendario A', 'value': 'A'},
                    {'label': 'Calendario B', 'value': 'B'}
                ],
                value='A',
                clearable=False,
                style={"width": "90%"}
            ),
            dcc.Graph(id='bar-chart', style={"width": "90%"})
        ], style={"width": "50%", "display": "inline-block", "vertical-align": "top"}),

        html.Div([
            html.H2("Resultados por Colegio y Sede"),
            html.Label('Seleccione el Colegio:'),
            dcc.Dropdown(
                id='dropdown-colegio',
                options=[{'label': colegio, 'value': colegio} for colegio in df_sin_nulos['cole_nombre_establecimiento'].unique()],
                value=None
            ),
            html.Label('Seleccione la Sede:'),
            dcc.Dropdown(
                id='dropdown-sede',
                options=[],
                value=None
            ),
            html.Div(id='info-colegio'),
            dcc.Graph(id='grafico-puntajes')
        ], style={"width": "50%", "display": "inline-block", "vertical-align": "top"})
    ]),

    html.Div([
        html.H2("Puntajes Promedio"),
        html.Label("Seleccione la Materia:"),
        dcc.RadioItems(
            id='subject-radio',
            options=[
                {'label': 'Inglés', 'value': 'punt_ingles'},
                {'label': 'Matemáticas', 'value': 'punt_matematicas'},
                {'label': 'Sociales y Ciudadanas', 'value': 'punt_sociales_ciudadanas'},
                {'label': 'Ciencias Naturales', 'value': 'punt_c_naturales'},
                {'label': 'Lectura Crítica', 'value': 'punt_lectura_critica'}
            ],
            value='punt_ingles'
        ),
        html.Label("Seleccione la Categoría:"),
        dcc.Dropdown(
            id='category-dropdown',
            options=[
                {'label': 'Personas en el Hogar', 'value': 'fami_personashogar'},
                {'label': 'Tiene Automóvil', 'value': 'fami_tieneautomovil'},
                {'label': 'Tiene Computador', 'value': 'fami_tienecomputador'},
                {'label': 'Tiene Internet', 'value': 'fami_tieneinternet'},
                {'label': 'Tiene Lavadora', 'value': 'fami_tienelavadora'},
                {'label': 'Educación del Padre', 'value': 'fami_educacionpadre'},
                {'label': 'Educación de la Madre', 'value': 'fami_educacionmadre'},
                {'label': 'Cuartos en el Hogar', 'value': 'fami_cuartoshogar'},
                {'label': 'Estrato de la Vivienda', 'value': 'fami_estratovivienda'}
            ],
            value='fami_estratovivienda'
        ),
        html.Div(id='gauges-container')
    ])
])

# Callback para actualizar el gráfico en base a los dropdowns seleccionados
@app.callback(
    Output('bar-chart', 'figure'),
    Input('tipo-colegio-dropdown', 'value'),
    Input('periodo-dropdown', 'value'),
    Input('calendario-dropdown', 'value')
)
def update_graph(tipo_colegio, periodo, calendario):
    filtered_df = df_sin_nulos[(df_sin_nulos['cole_naturaleza'] == tipo_colegio) &
                               (df_sin_nulos['periodo'] == periodo) &
                               (df_sin_nulos['cole_calendario'] == calendario)]

    # Calcula el promedio de los puntajes
    mean_scores = filtered_df[['punt_matematicas', 'punt_ingles', 'punt_sociales_ciudadanas',
                               'punt_c_naturales', 'punt_lectura_critica']].mean().reset_index()
    mean_scores.columns = ['Competencia', 'Promedio']
    
    # Crea la gráfica de barras
    fig = px.bar(mean_scores, x='Competencia', y='Promedio', title='Promedio de Puntajes por Competencia')
    fig.update_traces(marker_color='#008f39')  
    return fig

# Callback para actualizar las opciones de la sede
@app.callback(
    Output('dropdown-sede', 'options'),
    Input('dropdown-colegio', 'value')
)
def set_sede_options(selected_colegio):
    if selected_colegio:
        filtered_df = df_sin_nulos[df_sin_nulos['cole_nombre_establecimiento'] == selected_colegio]
        return [{'label': sede, 'value': sede} for sede in filtered_df['cole_nombre_sede'].unique()]
    return []

# Callback para mostrar la información del colegio y actualizar el gráfico
@app.callback(
    [Output('info-colegio', 'children'),
     Output('grafico-puntajes', 'figure')],
    [Input('dropdown-colegio', 'value'),
     Input('dropdown-sede', 'value')]
)
def update_output(selected_colegio, selected_sede):
    if selected_colegio and selected_sede:
        filtered_df = df_sin_nulos[(df_sin_nulos['cole_nombre_establecimiento'] == selected_colegio) & (df_sin_nulos['cole_nombre_sede'] == selected_sede)]

        num_hombres = filtered_df[filtered_df['estu_genero'] == 'M'].shape[0]
        num_mujeres = filtered_df[filtered_df['estu_genero'] == 'F'].shape[0]
        bilingue = filtered_df['cole_bilingue'].iloc[0] if not filtered_df['cole_bilingue'].isnull().all() else 'N'
        calendario = filtered_df['cole_calendario'].iloc[0]
        area_ubicacion = filtered_df['cole_area_ubicacion'].iloc[0]
        sede_principal = filtered_df['cole_sede_principal'].iloc[0] if not filtered_df['cole_sede_principal'].isnull().all() else 'N'

        info = html.Div([
            html.P(f"Número de hombres: {num_hombres}"),
            html.P(f"Número de mujeres: {num_mujeres}"),
            html.P(f"Bilingüe: {'Sí' if bilingue == 'S' else 'No'}"),
            html.P(f"Calendario: {calendario}"),
            html.P(f"Área de ubicación: {area_ubicacion}"),
            html.P(f"Sede principal: {'Sí' if sede_principal == 'S' else 'No'}")
        ])

        # Calcular el promedio de los puntajes por materia
        promedio_puntajes = filtered_df[['punt_matematicas', 'punt_ingles', 'punt_sociales_ciudadanas', 'punt_c_naturales', 'punt_lectura_critica']].mean().reset_index()
        promedio_puntajes.columns = ['Materia', 'Puntaje']

        # Crear gráfico de barras horizontales
        fig_barras = px.bar(
            promedio_puntajes,
            x='Puntaje',
            y='Materia',
            orientation='h',
            title='Promedio de Puntajes por Materia'
        )
        fig_barras.update_traces(marker_color='#008f39')  
        return info, fig_barras

    return '', {}

# Callback para actualizar los gráficos de velocímetro
@app.callback(
    Output('gauges-container', 'children'),
    [Input('subject-radio', 'value'),
     Input('category-dropdown', 'value')]
)
def update_gauges(subject, category):
    # Calcular el promedio por categoría
    avg_scores = df_sin_nulos.groupby(category)[subject].mean().reset_index()
    avg_scores = avg_scores.sort_values(by=category)

    # Crear gráficos de velocímetro
    gauges = []
    for _, row in avg_scores.iterrows():
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=row[subject],
            title={'text': f"{category}: {row[category]}"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 100], 'color': "gray"}
                ],
            }
        ))
        gauges.append(dcc.Graph(figure=fig))

    return gauges

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
