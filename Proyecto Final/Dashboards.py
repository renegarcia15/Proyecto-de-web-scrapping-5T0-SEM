import pandas as pd
from dash import Dash, dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import CONSTANTES as cnst
import sqlalchemy as alch

class Conexion:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conexion = None

    def conectar(self):
        self.conexion = alch.create_engine(f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}/{self.database}").connect()

    def desconectar(self):
        if self.conexion:
            self.conexion.close()

    def obtener_datos(self, consulta1, consulta2):
        try:
            self.conectar()
            df_jugador = pd.read_sql_query(consulta1, self.conexion)
            df_valores = pd.read_sql_query(consulta2, self.conexion)
            return df_jugador, df_valores
        finally:
            self.desconectar()

conexion = Conexion(
    cnst.HOST,
    cnst.USER,
    cnst.PASSWORD,
    cnst.DATABASE
)

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)


def dashboard01():
    query = cnst.CONSULTA_JUGADOR
    query2 = cnst.CONSULTA_VALORES
    df_jugador, df_valores = conexion.obtener_datos(query, query2)
    df = pd.merge(df_jugador, df_valores)
    jugadores_posicion = px.bar(df, x="nombre", y="valor_mercado_millones",
                                        title="Valor de los jugadores por su posicion",color="nombre")
    return dbc.Container([
        dbc.Row([html.P("Objetivos: Mostrar el número de jugadores por país, los jugadores mas caros y baratos (Top 10) y cuales son los de mayor precio en el mercado en base a su posicion")]),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="dropdown-paises",
                    options=[{"label": pais, "value": pais} for pais in df["nacionalidad"].unique()],
                    value=None,
                    multi=True,
                    placeholder="Selecciona país"
                ),
            ], width=6),
            dbc.Col(dcc.Graph(id="grafica-por-pais"))
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="dropdown-nombres-valores",
                    options=[
                        {"label": "Jugadores Caros", "value": "caros"},
                        {"label": "Jugadores Baratos", "value": "baratos"}
                    ],
                    value="caros",
                    multi=False,
                    placeholder="Selecciona tipo de jugadores"
                ),
            ], width=6),
            dbc.Col(dcc.Graph(id="grafica-jugadores"))
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="dropdown-posiciones",
                    options=[{"label": posicion, "value": posicion} for posicion in df["posicion"].unique()],
                    value=None,
                    multi=False,
                    placeholder="Selecciona posición"
                ),
            ], width=6),
            dbc.Col(dcc.Graph(id="grafica-jugadores-posicion", figure=jugadores_posicion))
        ]),
    ])

def dashboard02():
    eq = cnst.CONSULTA_EQUIPOS
    val = cnst.CONSULTA_VALORES
    df_jugador, df_valores = conexion.obtener_datos(eq, val)
    df_d2 = pd.merge(df_jugador, df_valores)
    mejores_equipos = df_d2.groupby("equipo")["valor_mercado_millones"].sum().nlargest(10).reset_index()
    graf_mejores = px.bar(mejores_equipos, x="valor_mercado_millones", y="equipo",color="equipo",
                          title="Top 10 Equipos con el mejor valor del mercado").update_layout(yaxis_title="Equipos")
    peores_equipos = df_d2.groupby("equipo")["valor_mercado_millones"].sum().nsmallest(5).reset_index()


    graf_peores = px.bar(peores_equipos, x="equipo", y="valor_mercado_millones",
                     title="Top 5 Equipos con el peor valor en el mercado",color="equipo")
    return dbc.Container([
        dbc.Row([html.P(
        "Objetivos: Mostrar la cantidad de jugadores por equipo, equipos con el mejor valor en el mercado (Top 10) y a los equipos con el peor valor en el mercado (Top 5)")]),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                id="dropdown-equipos",
                options=[{"label": equipo, "value": equipo} for equipo in df_d2["equipo"].unique()],
                value=None,
                multi=True,
                placeholder="Selecciona equipo"
            ),
        ], width=6),
        dbc.Col(dcc.Graph(id="grafica-equipos"))
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafica-top-equipos", figure=graf_mejores))
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafica-peores-equipos", figure=graf_peores))
    ]),
])

