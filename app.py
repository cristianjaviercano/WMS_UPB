import streamlit as st
import database

# Page Configuration
st.set_page_config(
    page_title="UPB Solidaria - Gestión de Donaciones",
    page_icon="🤝",
    layout="wide"
)

# Initialize Database
database.init_db()

# Main Interface
st.title("🤝 UPB Solidaria - Centro de Acopio")

st.markdown("""
### Bienvenido al sistema de gestión de donaciones.
Este sistema permite gestionar el inventario, armar kits y despachar ayudas humanitarias para la tragedia de Córdoba.

**Navega por el menú lateral para acceder a las diferentes funcionalidades:**
- **📥 Ingreso Donaciones:** Registra nuevos ítems recibidos.
- **📦 Inventario:** Consulta y filtra el stock actual.
- **🎁 Armado de Kits:** Crea kits estandarizados basados en el stock.
- **🚚 Despachos:** Emite órdenes de salida.
""")

# Sidebar Metrics (Placeholder)
st.sidebar.header("Resumen Rápido")
# Here we could add some quick stats like "Total Items", "Kits Ready", etc.
