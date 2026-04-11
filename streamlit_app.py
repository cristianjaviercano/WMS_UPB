"""
WMS UPB - Sistema de Gestión de Almacenes Educativo
===================================================
Laboratorio práctico para aprender gestión de almacenes y logística.

Universidad Pontificia Boliviana - Ingeniería Industrial
Profesor: Ing. Cristian Javier Cano Mogollon

Este es un sistema educativo diseñado para:
- Enseñar los conceptos fundamentales de un WMS
- Practicar transacciones logísticas en un ambiente seguro
- Entender los KPIs logísticos y cómo se calculan
- Preparar a los estudiantes para entornos industriales reales
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="WMS UPB - Laboratorio de Gestión de Almacenes",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# CONSTANTES EDUCATIVAS - EXPLICACIONES
# ============================================================================
INFO_WMS = """
## 🏭 ¿Qué es un WMS?

Un **Sistema de Gestión de Almacenes (WMS)** es un software que controla todas las 
operaciones dentro de un almacén. Su objetivo principal es optimizar el almacenamiento y 
la distribución de productos.

### Funciones principales de un WMS:
1. **Recepción** - Controlar el ingreso de mercancía
2. **Almacenamiento** - Asignar ubicaciones óptimas
3. **Inventario** - Mantener registro preciso de las existencias
4. **Preparación de pedidos** - Gestionar Picking y Packing
5. **Despacho** - Controlar salida de productos
6. **Reporting** - Generar métricas y KPIs

### ¿Por qué aprender WMS?

En la industria moderna, la gestión eficiente del almacén puede representar 
ahorros del 15-30% en costos operativos. Las empresas buscan profesionales 
capacitados en estas herramientas.
"""

INFO_RECEPCION = """
## 📥 Transacción: RECEPCIÓN (Inbound)

La **recepcón** es el proceso de aceptar mercancía que ingresa al almacén 
desde proveedores o centros de distribución.

### Flujo de la Recepción:
1. **Llegada del transporte** - El camión/vehículo llega al muelle
2. **Verificación de documentación** - OC, factura, guía de remise
3. **Inspección de cantidad** - Verificar unidades recibidas vs pedido
4. **Inspección de calidad** - Revisar estados de los productos
5. **Registro en sistema** - Ingresar datos al WMS
6. **Ubicación** - Asignar ubicación en el almacén
7. ** almacenaje** - Ubicar físicamente los productos

### Conceptos clave:
- **OC (Orden de Compra)** - Documento autorizado para compra
- **Remise** - Guía del transportador
- **Cantidad pedida vs recibida** - Puede haber diferencias
- **Unidad de manejo** - Cómo se manipula (caja, pallet, unidad)
"""

INFO_INVENTARIO = """
## 📦 Gestión de INVENTARIO

El **inventario** es el conjunto de todos los productos almacenados. 
Un buen control de inventario es la base de un WMS eficiente.

### Tipos de inventario:
1. **Inventario físico** - Lo que realmente existe en el almacén
2. **Inventario en sistema** - Lo registrado en el WMS
3. **Inventario disponible** - Lo que se puede usar para pedidos
4. **Inventario comprometido** - Lo reservado para pedidos
5. **Inventario en tránsito** - Entre ubicaciones

### Conceptos importantes:
- **SKU (Stock Keeping Unit)** - Código único por producto
- **Cantidad en mano** - Lo que realmente hay
- **Cantidad disponible** - Lo que se puede despachar
- **Punto de reorden** - Nivel que activa nueva compra
"""

INFO_DESPACHO = """
## 🚚 Transacción: DESPACHO (Outbound)

El **despacho** es el proceso de atender pedidos de clientes, 
ya sea minoristas, mayoristas o consumidores finales.

### Flujo del Despacho:
1. **Recepción del pedido** - Orden del cliente
2. **Verificación de disponibilidad** - Confirmar stock
3. **Reserva** - Separar productos del pedido
4. **Picking** - Recoger productos de ubicaciones
5. **Packing** - Empaquetar para transporte
6. **Documentación** - Generar guía de despacho
7. **Carga** - Subir al vehículo de reparto
8. **Entrega** - Delivery al cliente

### Términos clave:
- **Picking** - Recoger productos de estanterías
- **Packing** - Empaquetar el pedido
- **Orden de picking** - Lista de productos a recoger
- **Cliente** - Puede ser interno o externo
"""

INFO_KPIS = """
## 📊 Indicadores KPIs Logísticos

Los **KPIs (Key Performance Indicators)** son métricas que permiten 
medir la eficiencia y efectividad de las operaciones del almacén.

### KPIs principales en un WMS:

| KPI | Fórmula | Meta típica |
|-----|---------|-------------|
| **Exactitud de Inventario** | (Registros OK / Total) × 100 | > 98% |
| **Pedidos Perfectos** | (Sin errores / Total pedidos) × 100 | > 95% |
| **OTIF** |%A tiempo y completos / Total) × 100 | > 95% |
| **Rotación de Inventario** | Ventas / Inv. promedio | 4-12x/año |
| **Costo por unidad almacenada** | Costo total / Unidades | Minimizar |
| **Tiempo de ciclo de pedido** | Recepción → Envío | < 4 horas |

