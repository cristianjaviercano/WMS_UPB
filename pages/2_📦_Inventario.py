import streamlit as st
import pandas as pd
import database

st.set_page_config(page_title="Inventario Actual", page_icon="📦", layout="wide")

st.markdown("# 📦 Inventario General")
st.write("Vista en tiempo real de las existencias en el centro de acopio.")

# Reload data button
if st.button("🔄 Actualizar Datos"):
    st.cache_data.clear()

# Load data
try:
    df = database.get_inventory()
    
    if df.empty:
        st.info("El inventario está vacío. Registra donaciones para comenzar.")
    else:
        # Filters
        with st.expander("🔎 Filtros Avanzados"):
            col1, col2 = st.columns(2)
            with col1:
                cat_filter = st.multiselect("Filtrar por Categoría", options=df['category'].unique())
            with col2:
                status_filter = st.multiselect("Filtrar por Estado", options=df['status'].unique())
        
        # Apply filters
        df_filtered = df.copy()
        if cat_filter:
            df_filtered = df_filtered[df_filtered['category'].isin(cat_filter)]
        if status_filter:
            df_filtered = df_filtered[df_filtered['status'].isin(status_filter)]
            
        # Display Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Ítems (Registros)", len(df_filtered))
        col2.metric("Total Unidades (Suma)", int(df_filtered['quantity'].sum()))
        col3.metric("Categorías Únicas", df_filtered['category'].nunique())

        # Main Table
        st.dataframe(
            df_filtered,
            use_container_width=True,
            column_config={
                "entry_date": st.column_config.DatetimeColumn("Fecha Ingreso", format="D MMM YYYY, h:mm a"),
                "expiration_date": st.column_config.DateColumn("Vencimiento"),
                "quantity": st.column_config.NumberColumn("Cantidad", format="%d"),
            },
            hide_index=True
        )
        
        # Download Option
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte CSV",
            data=csv,
            file_name='inventario_upb_solidaria.csv',
            mime='text/csv',
        )

except Exception as e:
    st.error(f"Error al cargar el inventario: {e}")
