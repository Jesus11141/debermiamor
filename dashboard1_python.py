"""
DASHBOARD 1 - PROGRAMA PYTHON (Plotly Dash)
Modelo Dinámico de Datos - Consumo Eléctrico PRONACA Pifo
Datos Reales de Planilla 2024-2026
"""

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datos_pronaca import generar_datos_pronaca, resumen_mensual, resumen_anual, resumen_mensual_real

df       = generar_datos_pronaca()
planilla = resumen_mensual_real()

COLORES = {2024: "#1f77b4", 2025: "#ff7f0e", 2026: "#2ca02c"}
VERDE   = "#006633"

ESTILO_TH = {"color": "white", "padding": "10px", "borderBottom": "2px solid #ccffcc",
             "textAlign": "center", "fontSize": "12px", "backgroundColor": VERDE}
ESTILO_TD = {"color": "#333", "padding": "8px 10px", "borderBottom": "1px solid #ddd",
             "textAlign": "right", "fontSize": "13px"}
ESTILO_TD_MES = {"color": VERDE, "padding": "8px 10px", "borderBottom": "1px solid #ddd",
                 "textAlign": "left", "fontSize": "13px", "fontWeight": "bold"}


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


def construir_tabla():
    meses_orden = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                   "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    anios = sorted(planilla["anio"].unique())

    encabezado = html.Tr([
        html.Th("MES", style=ESTILO_TH),
        *[html.Th(str(a), style={**ESTILO_TH, "color": "#ccffcc"}) for a in anios]
    ])
    filas = [encabezado]
    totales = {a: 0 for a in anios}

    for mes_nombre in meses_orden:
        celdas = [html.Td(mes_nombre, style=ESTILO_TD_MES)]
        for a in anios:
            fila = planilla[(planilla["anio"]==a) & (planilla["mes_nombre"]==mes_nombre)]
            if not fila.empty:
                val = fila["costo_usd"].values[0]
                totales[a] += val
                celdas.append(html.Td(f"${val:,.2f}", style=ESTILO_TD))
            else:
                celdas.append(html.Td("—", style={**ESTILO_TD, "color": "#bbb"}))
        filas.append(html.Tr(celdas))

    fila_total = [html.Td("TOTAL", style={**ESTILO_TD_MES, "color": "#d62728"})]
    for a in anios:
        fila_total.append(html.Td(
            f"${totales[a]:,.2f}",
            style={**ESTILO_TD, "color": "#d62728", "fontWeight": "bold"}
        ))
    filas.append(html.Tr(fila_total))
    return html.Table(filas, style={"width": "100%", "borderCollapse": "collapse"})


app = Dash(__name__)
app.title = "PRONACA Pifo - Consumo Eléctrico"

app.layout = html.Div(
    style={"fontFamily": "Segoe UI, sans-serif", "backgroundColor": "#f0f2f5", "padding": "20px"},
    children=[

        html.Div(style={"backgroundColor": VERDE, "padding": "20px", "borderRadius": "10px", "marginBottom": "20px"}, children=[
            html.H1("⚡ PRONACA Pifo — Consumo Eléctrico 2024–2026",
                    style={"color": "white", "margin": 0, "fontSize": "24px"}),
            html.P("Dashboard 1 | Datos Reales de Planilla Eléctrica | Modelo Dinámico de Datos",
                   style={"color": "#ccffcc", "margin": "5px 0 0 0"}),
        ]),

        html.Div(style={"display": "flex", "gap": "15px", "marginBottom": "20px"}, children=[
            kpi("Facturación Total", f"${planilla['costo_usd'].sum():,.0f} USD", "#1f77b4"),
            kpi("Consumo Estimado", f"{planilla['kwh_estimado'].sum()/1e6:.2f} GWh", "#ff7f0e"),
            kpi("Promedio Mensual", f"${planilla['costo_usd'].mean():,.0f} USD", "#2ca02c"),
            kpi("Mes Máx. Factura", f"${planilla['costo_usd'].max():,.0f} USD", "#d62728"),
            kpi("Mes Mín. Factura", f"${planilla['costo_usd'].min():,.0f} USD", "#9467bd"),
        ]),

        html.Div(style={"backgroundColor": "white", "padding": "15px", "borderRadius": "10px",
                        "marginBottom": "20px", "display": "flex", "gap": "30px", "alignItems": "center"}, children=[
            html.Label("Año:", style={"fontWeight": "bold"}),
            dcc.Checklist(
                id="filtro-anio",
                options=[{"label": f" {a}", "value": a} for a in sorted(planilla["anio"].unique())],
                value=sorted(planilla["anio"].unique()), inline=True,
            ),
            html.Label("Vista:", style={"fontWeight": "bold", "marginLeft": "20px"}),
            dcc.RadioItems(
                id="granularidad",
                options=[{"label": " Mensual",    "value": "mensual"},
                         {"label": " Trimestral", "value": "trimestral"},
                         {"label": " Anual",      "value": "anual"}],
                value="mensual", inline=True,
            ),
        ]),

        html.Div(style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "15px", "marginBottom": "15px"}, children=[
            card(dcc.Graph(id="grafico-serie")),
            card(dcc.Graph(id="grafico-anual")),
        ]),

        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "15px", "marginBottom": "15px"}, children=[
            card(dcc.Graph(id="grafico-heatmap")),
            card(dcc.Graph(id="grafico-acumulado")),
            card(dcc.Graph(id="grafico-variacion")),
        ]),

        # TABLA PLANILLA REAL
        html.Div(style={
            "backgroundColor": "white", "borderRadius": "10px",
            "padding": "20px", "boxShadow": "0 2px 4px rgba(0,0,0,0.1)", "marginBottom": "15px"
        }, children=[
            html.H3("📋 Planilla Eléctrica Real PRONACA Pifo (USD)",
                    style={"color": VERDE, "marginTop": 0}),
            construir_tabla(),
        ]),

        html.Div(style={"textAlign": "center", "color": "#888", "marginTop": "10px"}, children=[
            html.P("Metodología: Definición → Formulación → Colección de Datos → Implementación → Verificación → Experimentación"),
        ]),
    ]
)


