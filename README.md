# 🏭 WMS UPB - Sistema de Gestión de Almacenes Educativo

**Universidad Pontificia Boliviana - Ingeniería Industrial**

Sistema educativo interactivo para la enseñanza de gestión de almacenes y logística. Desarrollado como herramienta complementaria para el curso de Gestión de Almacenamiento.

## 📋 Descripción

WMS UPB es una aplicación web desarrollada en Streamlit que simula un sistema de gestión de almacenes (WMS). Permite a los estudiantes de Ingeniería Industrial practicar y entender los procesos logísticos fundamentales:

- Gestión de inventario
- Ubicación de productos
- Recepción de mercancía
- Despacho de pedidos
- Cálculo de espacios
- Indicadores KPIs

## 🚀 Características

### Módulos Educativos

| Módulo | Descripción |
|--------|-------------|
| **Dashboard** | Vista general con métricas en tiempo real |
| **Gestión de Productos** | CRUD completo de inventario |
| **Ubicaciones** | Mapa visual del almacén por zonas |
| **Movimientos** | Registro histórico de entradas y salidas |
| **Simulador Recepción** | Práctica de proceso de recepción |
| **Simulador Despacho** | Práctica de proceso de despacho |
| **Calculadora Espacios** | Proyección de capacidad |
| **KPIs Logísticos** | Métricas y tendencias |

### Tecnologías

- **Frontend:** Streamlit (Python)
- **Backend:** SQLite (Base de datos local)
- **Visualización:** Plotly Express
- **Framework:** Python 3.x

## 📦 Requisitos

```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
```

## 💻 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/cristianjaviercano/WMS_UPB.git
cd WMS_UPB
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```bash
streamlit run streamlit_app.py
```

4. Abre en tu navegador: `http://localhost:8501`

## 🎓 Uso Educativo

### Para Estudiantes

1. Explora el **Dashboard** para entender las métricas principales
2. Practica en **Simulador de Recepción** para aprender el flujo de ingresos
3. Usa **Simulador de Despacho** para entender el proceso de salidas
4. Calcula espacios con la **Calculadora de Espacios**
5. Estudia los **KPIs** para entender métricas logísticas

### Para Instructores

- La base de datos se inicializa automáticamente con datos de ejemplo
- Los estudiantes pueden practicar sin riesgo (base de datos local)
- Totalmente funcional sin conexión a internet

## 📊 Estructura de la Base de Datos

### Tabla: productos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | Primary Key |
| sku | TEXT | Código único |
| nombre | TEXT | Nombre del producto |
| categoria | TEXT | Categoría |
| cantidad | INTEGER | Unidades en stock |
| ubicacion | TEXT | Código de ubicación |
| costo_unitario | REAL | Precio unitario |

### Tabla: ubicaciones
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | Primary Key |
| codigo | TEXT | Código único (A-01-01-01) |
| zona | TEXT | Zona (A, B, C) |
| pasillo | TEXT | Número de pasillo |
| estante | TEXT | Número de estante |
| nivel | TEXT | Nivel (1-3) |
| capacidad | INTEGER | Capacidad máxima |

### Tabla: movimientos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | Primary Key |
| tipo | TEXT | entrada/salida |
| producto_id | INTEGER | Foreign Key |
| cantidad | INTEGER | Unidades |
| fecha | TEXT | Fecha y hora |

## 📝 Autor

**Ing. Cristian Javier Cano Mogollon**  
Universidad Pontificia Boliviana  
Programa: Ingeniería Industrial

## 📚 Bibliografía

- Roux, M. (2009). Gestión de Almacenes
- Ballou, R. Logística Empresarial
- Taha, H. Investigación de Operaciones

## 📄 Licencia

Apache License 2.0 - Ver archivo LICENSE

---

⭐️ Si te sirve este proyecto, ¡no olvides dar una estrella!
