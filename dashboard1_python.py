"""
DASHBOARD 1 - PROGRAMA PYTHON (Plotly Dash)
Modelo Dinámico de Datos - Consumo Eléctrico PRONACA Pifo 2022-2024
"""

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datos_pronaca import generar_datos_pronaca, resumen_mensual, resumen_anual

df = generar_datos_pronaca()
COLORES = {"2022": "#1f77b4", "2023": "#ff7f0e", "2024": "#2ca02c"}
VERDE = "#006633"


def kpi(titulo, valor, color):
    return html.Div(style={
        "backgroundColor": "white", "padding": "15px", "borderRadius": "10px",
        "flex": 1, "borderLeft": f"5px solid {color}", "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
    }, children=[
        html.P(titulo, style={"margin": 0, "color": "#666", "fontSize": "12px"}),
        html.H3(valor, style={"margin": "5px 0 0 0", "color": color}),
    ])


def card(children):
    return html.Div(style={
        "backgroundColor": "white", "borderRadius": "10px",
        "padding": "10px", "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
    }, children=[children])


app = Dash(__name__)
app.title = "PRONACA Pifo - Consumo Eléctrico"

app.layout = html.Div(
    style={"fontFamily": "Segoe UI, sans-serif", "backgroundColor": "#f0f2f5", "padding": "20px"},
    children=[
        html.Div(style={"backgroundColor": VERDE, "padding": "20px", "borderRadius": "10px", "marginBottom": "20px"}, children=[
            html.H1("⚡ PRONACA Pifo — Consumo Eléctrico 2022–2024",
                    style={"color": "white", "margin": 0, "fontSize": "24px"}),
            html.P("Dashboard 1 | Modelo Dinámico de Datos | Simulación Industrial",
                   style={"color": "#ccffcc", "margin": "5px 0 0 0"}),
        ]),

        html.Div(style={"display": "flex", "gap": "15px", "marginBottom": "20px"}, children=[
            kpi("Total Consumo 3 años", f"{df['consumo_kwh'].sum()/1e6:.2f} GWh", "#1f77b4"),
            kpi("Costo Total Estimado", f"${df['costo_usd'].sum()/1e6:.2f}M USD", "#ff7f0e"),
            kpi("Promedio Diario", f"{df['consumo_kwh'].mean():,.0f} kWh", "#2ca02c"),
            kpi("Demanda Pico Máx.", f"{df['demanda_kw'].max():,.0f} kW", "#d62728"),
        ]),

        html.Div(style={"backgroundColor": "white", "padding": "15px", "borderRadius": "10px",
                        "marginBottom": "20px", "display": "flex", "gap": "30px", "alignItems": "center"}, children=[
            html.Label("Año:", style={"fontWeight": "bold"}),
            dcc.Checklist(
                id="filtro-anio",
                options=[{"label": f" {a}", "value": a} for a in [2022, 2023, 2024]],
                value=[2022, 2023, 2024], inline=True,
            ),
            html.Label("Granularidad:", style={"fontWeight": "bold", "marginLeft": "20px"}),
            dcc.RadioItems(
                id="granularidad",
                options=[{"label": " Diario", "value": "D"},
                         {"label": " Semanal", "value": "W"},
                         {"label": " Mensual", "value": "ME"}],
                value="ME", inline=True,
            ),
        ]),

        html.Div(style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "15px", "marginBottom": "15px"}, children=[
            card(dcc.Graph(id="grafico-serie")),
            card(dcc.Graph(id="grafico-anual")),
        ]),

        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "15px", "marginBottom": "15px"}, children=[
            card(dcc.Graph(id="grafico-heatmap")),
            card(dcc.Graph(id="grafico-semana")),
            card(dcc.Graph(id="grafico-costo")),
        ]),

        html.Div(style={"textAlign": "center", "color": "#888", "marginTop": "10px"}, children=[
            html.P("Metodología: Definición → Formulación → Colección de Datos → Implementación → Verificación → Experimentación"),
        ]),
    ]
)


@app.callback(
    Output("grafico-serie", "figure"),
    Output("grafico-anual", "figure"),
    Output("grafico-heatmap", "figure"),
    Output("grafico-semana", "figure"),
    Output("grafico-costo", "figure"),
    Input("filtro-anio", "value"),
    Input("granularidad", "value"),
)
def actualizar(anios, gran):
    dff = df[df["anio"].isin(anios)].copy()

    # 1. SERIE TEMPORAL
    serie = dff.set_index("fecha")["consumo_kwh"].resample(gran).mean()
    fig_serie = go.Figure()
    for anio in sorted(anios):
        s = serie[serie.index.year == anio]
        fig_serie.add_trace(go.Scatter(x=s.index, y=s.values, name=str(anio),
                                       line=dict(color=COLORES[str(anio)], width=2), mode="lines"))
    fig_serie.update_layout(title="Consumo Eléctrico en el Tiempo (kWh)",
                            xaxis_title="Fecha", yaxis_title="kWh",
                            legend=dict(orientation="h"), margin=dict(t=40, b=30))

    # 2. BARRAS ANUALES
    df_a = resumen_anual(dff)
    fig_anual = go.Figure(go.Bar(
        x=df_a["anio"].astype(str), y=df_a["consumo_total"] / 1e6,
        marker_color=[COLORES[str(a)] for a in df_a["anio"]],
        text=[f"{v:.2f}" for v in df_a["consumo_total"] / 1e6],
        textposition="outside",
    ))
    fig_anual.update_layout(title="Consumo Total por Año (GWh)",
                            yaxis_title="GWh", margin=dict(t=40, b=30))

    # 3. HEATMAP
    pivot = dff.groupby(["anio", "mes"])["consumo_kwh"].sum().reset_index()
    pivot_t = pivot.pivot(index="mes", columns="anio", values="consumo_kwh")
    meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    fig_heat = go.Figure(go.Heatmap(
        z=pivot_t.values, x=[str(c) for c in pivot_t.columns],
        y=[meses[i-1] for i in pivot_t.index],
        colorscale="YlOrRd", colorbar=dict(title="kWh"),
    ))
    fig_heat.update_layout(title="Heatmap Consumo Mensual", margin=dict(t=40, b=30))

    # 4. PATRÓN SEMANAL
    orden = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    etiq  = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
    sem = dff.groupby("dia_semana")["consumo_kwh"].mean().reindex(orden)
    fig_sem = go.Figure(go.Bar(
        x=etiq, y=sem.values,
        marker_color=[VERDE if d not in ["Saturday","Sunday"] else "#ff7f0e" for d in orden],
    ))
    fig_sem.update_layout(title="Consumo Promedio por Día", yaxis_title="kWh", margin=dict(t=40, b=30))

    # 5. COSTO MENSUAL
    df_c = dff.groupby(["anio", "mes"])["costo_usd"].sum().reset_index()
    fig_costo = px.line(df_c, x="mes", y="costo_usd", color=df_c["anio"].astype(str),
                        color_discrete_map=COLORES, markers=True,
                        labels={"costo_usd": "USD", "mes": "Mes", "color": "Año"})
    fig_costo.update_layout(title="Costo Mensual Estimado (USD)", margin=dict(t=40, b=30))

    return fig_serie, fig_anual, fig_heat, fig_sem, fig_costo


if __name__ == "__main__":
    print("Dashboard 1 en http://127.0.0.1:8050")
    app.run(debug=True, port=8050)
