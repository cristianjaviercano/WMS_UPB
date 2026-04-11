"""
WMS UPB - Warehouse Management System Educational
===================================================
Aplicación educativa para la gestión de almacenes
Universidad Pontificia Boliviana - Ingeniería Industrial

Autor: Ing. Cristian Javier Cano Mogollon
Curso: Gestión de Almacenamiento
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="WMS UPB - Sistema de Gestión de Almacenes",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# BASE DE DATOS - INICIALIZACIÓN
# ============================================================================
DB_FILE = "wms_inventory.db"


def init_database():
    """Inicializa la base de datos SQLite con las tablas necesarias"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Tabla de productos
    c.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            categoria TEXT,
            cantidad INTEGER DEFAULT 0,
            unidad TEXT,
            peso REAL,
            volumen REAL,
            ubicacion TEXT,
            costo_unitario REAL,
            proveedor TEXT,
            fecha_ingreso TEXT,
            estado TEXT DEFAULT 'activo'
        )
    """)

    # Tabla de ubicaciones
    c.execute("""
        CREATE TABLE IF NOT EXISTS ubicaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            zona TEXT,
            pasillo TEXT,
            estante TEXT,
            nivel TEXT,
            capacidad INTEGER,
            estado TEXT DEFAULT 'disponible'
        )
    """)

    # Tabla de movimientos
    c.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            producto_id INTEGER,
            cantidad INTEGER,
            ubicacion_origen TEXT,
            ubicacion_destino TEXT,
            usuario TEXT,
            fecha TEXT,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    # Insertar ubicaciones de ejemplo si no existen
    c.execute("SELECT COUNT(*) FROM ubicaciones")
    if c.fetchone()[0] == 0:
        zonas = ["A", "B", "C"]
        for z in zonas:
            for p in range(1, 4):
                for e in range(1, 6):
                    for n in range(1, 4):
                        codigo = f"{z}-{p:02d}-{e:02d}-{n}"
                        c.execute(
                            "INSERT INTO ubicaciones (codigo, zona, pasillo, estante, nivel, capacidad, estado) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (codigo, z, str(p), str(e), str(n), 100, "disponible"),
                        )

    # Insertar productos de ejemplo
    c.execute("SELECT COUNT(*) FROM productos")
    if c.fetchone()[0] == 0:
        productos_ejemplo = [
            (
                "SKU-001",
                "Portátil HP 15s",
                "Electrónica",
                150,
                "und",
                2.5,
                0.005,
                "A-01-01-02",
                450000,
                "HP Colombia",
                "2025-01-15",
            ),
            (
                "SKU-002",
                "Mouse Inalámbrico",
                "Accesorios",
                500,
                "und",
                0.1,
                0.0001,
                "B-02-03-01",
                25000,
                "Logitech",
                "2025-01-14",
            ),
            (
                "SKU-003",
                "Escritorio Metal",
                "Mobiliario",
                45,
                "und",
                25.0,
                0.5,
                "C-01-01-01",
                280000,
                "Muebles UPB",
                "2025-01-13",
            ),
            (
                "SKU-004",
                "Silla Ergonómica",
                "Mobiliario",
                30,
                "und",
                15.0,
                0.3,
                "C-01-02-02",
                350000,
                "Herman Miller",
                "2025-01-12",
            ),
            (
                "SKU-005",
                'Monitor 24"',
                "Electrónica",
                80,
                "und",
                4.0,
                0.01,
                "A-02-01-01",
                180000,
                "Samsung",
                "2025-01-11",
            ),
            (
                "SKU-006",
                "Teclado Mecánico",
                "Accesorios",
                200,
                "und",
                0.5,
                0.0005,
                "B-01-02-03",
                75000,
                "Logitech",
                "2025-01-10",
            ),
            (
                "SKU-007",
                "Webcam HD",
                "Electrónica",
                120,
                "und",
                0.2,
                0.0002,
                "A-01-03-01",
                95000,
                "Logitech",
                "2025-01-09",
            ),
            (
                "SKU-008",
                "Audífonos USB",
                "Accesorios",
                300,
                "und",
                0.3,
                0.0003,
                "B-03-01-02",
                45000,
                "JBL",
                "2025-01-08",
            ),
            (
                "SKU-009",
                "Cable HDMI 2m",
                "Accesorios",
                1000,
                "und",
                0.1,
                0.0001,
                "B-02-02-01",
                15000,
                "Genérico",
                "2025-01-07",
            ),
            (
                "SKU-010",
                "Disco SSD 500GB",
                "Electrónica",
                75,
                "und",
                0.1,
                0.0002,
                "A-03-01-02",
                120000,
                "Kingston",
                "2025-01-06",
            ),
        ]
        for p in productos_ejemplo:
            c.execute(
                "INSERT INTO productos (sku, nombre, categoria, cantidad, unidad, peso, volumen, ubicacion, costo_unitario, proveedor, fecha_ingreso) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                p,
            )

    conn.commit()
    conn.close()


# Inicializar base de datos
init_database()


# ============================================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================================
def get_connection():
    return sqlite3.connect(DB_FILE)


def get_productos():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM productos", conn)
    conn.close()
    return df


def get_ubicaciones():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM ubicaciones", conn)
    conn.close()
    return df


def get_movimientos():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM movimientos ORDER BY fecha DESC LIMIT 100", conn)
    conn.close()
    return df


def agregar_producto(
    sku, nombre, categoria, cantidad, unidad, peso, volumen, ubicacion, costo, proveedor
):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            """
            INSERT INTO productos (sku, nombre, categoria, cantidad, unidad, peso, volumen, ubicacion, costo_unitario, proveedor, fecha_ingreso)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                sku,
                nombre,
                categoria,
                cantidad,
                unidad,
                peso,
                volumen,
                ubicacion,
                costo,
                proveedor,
                datetime.now().strftime("%Y-%m-%d"),
            ),
        )
        conn.commit()
        return True, "Producto agregado correctamente"
    except sqlite3.IntegrityError:
        return False, "El SKU ya existe"
    finally:
        conn.close()