@app.callback(
    Output("grafico-serie",      "figure"),
    Output("grafico-anual",      "figure"),
    Output("grafico-heatmap",    "figure"),
    Output("grafico-acumulado",  "figure"),
    Output("grafico-variacion",  "figure"),
    Input("filtro-anio",   "value"),
    Input("granularidad",  "value"),
)
def actualizar(anios, gran):
    dfp = planilla[planilla["anio"].isin(anios)].copy()

    # 1. SERIE PRINCIPAL
    fig_serie = go.Figure()
    for a in sorted(anios):
        d = dfp[dfp["anio"]==a].sort_values("mes")
        color = COLORES.get(a, "#888")
        if gran == "mensual":
            fig_serie.add_trace(go.Scatter(
                x=d["mes_nombre"], y=d["costo_usd"], name=str(a),
                line=dict(color=color, width=2), mode="lines+markers", marker=dict(size=7),
            ))
        elif gran == "trimestral":
            d["trim"] = ((d["mes"]-1)//3 + 1)
            dt = d.groupby("trim")["costo_usd"].sum().reset_index()
            fig_serie.add_trace(go.Bar(
                x=["T1","T2","T3","T4"][:len(dt)], y=dt["costo_usd"],
                name=str(a), marker_color=color,
            ))
        else:
            total = d["costo_usd"].sum()
            fig_serie.add_trace(go.Bar(
                x=[str(a)], y=[total], name=str(a), marker_color=color,
                text=[f"${total:,.0f}"], textposition="outside",
            ))
    fig_serie.update_layout(title="Facturación Eléctrica PRONACA Pifo (USD)",
                            xaxis_title="Período", yaxis_title="USD",
                            legend=dict(orientation="h"), margin=dict(t=40, b=30),
                            barmode="group")

    # 2. BARRAS COMPARATIVAS
    fig_anual = go.Figure()
    for a in sorted(anios):
        d = dfp[dfp["anio"]==a].sort_values("mes")
        fig_anual.add_trace(go.Bar(
            x=d["mes_nombre"], y=d["costo_usd"], name=str(a),
            marker_color=COLORES.get(a, "#888"), opacity=0.85,
        ))
    fig_anual.update_layout(title="Comparativo Mensual (USD)", barmode="group",
                            legend=dict(orientation="h"), margin=dict(t=40, b=30))

    # 3. HEATMAP
    pivot = dfp.pivot(index="mes_nombre", columns="anio", values="costo_usd")
    meses_orden = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                   "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    pivot = pivot.reindex([m for m in meses_orden if m in pivot.index])
    fig_heat = go.Figure(go.Heatmap(
        z=pivot.values, x=[str(c) for c in pivot.columns], y=pivot.index,
        colorscale="YlOrRd", colorbar=dict(title="USD"),
        text=[[f"${v:,.0f}" if not pd.isna(v) else "—" for v in row] for row in pivot.values],
        texttemplate="%{text}",
    ))
    fig_heat.update_layout(title="Heatmap Planilla Real (USD)", margin=dict(t=40, b=30))

    # 4. ACUMULADO
    fig_ac = go.Figure()
    for a in sorted(anios):
        d = dfp[dfp["anio"]==a].sort_values("mes")
        fig_ac.add_trace(go.Scatter(
            x=d["mes_nombre"], y=d["costo_usd"].cumsum(), name=str(a),
            fill="tozeroy", mode="lines", line=dict(color=COLORES.get(a,"#888"), width=2),
        ))
    fig_ac.update_layout(title="Facturación Acumulada en el Año (USD)",
                         legend=dict(orientation="h"), margin=dict(t=40, b=30))

    # 5. VARIACIÓN MES A MES
    df_var = dfp.sort_values(["anio","mes"]).copy()
    df_var["variacion"] = df_var.groupby("anio")["costo_usd"].pct_change() * 100
    fig_var = go.Figure()
    for a in sorted(anios):
        d = df_var[df_var["anio"]==a].dropna()
        fig_var.add_trace(go.Bar(
            x=d["mes_nombre"], y=d["variacion"], name=str(a),
            marker_color=[COLORES.get(a,"#888") if v >= 0 else "#d62728" for v in d["variacion"]],
        ))
    fig_var.add_hline(y=0, line_color="#888", line_width=1)
    fig_var.update_layout(title="Variación Mensual (%)", yaxis_title="%",
                          legend=dict(orientation="h"), margin=dict(t=40, b=30),
                          barmode="group")

    return fig_serie, fig_anual, fig_heat, fig_ac, fig_var


if __name__ == "__main__":
    print("Dashboard 1 en http://127.0.0.1:8050")
    app.run(debug=True, port=8050)
