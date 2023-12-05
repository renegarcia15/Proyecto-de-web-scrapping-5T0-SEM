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


if __name__ == "__main__":
    app.run_server(debug=True)
