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

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


def dashboard01():
    query = cnst.CONSULTA_JUGADOR
    query2 = cnst.CONSULTA_VALORES
    df_jugador, df_valores = conexion.obtener_datos(query, query2)
    df = pd.merge(df_jugador, df_valores)
    jugadores_posicion = px.bar(df, x="nombre", y="valor_mercado_millones",
                                       color="posicion", title="Valor de los jugadores por su posicion")

    return dbc.Container([
        dbc.Row([html.P("Objetivos: Mostrar el número de jugadores por país, equipo y cuales son los de mayor precio en el mercado")]),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="dropdown-paises",
                    options=[{"label": pais, "value": pais} for pais in df["nacionalidad"].unique()],
                    value=None,
                    multi=False,
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
    graf_mejores = px.bar(mejores_equipos, x="equipo", y="valor_mercado_millones",
                          title="Top 10 Equipos con el mejor valor del mercado").update_layout(yaxis_title="Valor en el mercado")
    peores_equipos = df_d2.groupby("equipo")["valor_mercado_millones"].sum().nsmallest(5).reset_index()


    graf_peores = px.pie(peores_equipos, names="equipo", values="valor_mercado_millones",
                     title="Top 10 Equipos con el peor valor en el mercado")
    return dbc.Container([
        dbc.Row([html.P(
        "Objetivos: Mostrar los equipos con más jugadores, la cantidad de jugadores por equipo y qué equipo tiene a más jugadores en el top 50")]),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                id="dropdown-equipos",
                options=[{"label": equipo, "value": equipo} for equipo in df_d2["equipo"].unique()],
                value=None,
                multi=False,
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
        filtered_df = df[df["nacionalidad"] == selected_pais]
    figure = px.bar(filtered_df, x="nacionalidad", title="Jugadores por País").update_layout(
        yaxis_title="Cantidad de jugadores")
    return figure

if __name__ == "__main__":
    app.run_server(debug=True)
