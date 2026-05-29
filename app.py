import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración secreta necesaria para usar sesiones (carrito de compras)
app.secret_key = 'mi_clave_secreta_super_segura_para_la_tienda'

# Configuración para la subida de imágenes de productos
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurar que la carpeta de subidas exista al arrancar el servidor
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# -------------------------------------------------------------
# SIMULACIÓN DE BASE DE DATOS (Listas en memoria - Informática)
# -------------------------------------------------------------
categorias_db = [
    {"id": 1, "nombre": "Equipos y Laptops"},
    {"id": 2, "nombre": "Periféricos y Accesorios"},
    {"id": 3, "nombre": "Componentes y Redes"}
]

productos_db = [
    {
        "id": 1,
        "nombre": "Audífonos Gamer Pro Max",
        "precio": 999.99,
        "descripcion": "Audífonos con sonido envolvente 7.1, micrófono con cancelación de ruido y luces RGB.",
        "categoria_id": 2,
        "imagen": "audifonos.jpg"
    },
    {
        "id": 2,
        "nombre": "Monitor Gamer 24 Ultra-Slim",
        "precio": 2499.00,
        "descripcion": "Pantalla Full HD de 24 pulgadas, tasa de refresco de 144Hz y tiempo de respuesta de 1ms.",
        "categoria_id": 2,
        "imagen": "monitor.jpg"
    },
    {
        "id": 3,
        "nombre": "Mouse Óptico Ergonómico",
        "precio": 350.00,
        "descripcion": "Mouse alámbrico ajustable hasta 3200 DPI con 6 botones programables.",
        "categoria_id": 2,
        "imagen": "mouse.jpg"
    },
    {
        "id": 4,
        "nombre": "Laptop Portátil Slim 15.6\"",
        "precio": 11499.00,
        "descripcion": "Procesador de última generación, 8GB de memoria RAM y 512GB de almacenamiento SSD.",
        "categoria_id": 1,
        "imagen": "laptop.jpg"
    },
    {
        "id": 5,
        "nombre": "Gabinete CPU de Alto Rendimiento",
        "precio": 8799.00,
        "descripcion": "Computadora de escritorio armada, ideal para oficina y multitarea eficiente.",
        "categoria_id": 1,
        "imagen": "cpu.jpg"
    },
    {
        "id": 6,
        "nombre": "Cable Ethernet Cat6 Alta Velocidad",
        "precio": 120.00,
        "descripcion": "Cable de red de 5 metros, ideal para una conexión a internet estable y rápida.",
        "categoria_id": 3,
        "imagen": "cable_ethernet.jpg"
    }
]

# -------------------------------------------------------------
# FUNCIONES AUXILIARES
# -------------------------------------------------------------
def herram_archivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Context processor para ayudar a las plantillas a saber dónde está guardada cada imagen
@app.context_processor
def utilidad_imagenes():
    def obtener_ruta_imagen(nombre_imagen):
        if nombre_imagen == 'producto-placeholder.jpg':
            return url_for('static', filename=nombre_imagen)
        return url_for('static', filename='uploads/' + nombre_imagen)
    return dict(obtener_ruta_imagen=obtener_ruta_imagen)

# -------------------------------------------------------------
# RUTAS DE LA APLICACIÓN
# -------------------------------------------------------------

# 1. CATÁLOGO / INICIO
@app.route('/')
def index():
    return render_template('index.html', productos=productos_db, categorias=categorias_db)


# 2. GESTIÓN DE CATEGORÍAS (Ver y Crear)
@app.route('/categorias', methods=['GET', 'POST'])
def categorias():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        if nombre:
            nuevo_id = len(categorias_db) + 1 if categorias_db else 1
            nueva_cat = {"id": nuevo_id, "nombre": nombre}
            categorias_db.append(nueva_cat)
            flash('¡Categoría registrada exitosamente!', 'success')
        return redirect(url_for('categorias'))
        
    return render_template('categorias.html', categories=categorias_db)


# 3. REGISTRO Y ADMINISTRACIÓN DE PRODUCTOS
@app.route('/agregar-producto', methods=['GET', 'POST'])
def productos():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        descripcion = request.form.get('descripcion')
        categoria_id = request.form.get('categoria_id')
        file = request.files.get('imagen')

        # Procesar archivo de imagen
        filename = 'producto-placeholder.jpg'
        if file and herram_archivo_permitido(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if nombre and precio:
            nuevo_id = len(productos_db) + 1 if productos_db else 1
            nuevo_prod = {
                "id": nuevo_id,
                "nombre": nombre,
                "precio": float(precio),
                "descripcion": descripcion,
                "categoria_id": int(categoria_id) if categoria_id else None,
                "imagen": filename
            }
            productos_db.append(nuevo_prod)
            flash('¡Producto agregado al catálogo correctamente!', 'success')
            return redirect(url_for('index'))

    return render_template('productos.html', categorias=categorias_db)


# 4. DETALLE DE UN PRODUCTO ESPECÍFICO
@app.route('/producto/<int:id>')
def detalle_producto(id):
    producto = next((p for p in productos_db if p['id'] == id), None)
    if not producto:
        return "Producto no encontrado", 404
    return render_template('detalle_producto.html', producto=producto)


# 5. AÑADIR PRODUCTO AL CARRITO
@app.route('/agregar-al-carrito/<int:id>', methods=['GET', 'POST'])
def agregar_al_carrito(id):
    if 'carrito' not in session:
        session['carrito'] = []
    
    carrito_actual = session['carrito']
    carrito_actual.append(str(id))
    session['carrito'] = carrito_actual
    
    flash('Producto añadido al carrito.', 'success')
    return redirect(url_for('index'))


# 6. VER EL CARRITO
@app.route('/carrito')
def carrito():
    carrito_ids = session.get('carrito', [])
    carrito_usuario = []
    total = 0.0

    for prod_id in carrito_ids:
        producto_encontrado = next((p for p in productos_db if str(p.get('id')) == str(prod_id)), None)
        
        if producto_encontrado:
            carrito_usuario.append(producto_encontrado)
            precio = producto_encontrado.get('precio') or producto_encontrado.get('price') or 0
            total += float(precio)

    return render_template('carrito.html', carrito=carrito_usuario, total=total)


# 7. VACIAR CARRITO
@app.route('/limpiar-carrito')
def limpiar_carrito():
    session.pop('carrito', None)
    flash('Se ha vaciado tu carrito de compras.', 'info')
    return redirect(url_for('carrito'))


# 8. PANTALLA DE FINALIZAR COMPRA
@app.route('/finalizar-compra')
def finalizar_compra():
    if 'carrito' not in session or not session['carrito']:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('carrito'))
        
    carrito_ids = session.get('carrito', [])
    carrito_usuario = []
    total = 0.0

    for prod_id in carrito_ids:
        producto_encontrado = next((p for p in productos_db if str(p.get('id')) == str(prod_id)), None)
        if producto_encontrado:
            carrito_usuario.append(producto_encontrado)
            total += float(producto_encontrado.get('precio', 0))

    return render_template('finalizar.html', carrito=carrito_usuario, total=total)


# -------------------------------------------------------------
# ARRANQUE DEL SERVIDOR
# -------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)