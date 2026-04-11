import streamlit as st
import pandas as pd
import database
import json

st.set_page_config(page_title="Despachos", page_icon="🚚", layout="wide")

st.markdown("# 🚚 Gestión de Despachos")
st.write("Genera órdenes de salida para enviar ayudas a los damnificados.")

# Tabs for Create Dispatch and View History
tab1, tab2 = st.tabs(["🆕 Nuevo Despacho", "📜 Historial de Despachos"])

with tab1:
    # 1. Select Items to Dispatch
    st.subheader("1. Selección de Ítems a Enviar")
    
    df = database.get_inventory()
    available_df = df[df['status'] == 'Available']
    
    if available_df.empty:
        st.warning("No hay inventario disponible para despachar.")
    else:
        # Group to see total quantities
        stock_summary = available_df.groupby('item_name')['quantity'].sum().reset_index()
        
        # Multiselect for items
        all_items = stock_summary['item_name'].unique()
        selected_items_dispatch = st.multiselect("Seleccionar Productos / Kits", all_items)
        
        dispatch_list = []
        if selected_items_dispatch:
            st.write("Definir cantidades a enviar:")
            for item in selected_items_dispatch:
                max_avail = stock_summary[stock_summary['item_name'] == item]['quantity'].values[0]
                qty = st.number_input(f"Cantidad a enviar de **{item}** (Disp: {max_avail})", min_value=1, max_value=int(max_avail), key=f"disp_{item}")
                dispatch_list.append({'item_name': item, 'quantity': qty})
        
        st.divider()
        
        # 2. Dispatch Info
        st.subheader("2. Información del Despacho")
        col1, col2 = st.columns(2)
        with col1:
            destination = st.text_input("Destino / Lugar de Entrega", placeholder="Ej. Barrio La Playa, Albergue Central...")
        with col2:
            receiver_name = st.text_input("Nombre del Responsable / Receptor", placeholder="Ej. Juan Pérez (Cruz Roja)")
            
        if st.button("🚀 Confirmar Despacho", type="primary", disabled=(not dispatch_list or not destination or not receiver_name)):
            success, msg = database.create_dispatch(destination, receiver_name, dispatch_list)
            if success:
                st.success("✅ Despacho registrado correctamente. El inventario ha sido actualizado.")
                st.balloons()
                st.cache_data.clear()
            else:
                st.error(f"❌ Error al realizar despacho: {msg}")

with tab2:
    st.subheader("Historial de Salidas")
    conn = database.get_connection()
    dispatches_df = pd.read_sql_query("SELECT * FROM dispatches ORDER BY dispatch_date DESC", conn)
    conn.close()
    
    if dispatches_df.empty:
        st.info("No se han registrado despachos aún.")
    else:
        st.dataframe(
            dispatches_df,
            use_container_width=True,
            column_config={
                "dispatch_date": st.column_config.DatetimeColumn("Fecha", format="D MMM YYYY, h:mm a"),
                "items_sent": st.column_config.TextColumn("Ítems Enviados"),
            },
            hide_index=True
        )