app.layout = html.Div([
    html.H2("Proyecto final Transfermarkt"),
    html.P(
        "Integrantes: Contreras Ramirez Juan Manuel, Garcia Soto Rene, Gutierrez Acosta Axel Michel, Guzman Hernandez Jose Iñaki, Rueda Franco Julian Fernando"),
    dcc.Tabs([
        dcc.Tab(label="Jugadores", children=[dashboard01()]),
        dcc.Tab(label="Equipos", children=[dashboard02()]),
    ])
])


@app.callback(
    Output("grafica-por-pais", "figure"),
    [Input("dropdown-paises", "value")]
)
def act_graficaPais(selected_pais):
    query = cnst.CONSULTA_JUGADOR
    query2 = cnst.CONSULTA_VALORES
    df_jugador, df_valores = conexion.obtener_datos(query, query2)
    df = pd.merge(df_jugador, df_valores)
    if not selected_pais:
        filtered_df = df
    else:
        filtered_df = df[df["nacionalidad"].isin(selected_pais)]
    figure = px.bar(filtered_df, x="nacionalidad", title="Jugadores por País").update_layout(
        yaxis_title="Cantidad de jugadores")
    figure.update_traces(marker_color = 'green', marker_line_color = 'black',
                  marker_line_width = 2, opacity = 1)
    return figure
@app.callback(
    Output("grafica-jugadores", "figure"),
    [Input("dropdown-nombres-valores", "value")]
)
def act_graficaJugador(selected_tipo):
    query = cnst.CONSULTA_JUGADOR
    query2 = cnst.CONSULTA_VALORES
    df_jugador, df_valores = conexion.obtener_datos(query, query2)
    df = pd.merge(df_jugador, df_valores)
    if selected_tipo == "caros":
        filtered_df = df.nlargest(10, "valor_mercado_millones")
    elif selected_tipo == "baratos":
        filtered_df = df.nsmallest(10, "valor_mercado_millones")
    else:
        filtered_df = df
    figure = px.bar(filtered_df, x="nombre", y="valor_mercado_millones",color="nombre", title=f"Jugadores {selected_tipo.capitalize()}").update_layout(yaxis_title="Valor en el mercado")
    return figure

@app.callback(
    Output("grafica-jugadores-posicion", "figure"),
    [Input("dropdown-posiciones", "value")]
)
def act_grafica_posicion(selected_posicion):
    query = cnst.CONSULTA_JUGADOR
    query2 = cnst.CONSULTA_VALORES
    df_jugador, df_valores = conexion.obtener_datos(query, query2)
    df = pd.merge(df_jugador, df_valores)
    if not selected_posicion:
        filtered_df = df
    else:
        filtered_df = df[df["posicion"] == selected_posicion]

    figure = px.bar(filtered_df, x="nombre", y="valor_mercado_millones",color="valor_mercado_millones",color_continuous_scale="viridis",
                          title=f"Valor en el mercado por posicion").update_layout(yaxis_title="Valor en el mercado")
    return figure
@app.callback(
    Output("grafica-equipos", "figure"),
    [Input("dropdown-equipos", "value")]
)
def act_grafica_equipos(selected_equipo):
    eq = cnst.CONSULTA_EQUIPOS
    val = cnst.CONSULTA_VALORES
    df_jugador, df_valores = conexion.obtener_datos(eq, val)
    df_d2 = pd.merge(df_jugador, df_valores)
    if not selected_equipo:
        filtered_df = df_d2
    else:
        filtered_df = df_d2[df_d2["equipo"].isin(selected_equipo)]
    figure = px.histogram(filtered_df, x="equipo",color="equipo",color_discrete_map = {'G1': 'green', 'G2': 'orange'}, title="Jugadores por Equipo").update_layout(yaxis_title="Cantidad de jugadores")
    return figure

@app.callback(
    Output("grafica-valor-jugadores", "figure"),
    [Input("dropdown-nombres-valor-jugadores", "value")]
)
def act_grafica_valor(selected_valor):
    eq = cnst.CONSULTA_EQUIPOS
    val = cnst.CONSULTA_VALORES
    df_jugador, df_valores = conexion.obtener_datos(eq, val)
    df_d2 = pd.merge(df_jugador, df_valores)
    if not selected_valor:
        filtered_df = df_d2
    else:
        filtered_df = df_d2[df_d2["valor_mercado_millones"] == selected_valor]
    figure = px.line(filtered_df, x="nombre", y="valor_mercado_millones", title="Valor de los jugadores").update_layout(yaxis_title="Valor en el mercado")
    return figure
if __name__ == "__main__":
    app.run_server(debug=True)