### ¿Por qué son importantes?
Los KPIs permiten:
- Identificar problemas antes de que sean críticos
- Medir el desempeño del personal
- Justificar inversiones en mejoras
- Compararse con estándares de la industria
"""

# ============================================================================
# BASE DE DATOS - INICIALIZACIÓN
# ============================================================================
DB_FILE = "wms_inventory.db"


def init_database():
    """Inicializa la base de datos SQLite con datos de ejemplo para práctica"""
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

    # Tabla de ubicaciones (sistema de coordenadas)
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

    # Tabla de movimientos (histórico)
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
            observaciones TEXT,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    # Insertar ubicaciones de ejemplo (Almacén pequeño)
    c.execute("SELECT COUNT(*) FROM ubicaciones")
    if c.fetchone()[0] == 0:
        zonas = ["A", "B", "C"]  # Zonas del almacén
        for z in zonas:
            for p in range(1, 4):  # 3 pasillos por zona
                for e in range(1, 6):  # 5 estantes por pasillo
                    for n in range(1, 4):  # 3 niveles por estante
                        codigo = f"{z}-{p:02d}-{e:02d}-{n}"
                        c.execute(
                            "INSERT INTO ubicaciones (codigo, zona, pasillo, estante, nivel, capacidad, estado) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (codigo, z, str(p), str(e), str(n), 100, "disponible"),
                        )

    # Insertar productos de ejemplo
    c.execute("SELECT COUNT(*) FROM productos")
    if c.fetchone()[0] == 0:
        productos_ejemplo = [
            ("SKU-001", "Portátil HP 15s", "Electrónica", 150, "und", 2.5, 0.005, "A-01-01-02", 450000, "HP Colombia", "2025-01-15"),
            ("SKU-002", "Mouse Inalámbrico", "Accesorios", 500, "und", 0.1, 0.0001, "B-02-03-01", 25000, "Logitech", "2025-01-14"),
            ("SKU-003", "Escritorio Metal", "Mobiliario", 45, "und", 25.0, 0.5, "C-01-01-01", 280000, "Muebles UPB", "2025-01-13"),
            ("SKU-004", "Silla Ergonómica", "Mobiliario", 30, "und", 15.0, 0.3, "C-01-02-02", 350000, "Herman Miller", "2025-01-12"),
            ('SKU-005', 'Monitor 24"', "Electrónica", 80, "und", 4.0, 0.01, "A-02-01-01", 180000, "Samsung", "2025-01-11"),
            ("SKU-006", "Teclado Mecánico", "Accesorios", 200, "und", 0.5, 0.0005, "B-01-02-03", 75000, "Logitech", "2025-01-10"),
            ("SKU-007", "Webcam HD", "Electrónica", 120, "und", 0.2, 0.0002, "A-01-03-01", 95000, "Logitech", "2025-01-09"),
            ("SKU-008", "Audífonos USB", "Accesorios", 300, "und", 0.3, 0.0003, "B-03-01-02", 45000, "JBL", "2025-01-08"),
            ("SKU-009", "Cable HDMI 2m", "Accesorios", 1000, "und", 0.1, 0.0001, "B-02-02-01", 15000, "Genérico", "2025-01-07"),
            ("SKU-010", "Disco SSD 500GB", "Electrónica", 75, "und", 0.1, 0.0002, "A-03-01-02", 120000, "Kingston", "2025-01-06"),
        ]
        for p in productos_ejemplo:
            c.execute(
                "INSERT INTO productos (sku, nombre, categoria, cantidad, unidad, peso, volumen, ubicacion, costo_unitario, proveedor, fecha_ingreso) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                p,
            )

        # Agregar movimientos de ejemplo
        c.execute("SELECT id FROM productos LIMIT 5")
        producto_ids = [row[0] for row in c.fetchall()]
        for i, pid in enumerate(producto_ids[:5]):
            c.execute(
                "INSERT INTO movimientos (tipo, producto_id, cantidad, ubicacion_origen, ubicacion_destino, usuario, fecha, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ("entrada", pid, 50, None, "A-01-01-01", "admin", "2025-01-10 08:00", "Recepción inicial"),
            )

    conn.commit()
    conn.close()


# Inicializar base de datos al iniciar
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


def get_movimientos(limit=100):
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM movimientos ORDER BY fecha DESC LIMIT {limit}", conn)
    conn.close()
    return df


def get_ubicaciones_disponibles():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM ubicaciones WHERE estado = 'disponible'", conn)
    conn.close()
    return df


def agregar_producto(sku, nombre, categoria, cantidad, unidad, peso, volumen, ubicacion, costo, proveedor):
    """Agrega un nuevo producto al inventario"""
    conn = get_connection()
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    try:
        c.execute(
            """INSERT INTO productos (sku, nombre, categoria, cantidad, unidad, peso, volumen, ubicacion, costo_unitario, proveedor, fecha_ingreso) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (sku, nombre, categoria, cantidad, unidad, peso, volumen, ubicacion, costo, proveedor, fecha_actual),
        )
        conn.commit()
        return True, "Producto agregado correctamente"
    except sqlite3.IntegrityError:
        return False, "El SKU ya existe. Use otro código."
    finally:
        conn.close()


