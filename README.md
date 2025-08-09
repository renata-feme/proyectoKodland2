# 🌱 Live Green: Asistente Ecológico Personal

## Introducción

Live Green es una aplicación web diseñada para promover la conciencia ambiental a través de herramientas prácticas. El objetivo principal es permitir a los usuarios cuantificar su huella de carbono, monitorear su progreso a lo largo del tiempo y facilitar la adopción de prácticas de reciclaje mediante tecnología de inteligencia artificial.



---

## ✨ Funcionalidades Principales

Este proyecto se compone de tres partes:

1.  **👣 Calculadora de Huella de Carbono:** Mediante un cuestionario de 8 preguntas, la aplicación calcula el impacto ambiental mensual del usuario. Las preguntas abarcan hábitos de consumo clave (energía, agua, transporte, etc.) para generar un puntaje representativo. Un puntaje menor indica un menor impacto ambiental.

2.  **🏆 Historial y Ranking:** Cada resultado del cuestionario es almacenado. La sección de "Historial" presenta estos registros en un formato de ranking, ordenados de menor a mayor puntaje, permitiendo al usuario visualizar su evolución y motivar la mejora continua.

3.  **📸 Clasificador de Residuos con IA:** Si tienes dudas sobre cómo clasificar un residuo, simplemente sube una fotografía. La aplicación utiliza un modelo de inteligencia artificial (entrenado con Teachable Machine) que analiza la imagen e identifica el tipo de residuo para facilitar su correcta separación.

---

## 🔬 Metodología del Cálculo de la Huella

El cálculo del puntaje se basa en una metodología estandarizada para convertir las acciones cotidianas en una medida cuantificable: **kilogramos de CO₂ equivalente (kg CO₂ eq.)**. El proceso es el siguiente:

1.  **Factores de Emisión:** Cada respuesta numérica del cuestionario se multiplica por un factor de emisión preestablecido. Estos factores, basados en estudios científicos, traducen unidades de consumo (ej. kWh, litros) a su equivalente en kg de CO₂.
    * `Litros de gasolina x 2.31` = kg de CO₂
    * `kWh de electricidad x 0.5` = kg de CO₂

2.  **Suma de Emisiones:** Se suman las emisiones de CO₂ calculadas para todos los hábitos de consumo evaluados (agua, electricidad, transporte, etc.).

3.  **Factores de Reducción:** Se aplican factores de reducción por prácticas sostenibles. Si el usuario recicla o consume productos locales, el total de emisiones se multiplica por un coeficiente que disminuye el puntaje final, reconociendo así sus acciones positivas.

El resultado es una estimación del impacto ambiental mensual del usuario, ofreciendo una visión clara de las áreas de oportunidad.

---

## 🚀 Instalación y Ejecución

Para ejecutar este proyecto de forma local (creemos), siga los siguientes pasos en orden:

1.  **Clonar el Repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)
    cd tu-repositorio
    ```

2.  **Configurar el Entorno Virtual:**
    Se recomienda encarecidamente el uso de un entorno virtual para aislar las dependencias del proyecto.

    ```bash
    # Para crear el entorno
    python -m venv env

    # Para activarlo (Linux)
    source env/bin/activate

    # Para activarlo (Windows)
    .\env\Scripts\activate
    ```

3.  **Instalar Dependencias:**
    Instale todas las librerías requeridas ejecutando el siguiente comando:

    ```bash
    pip install Flask Flask-SQLAlchemy Pillow numpy tensorflow requests
    ```

4.  **Ejecutar la Aplicación:**
    Una vez instaladas las dependencias, inicie el servidor de desarrollo de Flask:

    ```bash
    python app.py
    ```
    Si la instalación fue exitosa, la aplicación estará disponible en `http://127.0.0.1:5000`.

---

## 🔧 Tecnologías Implementadas

* **Backend:** Python 3, Flask.
* **Base de Datos:** SQLite a través de Flask-SQLAlchemy.
* **Frontend:** HTML, CSS, JavaScript.
* **Inteligencia Artificial:** Modelo de clasificación de imágenes desarrollado con Keras (TensorFlow) y Teachable Machine.
* **APIs Externas:** NewsAPI para la obtención de noticias en tiempo real.

---

## 💡 Casos de Uso

* **Caso 1: Nuevo Usuario.**
    Un usuario accede a la aplicación, completa el formulario de registro y procede a la sección "Calcular Huella". Tras responder el cuestionario, obtiene su primer resultado, el cual es almacenado en su historial.

* **Caso 2: Usuario Recurrente.**
    Un usuario existente inicia sesión y consulta su historial para revisar sus puntajes anteriores. Se propone reducir su impacto y completa un nuevo cuestionario, obteniendo un puntaje inferior y mejorando su posición en el ranking personal.

* **Caso 3: Clasificación de Residuos.**
    Un usuario tiene un residuo y duda sobre su correcta disposición. Accede a la herramienta "Clasificar Residuo", sube una fotografía del objeto y el sistema de IA le informa la categoría a la que pertenece, resolviendo la duda.


## ESPERAMOS SEA DE SU AGRADO :) , atte. Alonso & Renata

