from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from clases import db, Usuario, Consumo
import requests # cliente http para consumir las apis de noticias.
import os
import random

app = Flask(__name__)

# configuración de la aplicación
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db' # uri de conexión para la base de datos.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # desactiva eventos de sqlalchemy para mejorar performance.
app.config['SECRET_KEY'] = 'una-llave-secreta-muy-dificil-de-adivinar' # seed para la firma de cookies de sesión.

# configuración del módulo de noticias

# se prioriza la obtención de claves api desde variables de entorno para seguridad (best practice).
# el segundo argumento de os.getenv es un valor por defecto (fallback) que se usa si la variable de entorno no existe.
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '39bb1eb41e584d4b9c7b696a45c8ebad')
# GNEWS_API_KEY = os.getenv('GNEWS_API_KEY') # api de respaldo, opcional. si no existe, es none

# lista blanca de dominios para filtrar resultados de newsapi.
DOMINIOS_CONFIABLES = ",".join([
    "bbc.com", "dw.com", "elpais.com",
    "eluniversal.com.mx", "animalpolitico.com", "forbes.com.mx",
    "unep.org", "news.un.org", "who.int"
])

# palabras clave para un filtro sobre los resultados de la api
KEYWORDS_VERDES = [
    "reciclaje", "reciclar", "residuo", "residuos", "basura",
    "economía circular", "sustentable", "sostenible", "sostenibilidad",
    "medio ambiente", "cambio climático", "plástico", "contaminación",
    "reutilizar", "compostar", "compostaje", "emisiones", "huella de carbono",
    "energía renovable", "paneles solares", "eólica"
]

# inicialización de extensiones
db.init_app(app)

# creación del esquema de la base de datos dentro del contexto de la aplicación.
with app.app_context():
    db.create_all()

# funciones auxiliares del módulo de noticias

def _pasa_filtro_verde(articulo):
    """
    función de utilidad para el filtrado temático post-api.
    concatena título y descripción para tener más texto que analizar.
    .lower() es para hacer la búsqueda case-insensitive (no distingue mayúsculas).
    """
    texto = f"{articulo.get('title','')} {articulo.get('description','')}".lower()
    # any() : checar si cualquier palabra de nuestra lista está en el texto.
    return any(keyword in texto for keyword in KEYWORDS_VERDES)

def _normaliza_articulos_newsapi(articles):
    # adapta la respuesta de newsapi a la plantilla que tenemos, para que el frontend no se rompa, lol
    lista_limpia = []
    for articulo in articles:
        # hacemos una validación: si no hay título o url, el artículo no nos sirve.
        if not articulo.get('title') or not articulo.get('url'):
            continue
        #diccionario
        lista_limpia.append({
            "title": articulo.get('title'),
            "description": articulo.get('description'),
            "url": articulo.get('url'),
            "urlToImage": articulo.get('urlToImage'),
            "source": (articulo.get('source') or {}).get('name'), 
            "publishedAt": articulo.get('publishedAt')
        })
    return lista_limpia


# gnews


