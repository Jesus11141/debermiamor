"""
DATOS REALES - PLANILLA ELÉCTRICA PRONACA PIFO
Consumo en USD por mes: 2024, 2025, 2026
"""

import pandas as pd
import numpy as np

def generar_datos_pronaca():

    # ── DATOS REALES DE PLANILLA ───────────────────────────────────────────────
    datos_reales = {
        2024: {
            1: 64548.63,  2: 76034.86,  3: 68669.84,
            4: 73129.23,  5: 66992.87,  6: 60683.71,
            7: 79655.62,  8: 74259.72,  9: 70031.98,
           10: 66724.39, 11: 44333.16, 12: 21559.95,
        },
        2025: {
            1: 41559.82,  2: 67193.66,  3: 132012.70,
            4: 70343.94,  5: 72467.58,  6: 81301.98,
            7: 73120.46,  8: 164415.34, 9: 90510.87,
           10: 103278.23, 11: 84786.43, 12: 80304.72,
        },
        2026: {
            1: 83770.95,  2: 88363.20,  3: 78756.31,
        },
    }

    # Tarifa promedio industrial Ecuador: $0.09/kWh
    TARIFA = 0.09

    filas = []
    for anio, meses in datos_reales.items():
        for mes, costo_usd in meses.items():
            # Convertir costo a kWh estimado
            kwh_estimado = costo_usd / TARIFA
            dias_mes = pd.Period(f"{anio}-{mes:02d}").days_in_month

            # Distribuir en días con variación realista
            np.random.seed(anio * 100 + mes)
            pesos = np.random.dirichlet(np.ones(dias_mes) * 5)
            kwh_diarios = pesos * kwh_estimado

            fechas = pd.date_range(
                start=f"{anio}-{mes:02d}-01",
                periods=dias_mes, freq="D"
            )

            for fecha, kwh in zip(fechas, kwh_diarios):
                filas.append({
                    "fecha":       fecha,
                    "consumo_kwh": kwh,
                    "costo_usd":   kwh * TARIFA,
                })

    df = pd.DataFrame(filas)
    df["anio"]       = df["fecha"].dt.year
    df["mes"]        = df["fecha"].dt.month
    df["mes_nombre"] = df["fecha"].dt.strftime("%b")
    df["trimestre"]  = df["fecha"].dt.quarter
    df["dia_semana"] = df["fecha"].dt.day_name()
    df["semana"]     = df["fecha"].dt.isocalendar().week.astype(int)
    df["demanda_kw"] = df["consumo_kwh"] / np.random.uniform(14, 18, len(df))

    return df


def resumen_mensual_real():
    """Devuelve exactamente los datos de planilla originales"""
    datos_reales = {
        2024: {1:64548.63, 2:76034.86, 3:68669.84, 4:73129.23,
               5:66992.87, 6:60683.71, 7:79655.62, 8:74259.72,
               9:70031.98, 10:66724.39, 11:44333.16, 12:21559.95},
        2025: {1:41559.82, 2:67193.66, 3:132012.70, 4:70343.94,
               5:72467.58, 6:81301.98, 7:73120.46, 8:164415.34,
               9:90510.87, 10:103278.23, 11:84786.43, 12:80304.72},
        2026: {1:83770.95, 2:88363.20, 3:78756.31},
    }
    meses_str = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",
                 6:"Junio",7:"Julio",8:"Agosto",9:"Septiembre",
                 10:"Octubre",11:"Noviembre",12:"Diciembre"}
    filas = []
    for anio, meses in datos_reales.items():
        for mes, costo in meses.items():
            filas.append({
                "anio": anio,
                "mes": mes,
                "mes_nombre": meses_str[mes],
                "costo_usd": costo,
                "consumo_kwh": costo / 0.09,
            })
    return pd.DataFrame(filas)


def resumen_mensual(df):
    return df.groupby(["anio","mes","mes_nombre"]).agg(
        consumo_total=("consumo_kwh","sum"),
        consumo_promedio=("consumo_kwh","mean"),
        costo_total=("costo_usd","sum"),
        demanda_max=("demanda_kw","max"),
    ).reset_index()


def resumen_anual(df):
    return df.groupby("anio").agg(
        consumo_total=("consumo_kwh","sum"),
        costo_total=("costo_usd","sum"),
        demanda_max=("demanda_kw","max"),
        dias=("consumo_kwh","count"),
    ).reset_index()


if __name__ == "__main__":
    df = generar_datos_pronaca()
    print("=== PLANILLA REAL PRONACA PIFO ===")
    print(resumen_anual(df).to_string(index=False))
    print("\n=== DETALLE MENSUAL ===")
    print(resumen_mensual_real().to_string(index=False))
