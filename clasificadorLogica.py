#me lo robé del bot, ojalá sirva

from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np

# Desactiva la notación científica para que los resultados sean más claros, está padre no?
np.set_printoptions(suppress=True)

def obtener_prediccion(ruta_modelo, ruta_imagen, ruta_etiquetas):
    """
    Toma una imagen y usa el modelo de Keras para predecir a qué clase pertenece.
    """
    # Carga el modelo
    model = load_model(ruta_modelo, compile=False)

    # Cargar las etiquetas (los nombres de las clases)
    with open(ruta_etiquetas, "r") as f:
        class_names = [line.strip() for line in f.readlines()]

    # Prepara la imagen para el modelo
    # El modelo espera una imagen de 224x224  FALTA VER QUE FUNCIONEEEE
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    
    image = Image.open(ruta_imagen).convert("RGB")
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    
    data[0] = normalized_image_array

    # Hace la predicción
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    # Devuelve la clase y el porcentaje de confianza
    return class_name, confidence_score