def fetch_noticias():
    """orquesta la obtención, filtrado y normalización de noticias."""
    
    # estrategia principal: newsapi
    # se inicializa una lista vacía. si todo falla, esto es lo que se devolverá.
    candidatos = []
    if NEWS_API_KEY:
        try:
            url = "https://newsapi.org/v2/everything"
            # se definen los parámetros de la consulta para la api.
            params = {
                # qintitle busca las palabras clave solo en el título, para resultados más relevantes.
                "qInTitle": "reciclaje OR \"economía circular\" OR sostenible OR sustentable OR \"medio ambiente\"",
                # q busca en todo el artículo, es más amplio.
                "q": "(reciclaje OR residuos OR \"economía circular\" OR sostenible OR sustentable OR \"medio ambiente\" OR \"cambio climático\")",
                "language": "es",
                "sortBy": "publishedAt", # ordena por fecha de publicación.
                "pageSize": 30, # pedimos más artículos de los necesarios para tener margen en el filtrado
                "domains": DOMINIOS_CONFIABLES # filtramos por nuestra lista de fuentes confiable
            }
            # la api key se envía en los headers por seguridad, como especifica la documentación de newsapi
            headers = {"X-Api-Key": NEWS_API_KEY}
            
            # se ejecuta la petición get a la api con un timeout para no dejar colgada la app.
            respuesta = requests.get(url, params=params, headers=headers, timeout=8)
            
            # un código de éxito significa que la petición fue exitosa.
            if respuesta.status_code == 200:
                datos = respuesta.json()
                candidatos = _normaliza_articulos_newsapi(datos.get("articles", []))
            else:
                # si falla, imprimimos el error
                print(f"[newsapi] error {respuesta.status_code}: {respuesta.text[:200]}")
        except requests.RequestException as e:
            # captura errores de red (ej. no hay internet).
            print(f"[newsapi] hubo un problema de conexión: {e}")

    # procesamiento: filtrado y deduplicación
    # usamos un 'set' para guardar los títulos que ya vimos,la búsqueda en un set es de orden uno, mucho más rápida que en una lista, ojooo
    vistos = set() 
    filtradas = []
    for articulo in candidatos:
        # se aplica el segundo filtro temático para asegurar relevancia.
        if not _pasa_filtro_verde(articulo):
            continue
        # se crea una clave única (el título en minúsculas) para evitar duplicados.
        clave = (articulo.get("title","").strip().lower())
        if not clave or clave in vistos:
            continue
        vistos.add(clave)
        filtradas.append(articulo)
        # se rompe el ciclo en cuanto se alcanza el límite de artículos para ser eficientes.
        if len(filtradas) == 6:
            break

    # estrategia de respaldo (fallback): gnews
    # se activa solo si la principal no arroja suficientes resultados. ---> cambiado
    

    # se retorna un slice de la lista para asegurar que nunca se envíen más del límite de artículos.
    return filtradas[:6]


# rutaaas

@app.route("/menu/<int:id_usuario>")  #pasamos el usuario de una página a otra
def menu(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    noticias = fetch_noticias()
    return render_template("menu.html", usuario=usuario, noticias=noticias)

# id_usuario : número recibido desde la URL

@app.route("/registro", methods=["GET", "POST"])  #methods, decorador de FLASK: dice qué tipo de solicitud acepta la url
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]  #request.form[]: guarda los datos enviados de un formulario (tipo diccionario, busca la key, debe coincidir con lo que esté en name)
        contrasena = request.form["contrasena"]
        if Usuario.query.filter_by(nombre=nombre).first():
            error_msg = "el nombre de usuario ya existe. por favor, elige otro."
            return render_template("registro.html", error=error_msg)
        nuevoUsuario = Usuario(nombre=nombre, contrasena=contrasena)
        db.session.add(nuevoUsuario)
        db.session.commit()
        return redirect(url_for("login", registered='true'))
    return render_template("registro.html")

@app.route("/", methods=["GET", "POST"])   #decorador de FLASK: lit dice qué hacer (o mostrar) cuando se está en esa url
def login():
    success_msg = None
    if request.args.get('registered') == 'true':
        success_msg = "¡registro exitoso! ahora puedes iniciar sesión."
    if request.method == "POST":
        nombre = request.form["nombre"]
        contrasena = request.form["contrasena"]
        usuario = Usuario.query.filter_by(nombre=nombre, contrasena=contrasena).first()  #.query : sistema de consultas
        if usuario:
            session['user_id'] = usuario.id
            return redirect(url_for("menu", id_usuario=usuario.id))
        else:
            error_msg = "usuario o contraseña incorrectos"
            return render_template("login.html", error=error_msg)
    return render_template("login.html", success=success_msg)

