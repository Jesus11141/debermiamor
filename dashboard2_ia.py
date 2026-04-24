"""
DASHBOARD 2 - HERRAMIENTA DE IA (Machine Learning)
Modelo Dinámico de Datos - Consumo Eléctrico PRONACA Pifo 2022-2024
IA: Regresión Polinomial + Detección de Anomalías (Z-Score) + Recomendaciones automáticas
"""

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_percentage_error
from scipy import stats
from datos_pronaca import generar_datos_pronaca, resumen_mensual

df = generar_datos_pronaca()


def entrenar_modelo_ia(df):
    df_s = df.sort_values("fecha").copy()
    df_s["t"] = (df_s["fecha"] - df_s["fecha"].min()).dt.days
    X = df_s[["t"]].values
    y = df_s["consumo_kwh"].values
    poly = PolynomialFeatures(degree=3)
    Xp = poly.fit_transform(X)
    modelo = LinearRegression().fit(Xp, y)
    t_max = df_s["t"].max()
    t_fut = np.arange(t_max + 1, t_max + 366).reshape(-1, 1)
    fechas_fut = pd.date_range(df_s["fecha"].max() + pd.Timedelta(days=1), periods=365)
    y_pred = modelo.predict(poly.transform(t_fut))
    mape = mean_absolute_percentage_error(y, modelo.predict(Xp)) * 100
    return fechas_fut, y_pred, mape, poly


def detectar_anomalias(df, umbral=2.5):
    z = np.abs(stats.zscore(df["consumo_kwh"]))
    return df[z > umbral].copy()


def generar_recomendaciones(df, anomalias):
    promedio = df["consumo_kwh"].mean()
    max_dia = df.loc[df["consumo_kwh"].idxmax(), "fecha"]
    pct_finde = df[df["dia_semana"].isin(["Saturday","Sunday"])]["consumo_kwh"].mean() / promedio * 100
    tendencia = (df[df["anio"]==2024]["consumo_kwh"].mean() - df[df["anio"]==2022]["consumo_kwh"].mean()) / df[df["anio"]==2022]["consumo_kwh"].mean() * 100
    rec = []
    if tendencia > 5:
        rec.append(f"📈 Tendencia creciente del {tendencia:.1f}% en 3 años. Evaluar eficiencia energética o paneles solares.")
    if pct_finde > 60:
        rec.append(f"🏭 Consumo fin de semana = {pct_finde:.0f}% del promedio. Revisar equipos en stand-by.")
    if len(anomalias) > 10:
        rec.append(f"⚠️ Se detectaron {len(anomalias)} días anómalos. Revisar mantenimiento de equipos.")
    rec.append(f"💡 Pico histórico: {max_dia.strftime('%d/%m/%Y')}. Programar mantenimiento preventivo.")
    rec.append("🔋 Implementar sistema de gestión de energía (SCADA/EMS) para reducir demanda pico.")
    return rec


fechas_pred, consumo_pred, mape, poly = entrenar_modelo_ia(df)
anomalias = detectar_anomalias(df)
recomendaciones = generar_recomendaciones(df, anomalias)

ESTILO_TH = {"color": "#cc99ff", "padding": "8px", "borderBottom": "1px solid #333", "textAlign": "left"}
ESTILO_TD = {"color": "#e6e6e6", "padding": "6px 8px", "borderBottom": "1px solid #222"}


def kpi_dark(titulo, valor, color):
    return html.Div(style={
        "backgroundColor": "#161b22", "padding": "15px", "borderRadius": "10px",
        "flex": 1, "borderLeft": f"5px solid {color}"
    }, children=[
        html.P(titulo, style={"margin": 0, "color": "#888", "fontSize": "12px"}),
        html.H3(valor, style={"margin": "5px 0 0 0", "color": color}),
    ])


app = Dash(__name__)
app.title = "PRONACA Pifo - Dashboard IA"

