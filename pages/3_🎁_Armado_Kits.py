import streamlit as st
import pandas as pd
import database

st.set_page_config(page_title="Armado de Kits", page_icon="🎁", layout="wide")

st.markdown("# 🎁 Armado de Kits")
st.write("Crea kits de ayuda seleccionando productos del inventario.")

# 1. Get Inventory
df = database.get_inventory()
available_df = df[df['status'] == 'Available']

if available_df.empty:
    st.warning("No hay inventario disponible para armar kits.")
else:
    # Group by item name to show total available
    stock_summary = available_df.groupby('item_name')['quantity'].sum().reset_index()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1. Configurar Receta del Kit")
        kit_name = st.text_input("Nombre del Kit", value="Kit Básico de Alimentos")
        
        # Select items for the kit
        # Using a multiselect to pick items
        all_items = stock_summary['item_name'].unique()
        selected_items = st.multiselect("Seleccionar Productos", all_items)
        
        recipe = []
        if selected_items:
            st.write("Definir cantidades por cada Kit:")
            for item in selected_items:
                # Find max available to show as hint
                max_avail = stock_summary[stock_summary['item_name'] == item]['quantity'].values[0]
                qty = st.number_input(f"Cantidad de **{item}** (Disp: {max_avail})", min_value=1, max_value=int(max_avail), key=f"qty_{item}")
                recipe.append({'item_name': item, 'quantity_needed_per_kit': qty, 'max_available': max_avail})
    
    with col2:
        st.subheader("2. Calcular y Armar")
        if recipe:
            # Calculate max possible kits
            max_kits = float('inf')
            
            st.write("### Resumen de la Receta")
            recipe_df = pd.DataFrame(recipe)
            st.dataframe(recipe_df[['item_name', 'quantity_needed_per_kit']], hide_index=True)
            
            for r in recipe:
                possible = r['max_available'] // r['quantity_needed_per_kit']
                if possible < max_kits:
                    max_kits = possible
            
            st.info(f"⚡ Según el inventario actual, puedes armar un máximo de **{int(max_kits)}** kits.")
            
            qty_to_make = st.number_input("¿Cuántos kits deseas armar?", min_value=1, max_value=int(max_kits) if max_kits > 0 else 1, value=1)
            
            if st.button("🚀 Confirmar y Armar Kits", type="primary", disabled=(max_kits == 0)):
                if max_kits == 0:
                    st.error("No hay suficiente stock para armar ni siquiera 1 kit.")
                else:
                    success, msg = database.assemble_kit(kit_name, recipe, qty_to_make)
                    if success:
                        st.success(f"✅ {msg}")
                        st.balloons()
                        # Clean cache to update inventory view
                        st.cache_data.clear()
                    else:
                        st.error(f"❌ Error: {msg}")

        else:
            st.info("Selecciona productos a la izquierda para comenzar.")