@app.route("/clasificador/<int:id_usuario>")
def clasificador(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    return render_template("clasificador.html", usuario=usuario)

@app.route("/cuestionario/iniciar/<int:id_usuario>")
def iniciar_cuestionario(id_usuario):
    session['respuestas'] = {}
    return redirect(url_for('cuestionario', id_usuario=id_usuario))

@app.route("/cuestionario/guardar_respuesta", methods=["POST"])
def guardar_respuesta():
    data = request.get_json()
    if 'respuestas' not in session:
        session['respuestas'] = {}
    pregunta = data.get('pregunta')
    respuesta = data.get('respuesta')
    if pregunta and respuesta is not None:
        session['respuestas'][pregunta] = respuesta
        session.modified = True
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'}), 400

@app.route("/cuestionario/<int:id_usuario>", methods=["GET", "POST"])
def cuestionario(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    if request.method == "POST":
        respuestas = session.get('respuestas', {})
        if len(respuestas) < 8:
            return render_template("cuestionario.html", usuario=usuario, respuestas=respuestas, error="parece que faltan respuestas.")
        agua = float(respuestas.get("agua", 0))
        luz = float(respuestas.get("luz", 0))
        gasolina = float(respuestas.get("gasolina", 0))
        bano = float(respuestas.get("bano", 0))
        aguaEmbot = float(respuestas.get("aguaEmbot", 0))
        reciclaje = int(respuestas.get("reciclaje", 0))
        ropa = int(respuestas.get("ropa", 0))
        consumoLocal = int(respuestas.get("consumoLocal", 0))
        aguaTotal = agua * 0.0013
        luzTotal = luz * 0.5
        gasolinaTotal = gasolina * 2.31
        duchaTotal = bano * 9 * 30 * 0.0013
        botellasTotal = aguaEmbot * 4 * 0.3
        ropaTotal = ropa * 7.5
        factor_reciclaje = {0: 1.0, 1.0: 0.9, 2.0: 0.7, 3.0: 0.5}.get(reciclaje, 1.0)
        factor_consumo = {0: 1.0, 1.0: 0.85, 2.0: 0.7}.get(consumoLocal, 1.0)
        total = (aguaTotal + luzTotal + gasolinaTotal + duchaTotal + ropaTotal + botellasTotal) * factor_reciclaje * factor_consumo
        puntaje_final = round(total, 2)
        nuevo_consumo = Consumo(
            usuario_id=usuario.id, agua=agua, luz=luz, gasolina=gasolina, bano=bano,
            aguaEmbot=aguaEmbot, reciclaje=reciclaje, ropa=ropa, consumoLocal=consumoLocal,
            puntaje=puntaje_final
        )
        db.session.add(nuevo_consumo)
        db.session.commit()
        session.pop('respuestas', None)
        return redirect(url_for("resultado", id_consumo=nuevo_consumo.id))
    respuestas_guardadas = session.get('respuestas', {})
    return render_template("cuestionario.html", usuario=usuario, respuestas=respuestas_guardadas)

@app.route("/resultado/<int:id_consumo>")
def resultado(id_consumo):
    consumo = Consumo.query.get_or_404(id_consumo)
    usuario = Usuario.query.get(consumo.usuario_id)
    puntaje = consumo.puntaje
    mensaje_titulo = ""
    mensaje_cuerpo = ""
    if puntaje <= 250:
        mensaje_titulo = "resultado sobresaliente"
        mensaje_cuerpo = "felicidades. tu huella de carbono es significativamente baja, lo que demuestra un gran compromiso ambiental. tus hábitos de consumo son un modelo a seguir."
    elif puntaje <= 500:
        mensaje_titulo = "resultado positivo"
        mensaje_cuerpo = "buen trabajo. tu huella de carbono está por debajo del promedio, indicando un esfuerzo consciente por reducir tu impacto. para optimizar tu resultado, considera áreas como el transporte o el consumo de energía."
    elif puntaje <= 750:
        mensaje_titulo = "potencial de mejora"
        mensaje_cuerpo = "tu resultado se encuentra dentro del promedio. este es un buen punto de partida para identificar áreas de mejora. pequeños ajustes en tus hábitos diarios, como el reciclaje, pueden generar un gran impacto."
    else:
        mensaje_titulo = "se recomienda acción"
        mensaje_cuerpo = "tu huella de carbono actual es elevada. te recomendamos enfocarte en acciones concretas para reducirla. empezar por un área, como disminuir el consumo de energía, puede ser un excelente primer paso."
    return render_template("resultado.html", 
                           consumo=consumo, 
                           usuario=usuario,
                           mensaje_titulo=mensaje_titulo, 
                           mensaje_cuerpo=mensaje_cuerpo)

@app.route("/historial/<int:id_usuario>")
def historial(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    consumos_ordenados = Consumo.query.filter_by(usuario_id=usuario.id).order_by(Consumo.puntaje.asc()).all()
    return render_template("historial.html", usuario=usuario, consumos=consumos_ordenados)

if __name__ == "__main__":
    app.run(debug=True)
