## EventIA
# Agencia de Inteligencia Artificial

Plataforma web que ofrece servicios de análisis de datos mediante modelos de Machine Learning. Desarrollado con Flask, Scikit-learn, Pandas y Seaborn.

---

## 🚀 Funcionalidades

- Registro e inicio de sesión con roles: cliente y administrador.
- Creación de proyectos con subida de archivos CSV.
- Ejecución de 3 modelos de ML:
  - Análisis de sentimientos
  - Predicción de ventas
  - Detección de anomalías
- Visualización de resultados en tablas y gráficos generados con Seaborn.
- Dashboard diferente según el tipo de usuario.
- Panel de administración con acceso a todos los usuarios y proyectos.
- Control de acceso por sesión y rol.
- Sistema de verificación para registrar usuarios con rol de administrador.

---

## 📊 Modelos integrados

1. **Análisis de sentimientos**
   - Basado en clasificación (`MultinomialNB`)
   - Entrenado previamente, predice si un texto es positivo, neutro o negativo

2. **Predicción de ventas**
   - Basado en `LinearRegression` y `RandomForest`
   - Entrena con el dataset del cliente (columna 'ventas')
   - Muestra valores reales y predichos en gráfico de líneas

3. **Detección de anomalías**
   - Utiliza `IsolationForest`
   - Detecta outliers en columnas numéricas del CSV
   - Resultado visual en scatter plot con anomalías destacadas

---

## 🧱 Tecnologías utilizadas

- **Backend**: Flask, Flask-Login, Flask-WTF, SQLAlchemy
- **Frontend**: HTML, CSS, Jinja
- **Machine Learning**: Scikit-learn, Pandas, Seaborn, Matplotlib
- **Base de datos**: SQLite
- **Control de entorno**: `dotenv`, `venv`

---

## 🗂 Estructura del proyecto

```
app/
├── static/
│   └── plots/              # Gráficos generados por los modelos
├── templates/
│   ├── registro_form.html
│   ├── dashboard.html
│   └── resultado_*.html    # Vistas para cada modelo
├── machine_learning/
│   ├── sentimiento.py
│   ├── prediccion.py
│   └── anomalias.py
├── routes.py               # Todas las rutas de la aplicación
├── models.py               # Modelos de SQLAlchemy
└── __init__.py
```

---

## ⚙️ Instalación y uso

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Guillermomd01/eventia.git
   cd eventia
   ```

2. Crea el entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # en Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Crea el archivo `.env` con la clave secreta y la contraseña de administrador:
   ```
   SECRET_KEY=tu_clave_secreta
   ADMIN_SECRET=clave_para_registrar_admin
   ```

5. Ejecuta la app:
   ```bash
   flask run
   ```

---

## 🛡 Seguridad y control de acceso

- Las rutas están protegidas con `@login_required`.
- Las rutas de administración requieren rol "Administrador".
- La creación de administradores requiere verificación mediante contraseña secreta.
- Los archivos subidos se almacenan en `static/uploads` y se controlan por nombre y tipo.

---

## 📬 Contacto

Desarrollado por Guillermo
GitHub: [@Guillermomd01]https://github.com/Guillermomd01/
Email: md.guillermo1@gmail.com