app.layout = html.Div(
    style={"fontFamily": "Segoe UI, sans-serif", "backgroundColor": "#0d1117", "padding": "20px", "minHeight": "100vh"},
    children=[
        html.Div(style={"background": "linear-gradient(135deg, #7b2d8b, #1a1a2e)", "padding": "20px",
                        "borderRadius": "10px", "marginBottom": "20px"}, children=[
            html.H1("🤖 PRONACA Pifo — Dashboard IA | Predicción & Anomalías",
                    style={"color": "white", "margin": 0, "fontSize": "22px"}),
            html.P(f"Dashboard 2 | Machine Learning | Regresión Polinomial + Z-Score | MAPE: {mape:.2f}%",
                   style={"color": "#cc99ff", "margin": "5px 0 0 0"}),
        ]),

        html.Div(style={"display": "flex", "gap": "15px", "marginBottom": "20px"}, children=[
            kpi_dark("Precisión del Modelo IA", f"{100-mape:.1f}%", "#2ca02c"),
            kpi_dark("Anomalías Detectadas", f"{len(anomalias)} días", "#d62728"),
            kpi_dark("Predicción Promedio 2025", f"{np.mean(consumo_pred):,.0f} kWh/día", "#ff7f0e"),
            kpi_dark("Costo Proyectado 2025", f"${np.sum(consumo_pred)*0.09/1e3:,.1f}K USD", "#1f77b4"),
        ]),

        html.Div(style={"backgroundColor": "#161b22", "padding": "12px", "borderRadius": "8px",
                        "marginBottom": "15px", "display": "flex", "gap": "20px", "alignItems": "center"}, children=[
            html.Label("Vista IA:", style={"color": "white", "fontWeight": "bold"}),
            dcc.RadioItems(
                id="vista-ia",
                options=[
                    {"label": " Predicción 2025", "value": "pred"},
                    {"label": " Anomalías", "value": "anom"},
                    {"label": " Descomposición", "value": "descomp"},
                ],
                value="pred", inline=True,
                style={"color": "white"},
                labelStyle={"marginRight": "20px", "color": "white"},
            ),
        ]),

        html.Div(style={"backgroundColor": "#161b22", "borderRadius": "10px", "padding": "10px",
                        "marginBottom": "15px"}, children=[
            dcc.Graph(id="grafico-ia-principal", style={"height": "400px"}),
        ]),

        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "15px", "marginBottom": "15px"}, children=[
            html.Div(style={"backgroundColor": "#161b22", "borderRadius": "10px", "padding": "10px"}, children=[
                dcc.Graph(id="grafico-distribucion", style={"height": "300px"}),
            ]),
            html.Div(style={"backgroundColor": "#161b22", "borderRadius": "10px", "padding": "20px"}, children=[
                html.H3("🤖 Recomendaciones IA", style={"color": "#cc99ff", "marginTop": 0}),
                html.Ul([
                    html.Li(r, style={"color": "#e6e6e6", "marginBottom": "10px", "lineHeight": "1.5"})
                    for r in recomendaciones
                ]),
            ]),
        ]),

        html.Div(style={"backgroundColor": "#161b22", "borderRadius": "10px", "padding": "15px"}, children=[
            html.H3("⚠️ Días con Consumo Anómalo (Top 10)", style={"color": "#ff6b6b", "marginTop": 0}),
            html.Div(id="tabla-anomalias"),
        ]),
    ]
)


