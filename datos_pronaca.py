"""
MÓDULO DE DATOS - PRONACA PIFO
Colección de Datos: Simulación realista del consumo eléctrico 2022-2024
Planta de procesamiento avícola con patrones reales de industria alimentaria
"""

import pandas as pd
import numpy as np

def generar_datos_pronaca():
    np.random.seed(42)
    fechas = pd.date_range(start="2022-01-01", end="2024-12-31", freq="D")

    consumo = []
    for fecha in fechas:
        mes = fecha.month
        dia_semana = fecha.dayofweek  # 0=lunes, 6=domingo

        # Base: planta industrial ~8,000 kWh/día
        base = 8000

        # Estacionalidad: más consumo en meses cálidos (refrigeración)
        estacional = 1200 * np.sin(2 * np.pi * (mes - 3) / 12)

        # Patrón semanal: menos producción los domingos
        if dia_semana == 6:
            factor_semana = 0.55
        elif dia_semana == 5:
            factor_semana = 0.80
        else:
            factor_semana = 1.0

        # Tendencia de crecimiento anual (~3% por año)
        anios_desde_inicio = (fecha - fechas[0]).days / 365
        tendencia = 150 * anios_desde_inicio

        # Ruido aleatorio
        ruido = np.random.normal(0, 300)

        valor = (base + estacional + tendencia) * factor_semana + ruido
        consumo.append(max(valor, 1500))  # mínimo operativo

    df = pd.DataFrame({"fecha": fechas, "consumo_kwh": consumo})
    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["mes_nombre"] = df["fecha"].dt.strftime("%b")
    df["semana"] = df["fecha"].dt.isocalendar().week.astype(int)
    df["dia_semana"] = df["fecha"].dt.day_name()
    df["trimestre"] = df["fecha"].dt.quarter

    # Costo estimado: tarifa industrial Ecuador ~$0.09/kWh
    df["costo_usd"] = df["consumo_kwh"] * 0.09

    # Demanda pico simulada (kW) = consumo / horas operativas
    df["demanda_kw"] = df["consumo_kwh"] / np.random.uniform(14, 18, len(df))

    return df


def resumen_mensual(df):
    return df.groupby(["anio", "mes", "mes_nombre"]).agg(
        consumo_total=("consumo_kwh", "sum"),
        consumo_promedio=("consumo_kwh", "mean"),
        costo_total=("costo_usd", "sum"),
        demanda_max=("demanda_kw", "max"),
    ).reset_index()


def resumen_anual(df):
    return df.groupby("anio").agg(
        consumo_total=("consumo_kwh", "sum"),
        costo_total=("costo_usd", "sum"),
        demanda_max=("demanda_kw", "max"),
        dias=("consumo_kwh", "count"),
    ).reset_index()


if __name__ == "__main__":
    df = generar_datos_pronaca()
    print("=== RESUMEN ANUAL PRONACA PIFO ===")
    print(resumen_anual(df).to_string(index=False))
    print(f"\nTotal registros: {len(df)}")
    print(f"Período: {df['fecha'].min().date()} → {df['fecha'].max().date()}")
