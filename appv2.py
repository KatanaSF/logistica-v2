import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title="Análisis Logístico Profesional", layout="wide")

st.title("📊 Análisis de Eficiencia Logística Profesional")

# Instrucciones
st.markdown("""
Carga tu archivo Excel con datos logísticos y analiza la eficiencia con gráficos interactivos y reportes detallados.
""")

# Subida de archivo
uploaded_file = st.file_uploader("📁 Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # Validar columnas
        expected_cols = ['fecha', 'vehiculo_id', 'conductor', 'zona', 'n_entregas', 
                         'tiempo_total', 'combustible_usado', 'km_recorridos', 'incidencias']
        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            st.error(f"❌ Faltan columnas en el archivo: {missing_cols}")
        else:
            # Conversión fecha
            df['fecha'] = pd.to_datetime(df['fecha'])

            # Filtros laterales
            st.sidebar.header("Filtros de análisis")
            zonas = df['zona'].unique()
            selected_zonas = st.sidebar.multiselect("Selecciona zonas", zonas, default=zonas)

            conductores = df['conductor'].unique()
            selected_conductores = st.sidebar.multiselect("Selecciona conductores", conductores, default=conductores)

            fechas = df['fecha'].sort_values()
            start_date = st.sidebar.date_input("Fecha inicio", fechas.min())
            end_date = st.sidebar.date_input("Fecha fin", fechas.max())

            # Filtrar datos
            df_filtered = df[
                (df['zona'].isin(selected_zonas)) &
                (df['conductor'].isin(selected_conductores)) &
                (df['fecha'] >= pd.to_datetime(start_date)) &
                (df['fecha'] <= pd.to_datetime(end_date))
            ]

            st.markdown(f"### Datos filtrados: {len(df_filtered)} registros")

            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total entregas", int(df_filtered['n_entregas'].sum()))
            col2.metric("Tiempo total (h)", round(df_filtered['tiempo_total'].sum(), 2))
            col3.metric("Combustible usado (L)", round(df_filtered['combustible_usado'].sum(), 2))
            col4.metric("Km recorridos", round(df_filtered['km_recorridos'].sum(), 2))

            # Gráficos interactivos
            st.markdown("### 📈 Gráficos")

            # Entregas por zona
            entregas_zona = df_filtered.groupby('zona')['n_entregas'].sum().reset_index()
            fig1 = px.bar(entregas_zona, x='zona', y='n_entregas', title="Entregas por Zona")
            st.plotly_chart(fig1, use_container_width=True)

            # Tiempo por conductor
            tiempo_conductor = df_filtered.groupby('conductor')['tiempo_total'].sum().reset_index()
            fig2 = px.bar(tiempo_conductor, x='conductor', y='tiempo_total', title="Tiempo Total por Conductor")
            st.plotly_chart(fig2, use_container_width=True)

            # Evolución Km recorridos en el tiempo
            km_fecha = df_filtered.groupby('fecha')['km_recorridos'].sum().reset_index()
            fig3 = px.line(km_fecha, x='fecha', y='km_recorridos', title="Km Recorridos en el Tiempo")
            st.plotly_chart(fig3, use_container_width=True)

            # Incidencias resumen
            st.markdown("### ⚠️ Incidencias detectadas")
            incidencias_df = df_filtered[df_filtered['incidencias'].notna() & (df_filtered['incidencias'] != '')]
            if not incidencias_df.empty:
                st.dataframe(incidencias_df[['fecha','vehiculo_id','conductor','zona','incidencias']])
            else:
                st.info("No se detectaron incidencias en el filtro actual.")

    except Exception as e:
        st.error(f"Error leyendo el archivo: {e}")

else:
    st.info("Por favor, sube un archivo Excel para comenzar el análisis.")