@app.callback(
    Output("grafico-ia-principal", "figure"),
    Output("grafico-distribucion", "figure"),
    Output("tabla-anomalias", "children"),
    Input("vista-ia", "value"),
)
def actualizar_ia(vista):
    if vista == "pred":
        fig = go.Figure()
        hist = df.set_index("fecha")["consumo_kwh"].resample("ME").mean()
        fig.add_trace(go.Scatter(x=hist.index, y=hist.values, name="Histórico",
                                 line=dict(color="#1f77b4", width=2)))
        pred_s = pd.Series(consumo_pred, index=fechas_pred)
        pred_m = pred_s.resample("ME").mean()
        fig.add_trace(go.Scatter(x=pred_m.index, y=pred_m.values, name="Predicción IA 2025",
                                 line=dict(color="#ff7f0e", width=2, dash="dash")))
        fig.add_trace(go.Scatter(
            x=list(pred_m.index) + list(pred_m.index[::-1]),
            y=list(pred_m.values * 1.05) + list(pred_m.values[::-1] * 0.95),
            fill="toself", fillcolor="rgba(255,127,14,0.15)",
            line=dict(color="rgba(0,0,0,0)"), name="Intervalo 95%",
        ))
        fig.update_layout(title="Predicción IA del Consumo 2025 (Regresión Polinomial)",
                          xaxis_title="Fecha", yaxis_title="kWh promedio mensual",
                          template="plotly_dark", legend=dict(orientation="h"))

    elif vista == "anom":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["fecha"], y=df["consumo_kwh"],
                                 mode="lines", name="Consumo", line=dict(color="#4a9eff", width=1)))
        fig.add_trace(go.Scatter(x=anomalias["fecha"], y=anomalias["consumo_kwh"],
                                 mode="markers", name="Anomalía",
                                 marker=dict(color="red", size=8, symbol="x")))
        fig.update_layout(title="Detección de Anomalías (Z-Score > 2.5σ)",
                          xaxis_title="Fecha", yaxis_title="kWh",
                          template="plotly_dark", legend=dict(orientation="h"))

    else:
        df_d = df.set_index("fecha")["consumo_kwh"].resample("ME").mean().reset_index()
        df_d.columns = ["fecha", "consumo"]
        df_d["tendencia"] = df_d["consumo"].rolling(3, center=True).mean()
        df_d["estacional"] = df_d["consumo"] - df_d["tendencia"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_d["fecha"], y=df_d["consumo"], name="Original", line=dict(color="#4a9eff")))
        fig.add_trace(go.Scatter(x=df_d["fecha"], y=df_d["tendencia"], name="Tendencia", line=dict(color="#ff7f0e", width=3)))
        fig.add_trace(go.Bar(x=df_d["fecha"], y=df_d["estacional"], name="Estacional",
                             marker_color="rgba(44,160,44,0.5)"))
        fig.update_layout(title="Descomposición: Tendencia + Estacionalidad",
                          template="plotly_dark", legend=dict(orientation="h"))

    fig_dist = go.Figure()
    for anio, color in [("2022", "#1f77b4"), ("2023", "#ff7f0e"), ("2024", "#2ca02c")]:
        datos = df[df["anio"] == int(anio)]["consumo_kwh"]
        fig_dist.add_trace(go.Histogram(x=datos, name=anio, opacity=0.7, marker_color=color, nbinsx=40))
    fig_dist.update_layout(title="Distribución del Consumo por Año",
                           xaxis_title="kWh/día", yaxis_title="Frecuencia",
                           barmode="overlay", template="plotly_dark", legend=dict(orientation="h"))

    top = anomalias.nlargest(10, "consumo_kwh")[["fecha", "consumo_kwh", "costo_usd", "dia_semana"]]
    filas = [html.Tr([html.Th("Fecha", style=ESTILO_TH), html.Th("Consumo (kWh)", style=ESTILO_TH),
                      html.Th("Costo (USD)", style=ESTILO_TH), html.Th("Día", style=ESTILO_TH)])]
    for _, row in top.iterrows():
        filas.append(html.Tr([
            html.Td(row["fecha"].strftime("%d/%m/%Y"), style=ESTILO_TD),
            html.Td(f"{row['consumo_kwh']:,.0f}", style={**ESTILO_TD, "color": "#ff6b6b"}),
            html.Td(f"${row['costo_usd']:,.2f}", style=ESTILO_TD),
            html.Td(row["dia_semana"], style=ESTILO_TD),
        ]))
    tabla = html.Table(filas, style={"width": "100%", "borderCollapse": "collapse"})

    return fig, fig_dist, tabla


if __name__ == "__main__":
    print("Dashboard 2 (IA) en http://127.0.0.1:8051")
    app.run(debug=True, port=8051)
