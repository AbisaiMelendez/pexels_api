from flask import Flask, jsonify, request, send_file, jsonify
from flask_cors import CORS
import mysql.connector
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/var/www/uploads'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)  # Permite que el frontend React acceda a la API

# Configuración de conexión a la base de datos
db_config = {
    'host': 'localhost',
    'user': 'pexels_user',
    'password': 'Jodete_03',
    'database': 'pexels_db'
}

@app.route('/api/anuncios', methods=['GET'])
def obtener_anuncios_aprobados():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM anuncios WHERE estado = 'approved'")
        anuncios = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(anuncios), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    

@app.route('/api/anuncios', methods=['POST'])
def crear_anuncio():
    try:
        data = request.get_json()
        titulo = data.get('titulo')
        descripcion = data.get('descripcion')
        categoria = data.get('categoria')
        localidad = data.get('localidad')
        imagenUrl = data.get('imagenUrl')
        precio = data.get('precio')
        whatsapp = data.get('whatsapp')
        telefono = data.get('telefono')
        url = data.get('url')
        plan = data.get('plan')

        if not all([titulo, descripcion, categoria, localidad, imagenUrl]):
            return jsonify({'error': 'Faltan datos obligatorios'}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO anuncios 
            (titulo, descripcion, categoria, localidad, imagenUrl, precio, whatsapp, telefono, url, plan, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        """, (titulo, descripcion, categoria, localidad, imagenUrl, precio, whatsapp, telefono, url, plan))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Anuncio creado correctamente'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


#api para aprobar el cambio de estado del anuncio 

@app.route('/api/anuncios/<int:anuncio_id>/aprobar', methods=['POST'])
def aprobar_anuncio(anuncio_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE anuncios SET estado = 'approved'
            WHERE id = %s
        """, (anuncio_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': f'Anuncio {anuncio_id} aprobado correctamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/anuncios/<int:anuncio_id>/rechazar', methods=['POST'])
def rechazar_anuncio(anuncio_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE anuncios SET estado = 'rejected'
            WHERE id = %s
        """, (anuncio_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': f'Anuncio {anuncio_id} rechazado correctamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/anuncios/<int:anuncio_id>/clic', methods=['POST'])
def contar_clic(anuncio_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("UPDATE anuncios SET clics = clics + 1 WHERE id = %s", (anuncio_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Clic contado'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#bloqueo de carga al folder de uploads

@app.route('/api/imagen/<nombre>')
def servir_imagen(nombre):
    ruta = os.path.join(app.config['UPLOAD_FOLDER'], nombre)
    if os.path.exists(ruta):
        return send_file(ruta)
    else:
        return jsonify({'error': 'No encontrada'}), 404


# Carga de imagenes

# Aceptar solo ciertas extensiones
EXTENSIONES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif'}

def extension_valida(nombre_archivo):
    return '.' in nombre_archivo and \
           nombre_archivo.rsplit('.', 1)[1].lower() in EXTENSIONES_PERMITIDAS

@app.route('/api/subir', methods=['POST'])
def subir_imagen():
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    archivo = request.files['imagen']

    if archivo.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    # Validar extensión
    if not extension_valida(archivo.filename):
        return jsonify({'error': 'Extensión no permitida'}), 400

    # Validar que sea un archivo de imagen real (según MIME)
    if not archivo.mimetype.startswith('image/'):
        return jsonify({'error': 'Solo se permiten archivos de imagen'}), 400

    # Guardar con nombre seguro
    nombre_seguro = secure_filename(archivo.filename)
    ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], nombre_seguro)
    archivo.save(ruta_completa)

    return jsonify({
        'mensaje': 'Imagen subida correctamente',
        'imagenUrl': nombre_seguro
    }), 201




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