def registrar_recepcion(sku, cantidad, proveedor, orden_compra, ubicacion, observaciones):
    """Procesa una recepción de mercancía"""
    conn = get_connection()
    c = conn.cursor()
    try:
        # Buscar producto
        c.execute("SELECT id, cantidad, ubicacion FROM productos WHERE sku = ?", (sku,))
        result = c.fetchone()
        
        if result:
            producto_id, cantidad_actual, ubicacion_actual = result
            nueva_cantidad = cantidad_actual + cantidad
            # Actualizar cantidad
            c.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, producto_id))
        else:
            return False, f"Producto {sku} no encontrado. Debe existir en inventario primero."

        # Registrar movimiento
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            "INSERT INTO movimientos (tipo, producto_id, cantidad, ubicacion_origen, ubicacion_destino, usuario, fecha, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("entrada", producto_id, cantidad, "Recepción", ubicacion, "admin", fecha_actual, f"OC: {orden_compra} - {observaciones}"),
        )

        # Actualizar estado de ubicación si aplica
        if ubicacion:
            c.execute("UPDATE ubicaciones SET estado = 'ocupada' WHERE codigo = ?", (ubicacion,))

        conn.commit()
        return True, f"Recepción registrada: {cantidad} unidades de {sku}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def registrar_despacho(sku, cantidad, cliente, numero_pedido, observaciones):
    """Procesa un despacho de mercancía"""
    conn = get_connection()
    c = conn.cursor()
    try:
        # Buscar producto
        c.execute("SELECT id, cantidad, ubicacion FROM productos WHERE sku = ?", (sku,))
        result = c.fetchone()

        if not result:
            return False, f"Producto {sku} no encontrado"

        producto_id, cantidad_actual, ubicacion = result

        if cantidad_actual < cantidad:
            return False, f"Stock insuficiente. Disponible: {cantidad_actual}, Solicitado: {cantidad}"

        nueva_cantidad = cantidad_actual - cantidad
        c.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, producto_id))

        # Registrar movimiento
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            " INSERT INTO movimientos (tipo, producto_id, cantidad, ubicacion_origen, ubicacion_destino, usuario, fecha, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("salida", producto_id, cantidad, ubicacion, "Despacho", "admin", fecha_actual, f"Pedido: {numero_pedido} - Cliente: {cliente} - {observaciones}"),
        )

        # Si stock llegó a 0, liberar ubicación
        if nueva_cantidad == 0:
            c.execute("UPDATE ubicaciones SET estado = 'disponible' WHERE codigo = ?", (ubicacion,))

        conn.commit()
        return True, f"Despacho registrado: {cantidad} unidades de {sku} para {cliente}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def calcular_espacios(ancho, largo, alto, num_sku, stock_promedio, altura_estanteria):
    """Calcula espacio necesario para almacenar productos"""
    volumen_producto = ancho * largo * alto
    total_unidades = num_sku * stock_promedio
    volumen_total = volumen_producto * total_unidades
    area_util = volumen_total / altura_estanteria if altura_estanteria > 0 else 0
    area_total = area_util / 0.4 if area_util > 0 else 0  # 40% eficiencia
    return {
        "volumen_unitario": volumen_producto,
        "volumen_total": volumen_total,
        "area_util": area_util,
        "area_total": area_total,
        "total_unidades": total_unidades
    }


