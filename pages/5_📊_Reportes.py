import streamlit as st
import pandas as pd
import database
import io

st.set_page_config(page_title="Reportes y Datos", page_icon="📊", layout="wide")

st.markdown("# 📊 Reportes y Gestión de Datos")
st.write("Importa inventario masivo o descarga reportes detallados.")

tab1, tab2, tab3 = st.tabs(["📄 Plantillas", "📥 Importar Masivo", "📤 Exportar Datos"])

with tab1:
    st.subheader("📄 Plantillas de Excel")
    st.markdown("""
    Descarga estas plantillas para organizar la información antes de cargarla al sistema.
    **Recuerda no cambiar los nombres de las columnas para evitar errores.**
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 📥 Plantilla de Ingreso (Donaciones)")
        st.write("Úsala para registrar inventario inicial o donaciones masivas.")
        
        # Template Generation: Donations
        donation_data = {
            'item_name': ['Arroz', 'Jabón de Baño', 'Atún', 'Agua 500ml'],
            'category': ['Alimentos No Perecederos', 'Aseo Personal', 'Alimentos No Perecederos', 'Agua / Bebidas'],
            'quantity': [50, 100, 200, 500],
            'unit': ['Kg', 'Unidades', 'Latas', 'Botellas'],
            'expiration_date': ['2025-12-31', '', '2026-06-30', '2025-01-01'],
            'donor_name': ['Donante Anónimo', 'Empresa X', 'Fundación Y', 'Familia Z']
        }
        df_donation_template = pd.DataFrame(donation_data)
        buffer_don = io.BytesIO()
        with pd.ExcelWriter(buffer_don, engine='xlsxwriter') as writer:
            df_donation_template.to_excel(writer, index=False, sheet_name='Donaciones')
            
        st.download_button(
            label="⬇️ Descargar Plantilla de Donaciones",
            data=buffer_don.getvalue(),
            file_name="plantilla_donaciones_upb.xlsx",
            mime="application/vnd.ms-excel",
        )

    with col2:
        st.write("### 🚚 Plantilla de Despachos (Histórico/Inicial)")
        st.write("Úsala si necesitas cargar despachos que ya se hicieron manualmente.")
        
        # Template Generation: Dispatches (Simulated import logic not yet implemented, but template offered)
        dispatch_data = {
            'destination': ['Albergue El Recreo', 'Barrio La Playa'],
            'receiver_name': ['Juan Pérez', 'María Gómez'],
            'item_name': ['Kit Básico', 'Agua 500ml'],
            'quantity': [10, 50],
            'dispatch_date': ['2024-05-20', '2024-05-21']
        }
        df_dispatch_template = pd.DataFrame(dispatch_data)
        buffer_disp = io.BytesIO()
        with pd.ExcelWriter(buffer_disp, engine='xlsxwriter') as writer:
            df_dispatch_template.to_excel(writer, index=False, sheet_name='Despachos')
            
        st.download_button(
            label="⬇️ Descargar Plantilla de Despachos",
            data=buffer_disp.getvalue(),
            file_name="plantilla_despachos_upb.xlsx",
            mime="application/vnd.ms-excel",
            help="Actualmente el sistema solo importa donaciones, pero puedes usar esto para ordenar tus registros manuales."
        )

with tab2:
    st.subheader("Importar Inventario desde Excel")
    st.markdown("""
    **Instrucciones:**
    1. Descarga la **Plantilla de Donaciones** en la pestaña anterior.
    2. Llena los datos.
    3. Sube el archivo aquí.
    """)
    
    uploaded_file = st.file_uploader("Subir Archivo Excel (Donaciones)", type=['xlsx'])
    
    if uploaded_file:
        try:
            df_upload = pd.read_excel(uploaded_file)
            st.write("Vista previa de datos a cargar:")
            st.dataframe(df_upload.head())
            
            if st.button("💾 Procesar y Cargar al Inventario"):
                # Validate columns
                required_cols = ['item_name', 'category', 'quantity', 'unit']
                if not all(col in df_upload.columns for col in required_cols):
                    st.error(f"El archivo debe tener las columnas: {', '.join(required_cols)}")
                else:
                    success_count = 0
                    for index, row in df_upload.iterrows():
                        try:
                            # Handle date formatting if present
                            exp_date = row.get('expiration_date', None)
                            if pd.isna(exp_date) or str(exp_date).lower() == 'nan':
                                exp_date = None
                            else:
                                exp_date = str(exp_date).split(' ')[0] # Keep only YYYY-MM-DD
                                
                            database.add_donation(
                                item_name=row['item_name'],
                                category=row['category'],
                                quantity=row['quantity'],
                                unit=row['unit'],
                                expiration_date=exp_date,
                                donor_name=row.get('donor_name', 'Importado')
                            )
                            success_count += 1
                        except Exception as e:
                            st.warning(f"Error en fila {index}: {e}")
                    
                    st.success(f"✅ Se cargaron exitosamente {success_count} registros.")
                    
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

with tab3:
    st.subheader("Descargar Reportes")
    
    # Inventory Export
    df_inv = database.get_inventory()
    if not df_inv.empty:
        buffer_inv = io.BytesIO()
        with pd.ExcelWriter(buffer_inv, engine='xlsxwriter') as writer:
            df_inv.to_excel(writer, index=False, sheet_name='Inventario')
        
        st.download_button(
            label="📦 Descargar Inventario Completo (Excel)",
            data=buffer_inv.getvalue(),
            file_name="inventario_upb.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.info("El inventario está vacío.")
        
    st.divider()
    
    # Dispatch Export
    conn = database.get_connection()
    df_disp = pd.read_sql_query("SELECT * FROM dispatches", conn)
    conn.close()
    
    if not df_disp.empty:
        buffer_disp = io.BytesIO()
        with pd.ExcelWriter(buffer_disp, engine='xlsxwriter') as writer:
            df_disp.to_excel(writer, index=False, sheet_name='Despachos')
            
        st.download_button(
            label="🚚 Descargar Historial de Despachos (Excel)",
            data=buffer_disp.getvalue(),
            file_name="despachos_upb.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.info("No hay historial de despachos.")
