from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from clases import db, Usuario, Consumo
import requests # requests es para la API QUE NO FUNCIONAAAA
import random

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'una-llave-secreta-muy-dificil-de-adivinar'

# API de Noticias con mi key 
NEWS_API_KEY = '39bb1eb41e584d4b9c7b696a45c8ebad'

db.init_app(app)

with app.app_context():
    db.create_all()

# Rutas de Registro y Login 
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        contrasena = request.form["contrasena"]
        if Usuario.query.filter_by(nombre=nombre).first():
            error_msg = "El nombre de usuario ya existe. Por favor, elige otro."
            return render_template("registro.html", error=error_msg)
        nuevoUsuario = Usuario(nombre=nombre, contrasena=contrasena)
        db.session.add(nuevoUsuario)
        db.session.commit()
        return redirect(url_for("login", registered='true'))
    return render_template("registro.html")

@app.route("/", methods=["GET", "POST"])
def login():
    success_msg = None
    if request.args.get('registered') == 'true':
        success_msg = "¡Registro exitoso! Ahora puedes iniciar sesión."
    if request.method == "POST":
        nombre = request.form["nombre"]
        contrasena = request.form["contrasena"]
        usuario = Usuario.query.filter_by(nombre=nombre, contrasena=contrasena).first()
        if usuario:
            session['user_id'] = usuario.id
            return redirect(url_for("menu", id_usuario=usuario.id))
        else:
            error_msg = "Usuario o contraseña incorrectos"
            return render_template("login.html", error=error_msg)
    return render_template("login.html", success=success_msg)

# Rutas Principales de la App

@app.route("/menu/<int:id_usuario>")
def menu(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    
    #No jala la noticiaaaaaa
    noticia = None
    try:
        query = '"medio ambiente" OR "sostenibilidad" OR "reciclaje"'
        url = f'https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&pageSize=1&apiKey={NEWS_API_KEY}'
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            if articles:
                noticia = articles[0]
    except requests.exceptions.RequestException as e:
        print(f"No se pudo conectar a la API de noticias: {e}")

    return render_template("menu.html", usuario=usuario, noticia=noticia)

# Ruta para el clasificador de imágenes
@app.route("/clasificador/<int:id_usuario>")
def clasificador(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    return render_template("clasificador.html", usuario=usuario)


# Rutas del Cuestionario y Resultados 
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
            return render_template("cuestionario.html", usuario=usuario, respuestas=respuestas, error="Parece que faltan respuestas.")
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
        factor_reciclaje = {0: 1.0, 1: 0.9, 2: 0.7, 3: 0.5}.get(reciclaje, 1.0)
        factor_consumo = {0: 1.0, 1: 0.85, 2: 0.7}.get(consumoLocal, 1.0)
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
        mensaje_titulo = "Resultado Sobresaliente"
        mensaje_cuerpo = "Felicidades. Tu huella de carbono es significativamente baja, lo que demuestra un gran compromiso ambiental. Tus hábitos de consumo son un modelo a seguir."
    elif puntaje <= 500:
        mensaje_titulo = "Resultado Positivo"
        mensaje_cuerpo = "Buen trabajo. Tu huella de carbono está por debajo del promedio, indicando un esfuerzo consciente por reducir tu impacto. Para optimizar tu resultado, considera áreas como el transporte o el consumo de energía."
    elif puntaje <= 750:
        mensaje_titulo = "Potencial de Mejora"
        mensaje_cuerpo = "Tu resultado se encuentra dentro del promedio. Este es un buen punto de partida para identificar áreas de mejora. Pequeños ajustes en tus hábitos diarios, como el reciclaje, pueden generar un gran impacto."
    else:
        mensaje_titulo = "Se Recomienda Acción"
        mensaje_cuerpo = "Tu huella de carbono actual es elevada. Te recomendamos enfocarte en acciones concretas para reducirla. Empezar por un área, como disminuir el consumo de energía, puede ser un excelente primer paso."
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