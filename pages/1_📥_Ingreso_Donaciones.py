import streamlit as st
import database
from datetime import date

st.set_page_config(page_title="Ingreso de Donaciones", page_icon="📥")

st.markdown("# 📥 Registro de Donaciones")
st.write("Registra aquí los ítems que ingresan al centro de acopio.")

with st.form("donation_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        donor_name = st.text_input("Nombre del Donante (Opcional)")
        item_name = st.text_input("Nombre del Ítem / Producto", placeholder="Ej. Arroz, Agua, Ropa...")
        category = st.selectbox("Categoría", [
            "Alimentos No Perecederos",
            "Alimentos Perecederos",
            "Agua / Bebidas",
            "Ropa / Calzado",
            "Aseo Personal",
            "Aseo Hogar",
            "Medicamentos",
            "Otros"
        ])
    
    with col2:
        quantity = st.number_input("Cantidad", min_value=1, value=1)
        unit = st.selectbox("Unidad", ["Unidades", "Kg", "Litros", "Cajas", "Paquetes"])
        expiration_date = st.date_input("Fecha de Vencimiento (Si aplica)", value=None)

    submitted = st.form_submit_button("📥 Registrar Entrada")

    if submitted:
        if not item_name:
            st.error("⚠️ El nombre del ítem es obligatorio.")
        else:
            try:
                # Convert date to string if it exists
                exp_date_str = expiration_date.strftime("%Y-%m-%d") if expiration_date else None
                
                database.add_donation(
                    item_name=item_name,
                    category=category,
                    quantity=quantity,
                    unit=unit,
                    expiration_date=exp_date_str,
                    donor_name=donor_name
                )
                st.success(f"✅ ¡{item_name} registrado exitosamente!")
            except Exception as e:
                st.error(f"❌ Error al registrar: {e}")