def actualizar_inventario(producto_id, nueva_cantidad):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, producto_id)
    )
    conn.commit()
    conn.close()


def registrar_movimiento(tipo, producto_id, cantidad, origen, destino):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO movimientos (tipo, producto_id, cantidad, ubicacion_origen, ubicacion_destino, usuario, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            tipo,
            producto_id,
            cantidad,
            origen,
            destino,
            "admin",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


# ============================================================================
# PÁGINA: DASHBOARD PRINCIPAL
# ============================================================================
def show_dashboard():
    st.title("🏭 Dashboard - WMS UPB")
    st.markdown(
        "### Sistema de Gestión de Almacenes - Universidad Pontificia Boliviana"
    )

    # Obtener datos
    productos = get_productos()
    ubicaciones = get_ubicaciones()
    movimientos = get_movimientos()

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total SKUs", len(productos), "productos")
    with col2:
        total_unidades = productos["cantidad"].sum()
        st.metric("Unidades en Stock", f"{total_unidades:,}")
    with col3:
        valor_total = (productos["cantidad"] * productos["costo_unitario"]).sum()
        st.metric("Valor Inventario", f"${valor_total:,.0f}")
    with col4:
        ubicaciones_usadas = len(
            productos[productos["ubicacion"].notna()]["ubicacion"].unique()
        )
        st.metric("Ubicaciones Usadas", ubicaciones_usadas)

    st.divider()

    # Gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Inventario por Categoría")
        if len(productos) > 0:
            fig_categoria = px.pie(
                productos,
                values="cantidad",
                names="categoria",
                title="Distribución de unidades por categoría",
                color_discrete_sequence=px.colors.sequential.Blues_r,
            )
            st.plotly_chart(fig_categoria, use_container_width=True)

    with col2:
        st.subheader("💰 Valor por Categoría")
        if len(productos) > 0:
            productos["valor_total"] = (
                productos["cantidad"] * productos["costo_unitario"]
            )
            valor_cat = (
                productos.groupby("categoria")["valor_total"].sum().reset_index()
            )
            fig_valor = px.bar(
                valor_cat,
                x="categoria",
                y="valor_total",
                title="Valor del inventario por categoría",
                color="categoria",
                color_discrete_sequence=px.colors.sequential.Blues_r,
            )
            st.plotly_chart(fig_valor, use_container_width=True)

    # Tabla de productos con métricas
    st.subheader("📋 Inventario Actual")
    if len(productos) > 0:
        productos["valor_total"] = productos["cantidad"] * productos["costo_unitario"]
        st.dataframe(
            productos[
                [
                    "sku",
                    "nombre",
                    "categoria",
                    "cantidad",
                    "ubicacion",
                    "costo_unitario",
                    "valor_total",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================================
# PÁGINA: GESTIÓN DE PRODUCTOS
# ============================================================================
def show_productos():
    st.title("📦 Gestión de Productos")

    tab1, tab2 = st.tabs(["Inventario", "Agregar Producto"])

    with tab1:
        productos = get_productos()
        st.dataframe(productos, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Agregar Nuevo Producto")
        with st.form("nuevo_producto"):
            col1, col2 = st.columns(2)
            with col1:
                sku = st.text_input("SKU *", placeholder="SKU-XXX")
                nombre = st.text_input("Nombre *", placeholder="Nombre del producto")
                categoria = st.selectbox(
                    "Categoría",
                    ["Electrónica", "Accesorios", "Mobiliario", "Suministros", "Otro"],
                )
                cantidad = st.number_input("Cantidad", min_value=0, value=0)
            with col2:
                unidad = st.selectbox(
                    "Unidad", ["und", "kg", "caja", "pallet", "metro"]
                )
                peso = st.number_input("Peso unitario (kg)", min_value=0.0, value=0.0)
                volumen = st.number_input(
                    "Volumen unitario (m³)", min_value=0.0, value=0.0
                )
                costo = st.number_input("Costo unitario ($)", min_value=0, value=0)

            ubicacion = st.selectbox("Ubicación", get_ubicaciones()["codigo"].tolist())
            proveedor = st.text_input("Proveedor", placeholder="Nombre del proveedor")

            submit = st.form_submit_button("💾 Guardar Producto")

            if submit:
                if sku and nombre:
                    success, msg = agregar_producto(
                        sku,
                        nombre,
                        categoria,
                        cantidad,
                        unidad,
                        peso,
                        volumen,
                        ubicacion,
                        costo,
                        proveedor,
                    )
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("SKU y Nombre son obligatorios")


# ============================================================================
# PÁGINA: GESTIÓN DE UBICACIONES
# ============================================================================
def show_ubicaciones():
    st.title("📍 Gestión de Ubicaciones")

    ubicaciones = get_ubicaciones()
    productos = get_productos()

    # Mapa de ocupaciones
    ubicaciones_ocupadas = (
        productos[productos["ubicacion"].notna()]
        .groupby("ubicacion")
        .size()
        .reset_index()
    )
    ubicaciones_ocupadas.columns = ["codigo", "productos"]

    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Ubicaciones", len(ubicaciones))
    with col2:
        disp = len(ubicaciones[ubicaciones["estado"] == "disponible"])
        st.metric("Disponibles", disp)
    with col3:
        ocup = len(ubicaciones[ubicaciones["estado"] == "ocupada"])
        st.metric("Ocupadas", ocup)

    # Visualización del almacén
    st.subheader("🏭 Visualización del Almacén")

    for zona in ["A", "B", "C"]:
        st.markdown(f"### Zona {zona}")
        zona_data = ubicaciones[ubicaciones["zona"] == zona].sort_values(
            ["pasillo", "estante", "nivel"]
        )

        cols = st.columns(3)
        for idx, row in zona_data.iterrows():
            col_idx = int(row["pasillo"]) % 3
            estado = "🟢" if row["estado"] == "disponible" else "🔴"
            with cols[col_idx]:
                with st.expander(f"{estado} {row['codigo']}"):
                    st.write(f"**Pasillo:** {row['pasillo']}")
                    st.write(f"**Estante:** {row['estante']}")
                    st.write(f"**Nivel:** {row['nivel']}")
                    st.write(f"**Capacidad:** {row['capacidad']} unidades")
                    st.write(f"**Estado:** {row['estado']}")

    st.divider()
    st.subheader("Lista de Ubicaciones")
    st.dataframe(ubicaciones, use_container_width=True, hide_index=True)


# ============================================================================
# PÁGINA: MOVIMIENTOS
# ============================================================================
def show_movimientos():
    st.title("🔄 Movimientos de Inventario")

    movimientos = get_movimientos()
    productos = get_productos()

    if len(movimientos) > 0:
        # Unir con nombres de productos
        movimientos = movimientos.merge(
            productos[["id", "nombre", "sku"]],
            left_on="producto_id",
            right_on="id",
            how="left",
        )

        # Gráfico de movimientos
        st.subheader("📈 Registro de Movimientos")
        st.dataframe(
            movimientos[
                [
                    "fecha",
                    "tipo",
                    "sku",
                    "nombre",
                    "cantidad",
                    "ubicacion_origen",
                    "ubicacion_destino",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No hay movimientos registrados. ¡Registra una recepción o despacho!")


# ============================================================================
# PÁGINA: SIMULADOR DE RECEPCIÓN
# ============================================================================
def show_recepcion():
    st.title("📥 Simulador de Recepción")
    st.markdown("Practica el proceso de recepción de mercancía")

    productos = get_productos()
    ubicaciones = get_ubicaciones()

    with st.form("recepcion_form"):
        st.subheader("Datos del producto a recibir")

        col1, col2 = st.columns(2)
        with col1:
            sku = st.text_input("SKU del producto", placeholder="SKU-XXX")
            cantidad = st.number_input("Cantidad a recibir", min_value=1, value=1)
        with col2:
            proveedor = st.text_input("Proveedor", placeholder="Nombre del proveedor")
            orden_compra = st.text_input("Órden de Compra", placeholder="OC-XXXXX")

        st.subheader("Ubicación en almacén")
        ubicacion = st.selectbox(
            "Seleccionar ubicación", ubicaciones["codigo"].tolist()
        )

        observaciones = st.text_area(
            "Observaciones", placeholder="Estado del producto, daños, etc."
        )

        submit = st.form_submit_button("✅ Confirmar Recepción")

        if submit:
            st.success(
                f"Recepción confirmada: {cantidad} unidades de {sku} recibidas en {ubicacion}"
            )
            st.balloons()


# ============================================================================
# PÁGINA: SIMULADOR DE DESPACHO
# ============================================================================
def show_despacho():
    st.title("🚚 Simulador de Despacho")
    st.markdown("Practica el proceso de despacho de mercancía")

    productos = get_productos()

    # Ver productos disponibles
    st.subheader("Productos Disponibles")
    st.dataframe(
        productos[["sku", "nombre", "cantidad", "ubicacion"]].style.format(
            {"cantidad": "{:d}"}
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    with st.form("despacho_form"):
        st.subheader("Datos del despacho")

        col1, col2 = st.columns(2)
        with col1:
            sku_seleccionar = st.selectbox("Seleccionar SKU", productos["sku"].tolist())
            cantidad_despachar = st.number_input(
                "Cantidad a despachar", min_value=1, value=1
            )
        with col2:
            cliente = st.text_input("Cliente", placeholder="Nombre del cliente")
            numero_pedido = st.text_input("Número de Pedido", placeholder="PED-XXXXX")

        transporte = st.selectbox(
            "Transporte",
            [
                "Camión propio",
                "Transportadora externa",
                "Mensajería",
                "Recoge en tienda",
            ],
        )

        submit = st.form_submit_button("🚚 Confirmar Despacho")

        if submit:
            producto = productos[productos["sku"] == sku_seleccionar].iloc[0]
            if cantidad_despachar <= producto["cantidad"]:
                st.success(
                    f"Despacho confirmado: {cantidad_despachar} unidades de {producto['nombre']} para {cliente}"
                )
                st.balloons()
            else:
                st.error(f"Stock insuficiente. Disponible: {producto['cantidad']}")


# ============================================================================
# PÁGINA: CALCULADORA DE ESPACIOS
# ============================================================================
def show_calculadora_espacios():
    st.title("📐 Calculadora de Espacios")
    st.markdown("Calcula la capacidad necesaria para tu almacén")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Dimensiones del Producto")
        ancho_producto = st.number_input("Ancho (m)", min_value=0.1, value=0.6)
        largo_producto = st.number_input("Largo (m)", min_value=0.1, value=0.8)
        alto_producto = st.number_input("Alto (m)", min_value=0.1, value=1.5)

    with col2:
        st.subheader("Parámetros del Almacén")
        num_sku = st.number_input("Número de SKUs diferentes", min_value=1, value=100)
        stock_promedio = st.number_input(
            "Stock promedio por SKU", min_value=1, value=50
        )
        altura_estanteria = st.number_input(
            "Altura de estanterías (m)", min_value=1.0, value=8.0
        )

    if st.button("Calcular"):
        # Cálculos
        volumen_producto = ancho_producto * largo_producto * alto_producto
        total_unidades = num_sku * stock_promedio
        volumen_total = volumen_producto * total_unidades

        # Asumiendo eficiencia del 40% (60% es pasillo)
        area_util = volumen_total / altura_estanteria
        area_total = area_util / 0.4

        st.divider()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Volumen por unidad", f"{volumen_producto:.3f} m³")
        with col2:
            st.metric("Volumen total necesario", f"{volumen_total:.1f} m³")
        with col3:
            st.metric("Área del almacén", f"{area_total:.1f} m²")

        st.success(
            f"Para almacenar {total_unidades:,} unidades con {num_sku} SKUs diferentes, necesitas aproximadamente {area_total:.1f} m² de área de almacenamiento"
        )


# ============================================================================
# PÁGINA: KPIs LOGÍSTICOS
# ============================================================================
def show_kpis():
    st.title("📊 Indicadores KPIs Logísticos")
    st.markdown("Métricas clave para la gestión de almacenes")

    productos = get_productos()
    movimientos = get_movimientos()
    ubicaciones = get_ubicaciones()

    # Calcular KPIs
    total_sku = len(productos)
    total_unidades = productos["cantidad"].sum()
    valor_inventario = (productos["cantidad"] * productos["costo_unitario"]).sum()

    ubicaciones_ocupadas = len(
        productos[productos["ubicacion"].notna()]["ubicacion"].unique()
    )
    capacidad_usada = (ubicaciones_ocupadas / len(ubicaciones)) * 100

    # KPI Cards
    st.subheader("KPIs Principal")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Exactitud de Inventario", "98.5%", "+0.5%")
    with col2:
        st.metric("Tasa de Pedidos Perfectos", "96.2%", "-1.2%")
    with col3:
        st.metric("OTIF (On Time In Full)", "94.8%", "+2.1%")
    with col4:
        st.metric("Rotación de Inventario", "4.2x", "+0.3x")

    st.divider()

    # Gráfico de KPIs
    st.subheader("📈 Tendencias")

    kpis_data = {
        "Mes": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
        "Accuracy": [96, 97, 97.5, 98, 98.2, 98.5],
        "OTIF": [91, 92, 93, 94, 94.5, 94.8],
        "Pedidos Perfectos": [94, 95, 95.5, 96, 96.1, 96.2],
    }
    df_kpis = pd.DataFrame(kpis_data)

    fig = px.line(
        df_kpis,
        x="Mes",
        y=["Accuracy", "OTIF", "Pedidos Perfectos"],
        title="Evolución de KPIs",
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Definiciones de KPIs
    st.divider()
    st.subheader("📖 Definiciones")

    kpis_def = [
        (
            "Exactitud de Inventario",
            "(Ítems correctos / Total ítems) × 100",
            "Mide la confiabilidad del registro vs la realidad física",
        ),
        (
            "Pedidos Perfectos",
            "(Pedidos sin errores / Total pedidos) × 100",
            "Porcentaje de pedidos entregados sin incidencias",
        ),
        (
            "OTIF",
            "(Órdenes a tiempo y completas / Total) × 100",
            "Nivel de servicio al cliente",
        ),
        (
            "Rotación de Inventario",
            "Costo ventas / Inventario promedio",
            "Veces que se renueva el inventario al año",
        ),
    ]

    for nombre, formula, desc in kpis_def:
        with st.expander(nombre):
            st.write(f"**Fórmula:** {formula}")
            st.write(f"**Descripción:** {desc}")


# ============================================================================
# BARRA LATERAL - NAVEGACIÓN
# ============================================================================
def main():
    # Sidebar
    st.sidebar.title("🏭 WMS UPB")
    st.sidebar.image("https://www.upb.edu.co/images/logo-upb.png", width=150)
    st.sidebar.divider()

    # Menú de navegación
    menu = [
        "📊 Dashboard",
        "📦 Productos",
        "📍 Ubicaciones",
        "🔄 Movimientos",
        "📥 Simulador Recepción",
        "🚚 Simulador Despacho",
        "📐 Calculadora Espacios",
        "📊 KPIs Logísticos",
    ]

    choice = st.sidebar.radio("Navegación", menu)

    # Información del curso
    st.sidebar.divider()
    st.sidebar.info("""
    **Curso:** Gestión de Almacenamiento  
    **Programa:** Ingeniería Industrial UPB  
    **Instructor:** Ing. Cristian Javier Cano Mogollon
    """)

    # Ejecutar la página seleccionada
    if choice == "📊 Dashboard":
        show_dashboard()
    elif choice == "📦 Productos":
        show_productos()
    elif choice == "📍 Ubicaciones":
        show_ubicaciones()
    elif choice == "🔄 Movimientos":
        show_movimientos()
    elif choice == "📥 Simulador Recepción":
        show_recepcion()
    elif choice == "🚚 Simulador Despacho":
        show_despacho()
    elif choice == "📐 Calculadora Espacios":
        show_calculadora_espacios()
    elif choice == "📊 KPIs Logísticos":
        show_kpis()


if __name__ == "__main__":
    main()