# ============================================================================
# PÁGINA: HOME - INTRODUCCIÓN EDUCATIVA
# ============================================================================
def show_home():
    st.title("🏭 WMS UPB - Laboratorio de Gestión de Almacenes")
    st.markdown("### Universidad Pontificia Boliviana - Ingeniería Industrial")
    st.markdown("---")

    # Bienvenida
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ## Bienvenido al Laboratorio WMS

        Este sistema es una herramienta educativa diseñada para que Aprendas los conceptos 
        fundamentales de la gestión de almacenes a través de la práctica.

        ### ¿Qué puedes hacer aquí?

        1. 📊 **Dashboard** - Ver métricas en tiempo real del almacén
        2. 📦 **Inventario** - Gestionar productos y existencias
        3. 📍 **Ubicaciones** - Visualizar el mapa del almacén
        4. 🔄 **Movimientos** - Ver histórico de operaciones
        5. 📥 **Recepción** - Simular ingresos de mercancía
        6. 🚚 **Despacho** - Simular salidas de mercancía
        7. 📐 **Calculadora** - Proyectar capacidad de almacenamiento
        8. 📊 **KPIs** - Aprender métricas logísticas
        """)
        
        st.info("💡 **Consejo:** Usa la barra lateral para navegar entre los módulos. "
                "Cada módulo incluye explicaciones teóricas.")
    
    with col2:
        st.markdown("### Estado del Sistema")
        productos = get_productos()
        ubicaciones = get_ubicaciones()
        movimientos = get_movimientos(10)
        
        st.metric("Productos (SKUs)", len(productos))
        st.metric("Unidades Totales", productos["cantidad"].sum())
        st.metric("Ubicaciones", len(ubicaciones))
        st.metric("Movimientos", len(movimientos))

    st.markdown("---")
    
    # Información educativa
    with st.expander("📚 ¿Qué es un WMS? (Click para expandir)"):
        st.markdown(INFO_WMS)

    with st.expander("📖 Glosario de Términos Logísticos"):
        st.markdown("""
        | Término | Definición |
        |--------|----------|
        | **SKU** | Código único que identifica cada producto |
        | **Picking** | Acto de seleccionar productos para un pedido |
        | **Packing** | Proceso de empacar productos para envío |
        | **Stock** | Cantidad de productos en almacén |
        | **Inventario** | Lista detallada de productos |
        | **Ubicación** | Espacio específico de almacenamiento |
        | **Rotación** | Veces que se renueva el inventario |
        | **OTIF** | On Time In Full - Entregado a tiempo y completo |
        """)


# ============================================================================
# PÁGINA: DASHBOARD
# ============================================================================
def show_dashboard():
    st.title("📊 Dashboard - Vista General del Almacén")
    st.markdown("Métricas en tiempo real del sistema.")

    # Obtener datos
    productos = get_productos()
    ubicaciones = get_ubicaciones()
    movimientos = get_movimientos(50)

    # === MÉTRICAS PRINCIPALES ===
    st.subheader("📈 Indicadores Actuales")
    col1, col2, col3, col4 = st.columns(4)

    total_unidades = productos["cantidad"].sum()
    valor_total = (productos["cantidad"] * productos["costo_unitario"]).sum()
    ubicaciones_ocupadas = len(productos[productos["ubicacion"].notna()]["ubicacion"].unique())

    with col1:
        st.metric("Total SKUs", len(productos), help="Cantidad de productos diferentes")
    with col2:
        st.metric("Unidades en Stock", f"{total_unidades:,}", help="Total de unidades almacenadas")
    with col3:
        st.metric("Valor del Inventario", f"${valor_total:,.0f}", help="Costo total del inventario")
    with col4:
        st.metric("Ubicaciones Usadas", ubicaciones_ocupadas, help="Espacios ocupados")

    st.divider()

    # === GRÁFICOS ===
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Distribución por Categoría")
        if len(productos) > 0:
            fig_cat = px.pie(
                productos, 
                values="cantidad", 
                names="categoria",
                title="Unidades por categoría",
                color_discrete_sequence=px.colors.sequential.Blues_r,
            )
            st.plotly_chart(fig_cat, use_container_width=True)
            
            # Explicación educativa
            with st.expander("💡 ¿Qué nos dice este gráfico?"):
                st.markdown("""
                Este gráfico muestra la **proporción del inventario** por cada categoría.
                Unbalance puede indicar:
                - Exceso de cierta categoría
                - Falta de diversidad
                - Demanda desigual
                """)

    with col2:
        st.subheader("💰 Valor por Categoría")
        if len(productos) > 0:
            productos["valor_total"] = productos["cantidad"] * productos["costo_unitario"]
            valor_cat = productos.groupby("categoria")["valor_total"].sum().reset_index()
            fig_valor = px.bar(
                valor_cat,
                x="categoria",
                y="valor_total",
                title="Valor monetario por categoría",
                color="categoria",
                color_discrete_sequence=px.colors.sequential.Blues_r,
            )
            st.plotly_chart(fig_valor, use_container_width=True)
            
            with st.expander("💡 ¿Para qué sirve?"):
                st.markdown("""
                El valor por categoría ayuda a:
                - Identificar productos de alto valor
                - Planificar seguridad
                - Priorizar espacios
                """)

    st.divider()

    # === TABLA DE INVENTARIO ===
    st.subheader("📋 Inventario Actual")
    if len(productos) > 0:
        productos["valor_total"] = productos["cantidad"] * productos["costo_unitario"]
        st.dataframe(
            productos[["sku", "nombre", "categoria", "cantidad", "ubicacion", "costo_unitario", "valor_total"]],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================================
# PÁGINA: GESTIÓN DE PRODUCTOS
# ============================================================================
def show_productos():
    st.title("📦 Gestión de Productos")
    st.markdown("Administra el catálogo de productos del almacén.")

    tab1, tab2 = st.tabs(["📋 Ver Inventario", "➕ Agregar Producto"])

    with tab1:
        productos = get_productos()
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            cat_filter = st.selectbox("Filtrar por categoría", ["Todas"] + list(productos["categoria"].unique()))
        with col2:
            busqueda = st.text_input("Buscar por SKU o nombre", "")

        # Aplicar filtros
        df_filtered = productos.copy()
        if cat_filter != "Todas":
            df_filtered = df_filtered[df_filtered["categoria"] == cat_filter
        if busqueda:
            df_filtered = df_filtered[
                df_filtered["sku"].str.contains(busqueda, case=False) | 
                df_filtered["nombre"].str.contains(busqueda, case=False)
            ]

        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        
        st.info(f"Mostrando {len(df_filtered)} de {len(productos)} productos")

    with tab2:
        st.markdown("### Nuevo Producto")
        st.markdown("Agrega un producto al catálogo.")
        
        with st.form("nuevo_producto"):
            col1, col2 = st.columns(2)
            with col1:
                sku = st.text_input("SKU *", placeholder="SKU-001")
                nombre = st.text_input("Nombre *", placeholder="Nombre del producto")
                categoria = st.selectbox("Categoría", ["Electrónica", "Accesorios", "Mobiliario", "Suministros", "Otro"])
                cantidad = st.number_input("Cantidad inicial", min_value=0, value=0)
            with col2:
                unidad = st.selectbox("Unidad", ["und", "kg", "caja", "pallet", "metro"])
                peso = st.number_input("Peso unitario (kg)", min_value=0.0, value=0.0)
                volumen = st.number_input("Volumen (m³)", min_value=0.0, value=0.0)
                costo = st.number_input("Costo unitario ($)", min_value=0, value=0)

            ubicacion = st.selectbox("Ubicación inicial", ["Sin asignar"] + get_ubicaciones()["codigo"].tolist())
            proveedor = st.text_input("Proveedor", placeholder="Nombre del proveedor")

            submit = st.form_submit_button("💾 Guardar Producto")

            if submit:
                if sku and nombre:
                    ubicacion_final = None if ubicacion == "Sin asignar" else ubicacion
                    success, msg = agregar_producto(sku, nombre, categoria, cantidad, unidad, peso, volumen, ubicacion_final, costo, proveedor)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)


# ============================================================================
# PÁGINA: UBICACIONES
# ============================================================================
def show_ubicaciones():
    st.title("📍 Mapa del Almacén")
    st.markdown("Visualiza las ubicaciones disponibles en el almacén.")

    ubicaciones = get_ubicaciones()
    productos = get_productos()

    # Crear mapping de ocupaciones
    ocupaciones = productos[productos["ubicacion"].notna()][["ubicacion", "nombre", "cantidad"]].groupby("ubicacion").agg({"nombre": "first", "cantidad": "sum"}).reset_index()

    # === MÉTRICAS ===
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Ubicaciones", len(ubicaciones))
    with col2:
        disp = len(ubicaciones[ubicaciones["estado"] == "disponible"])
        st.metric("Disponibles", disp)
    with col3:
        ocup = len(ubicaciones[ubicaciones["estado"] == "ocupada"])
        st.metric("Ocupadas", ocup)
    with col4:
        ocup_pct = (ocup / len(ubicaciones) * 100) if len(ubicaciones) > 0 else 0
        st.metric("% Ocupación", f"{ocup_pct:.1f}%")

    st.divider()

    # === EXPLICACIÓN ===
    with st.expander("💡 ¿Cómo se lee el código de ubicación?"):
        st.markdown("""
        El código **A-01-02-03** significa:
        - **A**: Zona del almacén (A, B, o C)
        - **01**: Pasillo número 1
        - **02**: Estante número 2  
        - **03**: Nivel número 3 (desde abajo hacia arriba)
        
        Este sistema permiteLocalizar cualquier producto rápidamente.
        """)

    # === VISUALIZACIÓN POR ZONA ===
    st.subheader("🏭 Distribución del Almacén")

    for zona in ["A", "B", "C"]:
        zona_data = ubicaciones[ubicaciones["zona"] == zona].sort_values(["pasillo", "estante", "nivel"])
        
        st.markdown(f"### Zona {zona}")
        
        cols = st.columns(4)
        for idx, row in zona_data.iterrows():
            col_idx = (int(row["pasillo"]) - 1) % 4
            
            # Info del producto si está ocupada
            prod_info = ocupaciones[ocupaciones["ubicacion"] == row["codigo"]]
            if len(prod_info) > 0:
                estado_icon = "🔴"
                estado = f"Ocupado: {prod_info['nombre'].values[0]} ({prod_info['cantidad'].values[0]} und)"
            else:
                estado_icon = "🟢"
                estado = "Disponible"
            
            with cols[col_idx]:
                color = "red" if "Ocupado" in estado else "green"
                st.markdown(f"""
                <div style="padding: 5px; border: 1px solid {color}; border-radius: 5px; text-align: center; margin: 2px;">
                    <b>{estado_icon} {row['codigo']}</b><br>
                    <small>{estado}</small>
                </div>
                """, unsafe_allow_html=True)

    st.divider()
    
    # === LISTA COMPLETA ===
    st.subheader("📋 Lista de Ubicaciones")
    st.dataframe(ubicaciones, use_container_width=True, hide_index=True)


# ============================================================================
# PÁGINA: MOVIMIENTOS
# ============================================================================
def show_movimientos():
    st.title("🔄 Historial de Movimientos")
    st.markdown("Registro histórico de todas las operaciones del almacén.")

    movimientos = get_movimientos(200)
    productos = get_productos()

    if len(movimientos) == 0:
        st.info("No hay movimientos registrados. ¡Intenta hacer una recepción o despacho!")
        return

    # Unir con nombres de productos
    movimientos = movimientos.merge(productos[["id", "nombre", "sku"]], left_on="producto_id", right_on="id", how="left")

    # === ESTADÍSTICAS ===
    col1, col2 = st.columns(2)
    entradas = len(movimientos[movimientos["tipo"] == "entrada"])
    salidas = len(movimientos[movimientos["tipo"] == "salida"])
    with col1:
        st.metric("Total Entradas", entradas, "📥")
    with col2:
        st.metric("Total Salidas", salidas, "📤")

    st.divider()

    # === GRÁFICO ===
    st.subheader("📈 Movimientos por Tipo")
    if len(movimientos) > 0:
        # Agrupar por fecha
        movimientos["fecha_date"] = pd.to_datetime(movimientos["fecha"]).dt.date
        bewegung_by_date = movimientos.groupby(["fecha_date", "tipo"]).size().reset_index(name="cantidad")
        
        fig = px.bar(bewegung_by_date, x="fecha_date", y="cantidad", color="tipo", 
                    title="Movimientos por día", 
                    color_discrete_map={"entrada": "green", "salida": "red"})
        st.plotly_chart(fig, use_container_width=True)

    # === TABLA ===
    st.subheader("📋 Últimos Movimientos")
    st.dataframe(
        movimientos[["fecha", "tipo", "sku", "nombre", "cantidad", "ubicacion_destino", "observaciones"]].head(50),
        use_container_width=True,
        hide_index=True,
    )

    # === EXPLICACIÓN EDUCATIVA ===
    with st.expander("💡 ¿Por qué es importante el registro de movimientos?"):
        st.markdown("""
        El **historial de movimientos** permite:
        - **Auditoría** - Rastrear cualquier producto
        - **Detección de anomalías** - Identificar pérdidas
        - **Análisis de tendencia** - Entender patrones de demanda
        - **Planeación** - Pronosticar necesidades
        """)


# ============================================================================
# PÁGINA: SIMULADOR DE RECEPCIÓN (INTERACTIVO)
# ============================================================================
def show_recepcion():
    st.title("📥 Simulador de Recepción")
    st.markdown("Práctica el proceso de recibir mercancía en el almacén.")
    
    # === EXPLICACIÓN TEÓRICA ===
    with st.expander("📖 Aprender: Proceso de Recepción"):
        st.markdown(INFO_RECEPCION)

    productos = get_productos()
    ubicaciones = get_ubicaciones_disponibles()

    st.divider()

    # === FORMULARIO ===
    st.subheader("📝 Registrar Recepción")
    
    with st.form("recepcion_form"):
        col1, col2 = st.columns(2)
        with col1:
            sku = st.selectbox("Seleccionar SKU", productos["sku"].tolist(), 
                            format_func=lambda x: f"{x} - {productos[productos['sku']==x]['nombre'].values[0]}")
            cantidad = st.number_input("Cantidad a recibir", min_value=1, value=10)
            proveedor = st.text_input("Proveedor", placeholder="Nombre del proveedor")
        with col2:
            orden_compra = st.text_input("Orden de Compra (OC)", placeholder="OC-2024-0001")
            ubicacion = st.selectbox("Ubicación en almacén", ["Seleccionar"] + ubicaciones["codigo"].tolist())
            observaciones = st.text_area("Observaciones", placeholder="Estado, daños, comentarios...")

        submit = st.form_submit_button("✅ Confirmar Recepción")

        if submit:
            if sku and cantidad > 0 and ubicacion != "Seleccionar":
                success, msg = registrar_recepcion(sku, cantidad, proveedor, orden_compra, ubicacion, observaciones)
                if success:
                    st.success(msg)
                    st.balloons()
                    
                    # Mostrar flujo completado
                    st.markdown("### ✅ Proceso Completado")
                    st.markdown(f"""
                    1. ✅ Verificación de documentación (OC: {orden_compra})
                    2. ✅ Inspección de cantidad ({cantidad} unidades)
                    3. ✅ Registro en sistema
                    4. ✅ Ubicación asignada ({ubicacion})
                    5. ✅ Producto dado de alta en inventario
                    """)
                else:
                    st.error(msg)
            else:
                st.warning("Complete todos los campos requeridos")

    # === PRODUCTOS DISPONIBLES ===
    st.divider()
    st.subheader("📦 Productos en Inventario")
    st.dataframe(productos[["sku", "nombre", "cantidad", "ubicacion"]], use_container_width=True, hide_index=True)


# ============================================================================
# PÁGINA: SIMULADOR DE DESPACHO (INTERACTIVO)
# ============================================================================
def show_despacho():
    st.title("🚚 Simulador de Despacho")
    st.markdown("Práctica el proceso de atender pedidos de clientes.")
    
    # === EXPLICACIÓN TEÓRICA ===
    with st.expander("📖 Aprender: Proceso de Despacho"):
        st.markdown(INFO_DESPACHO)

    productos = get_productos()

    st.divider()

    # === VERIFICAR DISPONIBILIDAD ===
    st.subheader("📦 Productos Disponibles")
    
    disponibles = productos[productos["cantidad"] > 0][["sku", "nombre", "cantidad", "ubicacion"]]
    
    if len(disponibles) == 0:
        st.warning("No hay productos disponibles para despachar.")
    else:
        st.dataframe(disponibles, use_container_width=True, hide_index=True)

    st.divider()

    # === FORMULARIO ===
    st.subheader("🚚 Registrar Despacho")
    
    with st.form("despacho_form"):
        col1, col2 = st.columns(2)
        with col1:
            sku = st.selectbox("Seleccionar SKU", productos[productos["cantidad"] > 0]["sku"].tolist(),
                            format_func=lambda x: f"{x} - {productos[productos['sku']==x]['nombre'].values[0]}")
            
            # Mostrar disponibilidad
            cant_disp = productos[productos["sku"] == sku]["cantidad"].values[0]
            st.caption(f"Disponible: {cant_disp} unidades")
            
            cantidad = st.number_input("Cantidad a despachar", min_value=1, max_value=cant_disp, value=min(1, cant_disp))
        with col2:
            cliente = st.text_input("Cliente", placeholder="Nombre del cliente")
            numero_pedido = st.text_input("Número de Pedido", placeholder="PED-2024-0001")
            observaciones = st.text_area("Instrucciones especiales", placeholder="Notas de entrega...")

        submit = st.form_submit_button("🚚 Confirmar Despacho")

        if submit and cantidad > 0 and sku:
            success, msg = registrar_despacho(sku, cantidad, cliente, numero_pedido, observaciones)
            if success:
                st.success(msg)
                st.balloons()
                
                # Mostrar flujo
                st.markdown("### ✅ Proceso Completado")
                st.markdown(f"""
                1. ✅ Verificación de disponibilidad ({cantidad} unidades)
                2. ✅ Reserva de inventario
                3. ✅ Picking realizado
                4. ✅ Empaquetado (Packing)
                5. ✅ Documentación generada (Pedido: {numero_pedido})
                6. ✅ Entrega a: {cliente}
                """)
            else:
                st.error(msg)


# ============================================================================
# PÁGINA: CALCULADORA DE ESPACIOS
# ============================================================================
def show_calculadora_espacios():
    st.title("📐 Calculadora de Espacios")
    st.markdown("Calcula la capacidad necesaria para tu almacén.")
    
    # === EXPLICACIÓN ===
    with st.expander("📖 Aprender: Cálculo de Espacios"):
        st.markdown("""
        ## Cálculo de Espacio en Almacén

        Para calcular el espacio necesario se consideran:
        
        1. **Volumen del producto** = largo × ancho × alto
        2. **Stock total** = SKUs × stock promedio por SKU
        3. **Volumen total** = Volumen producto × Stock total
        4. **Área útil** = Volumen total / Altura de estanterías
        5. **Área total** = Área útil / 0.4 (60% son pasillos)
        
        La **eficiencia de almacenamiento** típica es 40-60%.
        """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Dimensiones del Producto")
        st.markdown("_Ingresa las medidas de una unidad del producto_")
        ancho = st.number_input("Ancho (m)", min_value=0.1, value=0.6, help="Ancho de una caja/unidad")
        largo = st.number_input("Largo (m)", min_value=0.1, value=0.8, help="Largo de una caja/unidad")
        alto = st.number_input("Alto (m)", min_value=0.1, value=1.5, help="Alto de una caja/unidad")

    with col2:
        st.subheader("🏭 Parámetros del Almacén")
        st.markdown("_Ingresa las características del almacén_")
        num_sku = st.number_input("SKUs diferentes", min_value=1, value=100, help="Cuántos productos diferentes")
        stock_promedio = st.number_input("Stock promedio por SKU", min_value=1, value=50, help="Unidades de cada SKU")
        altura_estanteria = st.number_input("Altura de estanterías (m)", min_value=1.0, value=8.0, help="Altura máxima de almacenamiento")

    calcular = st.button("🔢 Calcular Espacio Necesario")

    if calcular:
        resultados = calcular_espacios(ancho, largo, alto, num_sku, stock_promedio, altura_estanteria)
        
        st.divider()
        st.subheader("📊 Resultados")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Volumen por unidad", f"{resultados['volumen_unitario']:.3f} m³")
        with col2:
            st.metric("Volumen total productos", f"{resultados['volumen_total']:.1f} m³")
        with col3:
            st.metric("Total unidades", f"{resultados['total_unidades']:,}")

        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Área útil necesaria", f"{resultados['area_util']:.1f} m²", help="Solo espacio de almacenamiento")
        with col2:
            st.metric("Área total del almacén", f"{resultados['area_total']:.1f} m²", help="Incluye pasillos y muebles")

        st.success(
            f"Para almacenar {resultados['total_unidades']:,} unidades de {num_sku} SKUs diferentes, "
            f"necesitas aproximadamente **{resultados['area_total']:.0f} m²** de área de almacén "
            f"(considerando 60% para pasillos y zonas de trabajo)."
        )
        
        # Recomendación
        st.info("💡 **Recomendación:** Agrega un 20% adicional para áreas de recepción, despacho y oficinas.")


# ============================================================================
# PÁGINA: KPIs LOGÍSTICOS (EDUCATIVA)
# ============================================================================
def show_kpis():
    st.title("📊 Indicadores KPIs Logísticos")
    st.markdown("Aprende los métricas principales de la gestión de almacenes.")
    
    # === EXPLICACIÓN TEÓRICA ===
    with st.expander("📖 Aprender: ¿Qué son los KPIs?"):
        st.markdown(INFO_KPIS)

    productos = get_productos()
    movimientos = get_movimientos(100)
    ubicaciones = get_ubicaciones()

    # === CÁLCULOS ===
    total_sku = len(productos)
    total_unidades = productos["cantidad"].sum()
    valor_inventario = (productos["cantidad"] * productos["costo_unitario"]).sum()
    
    ocup_count = len(productos[productos["ubicacion"].notna()]["ubicacion"].unique())
    capacidad_pct = (ocup_count / len(ubicaciones)) * 100 if len(ubicaciones) > 0 else 0

    # === KPIs PRINCIPALES ===
    st.subheader("📈 KPIs Principales del Almacén")

    col1, col2, col3, col4 = st.columns(4)
    
    # Simular valores (en un sistema real vendrían de datos históricos)
    accuracy = 98.5
    pedidos_perfectos = 96.2
    otif = 94.8
    rotacion = 4.2

    with col1:
        st.metric("Exactitud de Inventario", f"{accuracy}%", "+0.5%",
                help="(Registros OK / Total) × 100. Meta: > 98%")
    with col2:
        st.metric("Pedidos Perfectos", f"{pedidos_perfectos}%", "-1.2%",
                help="Pedidos sin errores. Meta: > 95%")
    with col3:
        st.metric("OTIF", f"{otif}%", "+2.1%",
                help="On Time In Full. Meta: > 95%")
    with col4:
        st.metric("Rotación", f"{rotacion}x", "+0.3x",
                help="Veces que se renueva inventario/año. Meta: 4-12x")

    st.divider()

    # === FÓRMULAS EXPLICADAS ===
    st.subheader("📐 Definiciones y Fórmulas")

    kpis_def = [
        ("Exactitud de Inventario (Accuracy)", 
         "(Ítems registrados correctly / Total ítems físicos) × 100",
         "Mide cuánto coincide el inventario en sistema vs el físico. Un 98% significa que de cada 100 items, 98 están correctamente registrados.",
         "98-99% es excelente, 95-97% aceptable, <95% necesita mejora"),
        
        ("Pedidos Perfectos (Perfect Order Rate)",
         "(Pedidos sin errores / Total pedidos) × 100",
         "Porcentaje de pedidos entregados sin problemas: ni faltantes, ni dañados, ni retrasados.",
         "95-99% es excelente, 90-95% aceptable"),
        
        ("OTIF (On Time In Full)",
         "(Órdenes a tiempo y completas / Total órdenes) × 100",
         " El cliente recibe lo que pidió, cuando lo pidió. Combina puntualidad y completitud.",
         "95-99% es excelente, 90-95% aceptable"),
        
        ("Rotación de Inventario",
         "Costo de ventas / Inventario promedio",
         "Cuántas veces al año se renueva el inventario. Alta rotación = más flujo de dinero.",
         "4-12x/año es normal. Depende del tipo de producto."),
        
        ("Costo por Unidad Almacenada",
         "Costo operativo total / Unidades promedio almacenadas",
         "Cuánto cuesta almacenar cada unidad. Incluye mano de obra, espacio, equipos.",
         "Minimizar es el objetivo"),
        
        ("Ciclo de Pedido",
         "Tiempo desde que llega el pedido hasta que sale",
         "Mide la velocidad de procesamiento. Incluye picking, packing y despacho.",
         "< 4 horas es excelente para manual, < 1 hora con automatización"),
    ]

    for nombre, formula, desc, meta in kpis_def:
        with st.expander(f"📊 {nombre}"):
            st.markdown(f"**Fórmula:** `{formula}`")
            st.markdown(f"**Qué mide:** {desc}")
            st.markdown(f"**Meta típica:** {meta}")

    # === GRÁFICOS ===
    st.divider()
    st.subheader("📈 Tendencias (Datos Simulados)")

    # Datos simulados para gráfico educativo
    kpis_data = {
        "Mes": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
        "Accuracy": [96.0, 96.5, 97.0, 97.5, 98.0, 98.5],
        "Pedidos Perfectos": [94.0, 94.5, 95.0, 95.5, 96.0, 96.2],
        "OTIF": [91.0, 92.0, 92.5, 93.5, 94.0, 94.8],
    }
    df_kpis = pd.DataFrame(kpis_data)

    fig = px.line(df_kpis, x="Mes", y=["Accuracy", "Pedidos Perfectos", "OTIF"],
                 title="Evolución de KPIs en el Tiempo",
                 color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("💡 ¿Cómo mejorar cada KPI?"):
        st.markdown("""
        ### Consejos de mejora:
        
        | KPI | Cómo mejorar |
        |-----|-------------|
        | Accuracy | Conteos cíclicos, tecnología de escaneo |
        | Pedidos Perfectos | Verificación doble,training персонала |
        | OTIF | WMS automatización, zonas de picking |
        | Rotación | Política de-demand , productos de lento movimiento |
        """)


# ============================================================================
# BARRA LATERAL - NAVEGACIÓN PRINCIPAL
# ============================================================================
def main():
    # Sidebar
    st.sidebar.title("🏭 WMS UPB")
    st.sidebar.markdown("### Laboratorio Educativo")
    st.sidebar.image("https://www.upb.edu.co/images/logo-upb.png", width=150)
    st.sidebar.divider()

    # Menú de navegación
    menu = [
        "🏠 Inicio",
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

    # Información del curso en sidebar
    st.sidebar.divider()
    st.sidebar.markdown("""
    ### 📚 Curso
    **Gestión de Almacenamiento**
    
    **Programa:** Ingeniería Industrial
    
    **Profesor:** Ing. Cristian Javier Cano Mogollon
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 💡 Cómo usar este laboratorio
    
    1. Lee la teoría en cada módulo
    2. Practica con los simuladores
    3. Observa los cambios en tiempo real
    4. Analiza los KPIs resultantes
    """)

    # Ejecutar según selección
    if choice == "🏠 Inicio":
        show_home()
    elif choice == "📊 Dashboard":
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