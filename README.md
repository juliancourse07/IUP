# Uniputumayo — Dashboard de Valor Agregado Saber T&T

Dashboard interactivo desarrollado con **Streamlit** para presentar el análisis de Valor Agregado (VA) de los resultados Saber T&T de la **Institución Universitaria del Putumayo (Uniputumayo)**.

---

## Estructura del proyecto

```
IUP/
├── app.py                        ← Aplicación principal Streamlit
├── requirements.txt              ← Dependencias Python
├── .streamlit/
│   └── config.toml               ← Tema visual Uniputumayo
├── assets/
│   ├── logo_uniputumayo.png      ← Logo (reemplazar con el oficial)
│   └── README.md                 ← Instrucciones para el logo
└── modules/
    ├── __init__.py
    ├── data_loader.py            ← Carga de datos desde Google Sheets
    ├── va_calculator.py          ← Cálculo del Valor Agregado
    └── charts.py                 ← Gráficos Plotly
```

---

## Vistas del dashboard

| Tab | Contenido |
|-----|-----------|
| 📊 Resumen General | KPIs institucionales y tabla de VA por programa |
| 🏫 Análisis por Programa | Tendencia VA, radar por componente e interpretación automática |
| 🔍 Comparación Programas | Barras horizontales comparando todos los programas |
| 📈 Histórico Puntajes | Puntajes promedio por componente a lo largo del tiempo |
| 📋 Datos Completos | Tabla cruda descargable en CSV |

---

## Ejecución local

### Requisitos previos
- Python 3.10 o superior
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/juliancourse07/IUP.git
cd IUP

# 2. Crear y activar entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
streamlit run app.py
```

La aplicación quedará disponible en `http://localhost:8501`.

---

## Logo institucional

El archivo `assets/logo-uniputumayo.webp` contiene el logo institucional de Uniputumayo.

**Fuente original:** [Logo azul Uniputumayo — itp.edu.co](https://itp.edu.co/ITP2022/wp-content/uploads/2025/11/Logo-azul-PNG-01-scaled.webp)

Para reemplazarlo con la imagen oficial:
1. Descarga el logo desde la fuente indicada arriba.
2. Guárdalo en el repositorio como `assets/logo-uniputumayo.webp`.
3. El app lo detectará automáticamente y lo mostrará en el encabezado y la barra lateral.

> **Nota:** Si prefieres usar PNG, guarda el archivo como `assets/logo_uniputumayo.png` y el app también lo reconocerá como alternativa.

---

## Despliegue en Streamlit Community Cloud (gratis)

1. **Sube el repositorio a GitHub** (si aún no lo has hecho):
   ```bash
   git push origin main
   ```

2. **Crea una cuenta** en [share.streamlit.io](https://share.streamlit.io) con tu cuenta GitHub.

3. Haz clic en **"New app"** y configura:
   - **Repository**: `juliancourse07/IUP`
   - **Branch**: `main`
   - **Main file path**: `app.py`

4. Haz clic en **"Deploy"**. En unos minutos tendrás una URL pública gratuita:
   ```
   https://<usuario>-iup-app-<hash>.streamlit.app
   ```

### Variables de entorno / secretos
El Google Sheet utilizado es **público**, por lo que no se necesitan credenciales.  
Si en el futuro el sheet se vuelve privado, agrega las credenciales en **Settings → Secrets** de Streamlit Cloud (nunca en el repositorio).

---

## Metodología de Valor Agregado

Para cada año se entrena un modelo de regresión lineal global usando **todos** los estudiantes de ese año:

```
TyT_componente ~ SB11_proxy
```

El VA de un programa es el **promedio de residuales** de sus estudiantes:

```
VA_programa = mean(TyT_observado − TyT_esperado(SB11))
```

| Componente | Variable TyT | Variable SB11 |
|------------|-------------|----------------|
| Lectura Crítica | `mod_lectura_critica_punt` | `sb11_punt_lectura_critica` |
| Razonamiento Cuantitativo | `mod_razona_cuantitat_punt` | `sb11_punt_matematicas` |
| Inglés | `mod_ingles_punt` | `sb11_punt_ingles` |
| Competencias Ciudadanas | `mod_competen_ciudada_punt` | `sb11_punt_sociales_ciudadanas` |
| Comunicación Escrita | `mod_comuni_escrita_punt` | *(sin proxy: VA = media prog. − media global)* |

**VA Total** = promedio de los VA de componentes disponibles.  
Solo se incluyen programas con al menos **10 estudiantes**.

---

## Fuente de datos

- Google Sheets ID: `18SHpWulw1uLPc6mZx3daDyT_WQuzHrF-Nz1py_YWfog`
- Hojas: `2023`, `2024`
- Acceso vía exportación CSV pública (sin autenticación)
- Caché de 1 hora para optimizar el rendimiento

---

## Tecnologías

- [Streamlit](https://streamlit.io) — Framework UI
- [Pandas](https://pandas.pydata.org) — Procesamiento de datos
- [scikit-learn](https://scikit-learn.org) — Modelos de regresión
- [Plotly](https://plotly.com/python/) — Gráficos interactivos
