# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import sqlite3
import datetime
import random
import requests
import json
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Crear la instancia de Flask PRIMERO
app = Flask(__name__)

# Configuración básica
app.config['SECRET_KEY'] = 'clave-secreta-para-examen-capital-farmer-2025'

# Principio Single Responsibility: Manejo de usuarios separado
class UserManager:
    @staticmethod
    def crear_tabla_usuarios():
        """Crea la tabla de usuarios si no existe"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                rol TEXT DEFAULT 'abogado',
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                activo INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Tabla de usuarios creada/verificada")

    @staticmethod
    def crear_usuario_admin():
        """Crea un usuario administrador por defecto"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Verificar si ya existe un admin
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            password_hash = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO usuarios (username, email, password_hash, rol)
                VALUES (?, ?, ?, ?)
            ''', ('admin', 'admin@capitalfarmer.com', password_hash, 'admin'))
            conn.commit()
            print("✅ Usuario admin creado: admin/admin123")
            
        conn.close()

    @staticmethod
    def validar_usuario(username, password):
        """Valida las credenciales del usuario"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, password_hash, rol 
            FROM usuarios 
            WHERE username = ? AND activo = 1
        ''', (username,))
        
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario and check_password_hash(usuario[3], password):
            return {
                'id': usuario[0],
                'username': usuario[1],
                'email': usuario[2],
                'rol': usuario[4]
            }
        return None

    @staticmethod
    def registrar_usuario(username, email, password, rol='abogado'):
        """Registra un nuevo usuario"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        try:
            password_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO usuarios (username, email, password_hash, rol)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, rol))
            
            conn.commit()
            print(f"✅ Usuario {username} registrado exitosamente")
            return True
            
        except sqlite3.IntegrityError as e:
            print(f"❌ Error al registrar usuario: {e}")
            return False
        finally:
            conn.close()

# Decorador para rutas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para rutas de admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        if session.get('rol') != 'admin':
            flash('No tiene permisos para acceder a esta página', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Principio Single Responsibility: Cada función una tarea específica
class DatabaseManager:
    @staticmethod
    def crear_tabla():
        """Crea la tabla de cotizaciones si no existe"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_cotizacion TEXT UNIQUE NOT NULL,
                nombre_cliente TEXT NOT NULL,
                email TEXT NOT NULL,
                tipo_servicio TEXT NOT NULL,
                descripcion_caso TEXT NOT NULL,
                precio_base REAL NOT NULL,
                complejidad TEXT,
                ajuste_precio INTEGER DEFAULT 0,
                precio_final REAL NOT NULL,
                servicios_adicionales TEXT,
                propuesta_texto TEXT,
                usuario_id INTEGER,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Tabla de cotizaciones creada/verificada")

    @staticmethod
    def guardar_cotizacion(cotizacion_data):
        """Guarda una cotización en la base de datos"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO cotizaciones 
                (numero_cotizacion, nombre_cliente, email, tipo_servicio, 
                 descripcion_caso, precio_base, complejidad, ajuste_precio, 
                 precio_final, servicios_adicionales, propuesta_texto, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cotizacion_data['numero_cotizacion'],
                cotizacion_data['nombre_cliente'],
                cotizacion_data['email'],
                cotizacion_data['tipo_servicio'],
                cotizacion_data['descripcion_caso'],
                cotizacion_data['precio_base'],
                cotizacion_data['complejidad'],
                cotizacion_data['ajuste_precio'],
                cotizacion_data['precio_final'],
                json.dumps(cotizacion_data['servicios_adicionales']),
                cotizacion_data['propuesta_texto'],
                session.get('user_id')
            ))
            
            conn.commit()
            print(f"✓ Cotización {cotizacion_data['numero_cotizacion']} guardada")
            return True
            
        except Exception as e:
            print(f"✗ Error al guardar cotización: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def obtener_cotizaciones_usuario(usuario_id):
        """Obtiene las cotizaciones de un usuario específico"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT numero_cotizacion, nombre_cliente, tipo_servicio, 
                   precio_final, fecha_creacion
            FROM cotizaciones 
            WHERE usuario_id = ?
            ORDER BY fecha_creacion DESC
        ''', (usuario_id,))
        
        cotizaciones = cursor.fetchall()
        conn.close()
        
        return cotizaciones

# NUEVA CLASE: Migración de base de datos
class DatabaseMigration:
    @staticmethod
    def verificar_y_migrar():
        """Verifica la estructura de la BD y migra si es necesario"""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        try:
            # Verificar si existe la columna usuario_id
            cursor.execute("PRAGMA table_info(cotizaciones)")
            columnas = [info[1] for info in cursor.fetchall()]
            
            if 'usuario_id' not in columnas:
                print("🔄 Migrando base de datos: agregando columna usuario_id...")
                
                # Agregar columna usuario_id
                cursor.execute('''
                    ALTER TABLE cotizaciones 
                    ADD COLUMN usuario_id INTEGER
                ''')
                
                # Actualizar registros existentes con usuario_id = 1 (admin)
                cursor.execute('''
                    UPDATE cotizaciones 
                    SET usuario_id = 1 
                    WHERE usuario_id IS NULL
                ''')
                
                conn.commit()
                print("✅ Migración completada exitosamente")
            else:
                print("✓ Base de datos actualizada")
                
        except Exception as e:
            print(f"❌ Error en migración: {e}")
        finally:
            conn.close()

# Principio Single Responsibility: Generador de números únicos
class CotizacionGenerator:
    @staticmethod
    def generar_numero_cotizacion():
        """Genera un número de cotización único"""
        año_actual = datetime.datetime.now().year
        numero_aleatorio = random.randint(1000, 9999)
        return f"COT-{año_actual}-{numero_aleatorio}"

    @staticmethod
    def calcular_precio_base(tipo_servicio):
        """Calcula el precio base según el tipo de servicio"""
        precios = {
            'constitucion': 1500,
            'laboral': 2000,
            'tributaria': 800
        }
        return precios.get(tipo_servicio, 0)

    @staticmethod
    def mapear_tipo_servicio(tipo_servicio):
        """Mapea el código del servicio a su nombre completo"""
        servicios = {
            'constitucion': 'Constitución de Empresa',
            'laboral': 'Defensa Laboral',
            'tributaria': 'Consultoría Tributaria'
        }
        return servicios.get(tipo_servicio, tipo_servicio)

# Principio Single Responsibility: Manejo de IA separado
class IAAnalyzer:
    @staticmethod
    def analizar_caso(descripcion, tipo_servicio):
        """Analiza el caso usando Groq AI y retorna análisis estructurado"""
        try:
            # Configuración de Groq API
            api_key = "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"
            url = "https://api.groq.com/openai/v1/chat/completions"
            
            prompt = f"""
            Eres un abogado experto peruano analizando un caso legal.
            
            Tipo de servicio: {tipo_servicio}
            Descripción del caso: {descripcion}
            
            Analiza y responde ÚNICAMENTE en formato JSON válido sin backticks ni explicaciones:

            {{"complejidad": "Baja", "ajuste_precio": 0, "servicios_adicionales": ["Servicio 1"], "propuesta_texto": "Texto aquí"}}
            
            Criterios:
            - Complejidad "Baja" (ajuste 0): Casos simples
            - Complejidad "Media" (ajuste 25): Casos moderados  
            - Complejidad "Alta" (ajuste 50): Casos complejos
            
            Servicios adicionales: máximo 3 relevantes
            Propuesta: 2-3 párrafos profesionales
            
            SOLO JSON, SIN ```json NI EXPLICACIONES.
            """
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system", 
                        "content": "Responde únicamente con JSON válido. No uses backticks ni explicaciones adicionales."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 800,
                "temperature": 0.3
            }
            
            print("🤖 Enviando solicitud a Groq AI...")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                respuesta_ia = response.json()
                contenido = respuesta_ia['choices'][0]['message']['content'].strip()
                
                print(f"📄 Respuesta de IA: {contenido}")
                
                # LIMPIEZA MEJORADA del JSON
                contenido_limpio = IAAnalyzer.limpiar_json(contenido)
                
                # Intentar parsear JSON
                try:
                    analisis = json.loads(contenido_limpio)
                    
                    # Validar y corregir campos
                    analisis_validado = IAAnalyzer.validar_analisis(analisis)
                    
                    print(f"✅ Análisis IA exitoso: {analisis_validado['complejidad']} complejidad")
                    return {
                        'success': True,
                        'analisis': analisis_validado
                    }
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Error parseando JSON limpio: {e}")
                    print(f"JSON limpio: {contenido_limpio}")
                    return IAAnalyzer.get_analisis_fallback()
            else:
                print(f"❌ Error API Groq: {response.status_code} - {response.text}")
                return IAAnalyzer.get_analisis_fallback()
                
        except Exception as e:
            print(f"❌ Error inesperado en análisis IA: {e}")
            return IAAnalyzer.get_analisis_fallback()
    
    @staticmethod
    def limpiar_json(contenido):
        """Limpia el contenido JSON de backticks y caracteres extra"""
        # Remover backticks y marcadores de código
        contenido = contenido.strip()
        
        # Remover ```json al inicio
        if contenido.startswith('```json'):
            contenido = contenido[7:]
        
        # Remover ``` al inicio (sin json)
        if contenido.startswith('```'):
            contenido = contenido[3:]
        
        # Remover ``` al final
        if contenido.endswith('```'):
            contenido = contenido[:-3]
        
        # Remover espacios y saltos de línea extra
        contenido = contenido.strip()
        
        return contenido
    
    @staticmethod
    def validar_analisis(analisis):
        """Valida y corrige el análisis de IA"""
        # Campos por defecto
        analisis_validado = {
            'complejidad': 'Media',
            'ajuste_precio': 25,
            'servicios_adicionales': ['Consulta legal'],
            'propuesta_texto': 'Propuesta profesional generada automáticamente.'
        }
        
        # Validar complejidad
        if 'complejidad' in analisis and analisis['complejidad'] in ['Baja', 'Media', 'Alta']:
            analisis_validado['complejidad'] = analisis['complejidad']
        
        # Validar ajuste de precio
        if 'ajuste_precio' in analisis and isinstance(analisis['ajuste_precio'], (int, float)):
            ajuste = int(analisis['ajuste_precio'])
            if ajuste in [0, 25, 50]:
                analisis_validado['ajuste_precio'] = ajuste
        
        # Validar servicios adicionales
        if 'servicios_adicionales' in analisis and isinstance(analisis['servicios_adicionales'], list):
            servicios = analisis['servicios_adicionales'][:3]  # Máximo 3
            if servicios:
                analisis_validado['servicios_adicionales'] = servicios
        
        # Validar propuesta texto
        if 'propuesta_texto' in analisis and isinstance(analisis['propuesta_texto'], str):
            propuesta = analisis['propuesta_texto'].strip()
            if len(propuesta) > 20:  # Mínimo 20 caracteres
                analisis_validado['propuesta_texto'] = propuesta
        
        return analisis_validado
    
    @staticmethod
    def get_analisis_fallback():
        """Análisis por defecto si la IA falla"""
        return {
            'success': True,
            'analisis': {
                'complejidad': 'Media',
                'ajuste_precio': 25,
                'servicios_adicionales': ['Revisión de documentos', 'Consulta adicional'],
                'propuesta_texto': 'Estimado cliente, hemos analizado su caso y consideramos que requiere atención especializada de nuestro equipo legal. Nos comprometemos a brindarle un servicio profesional y oportuno, asegurando que todos los aspectos legales sean manejados con la mayor diligencia. La propuesta incluye todos los servicios necesarios para resolver su situación de manera efectiva y dentro de los plazos establecidos.'
            }
        }

# ===============================
# RUTAS PÚBLICAS (SIN AUTENTICACIÓN)
# ===============================

@app.route('/')
def index():
    """NUEVA: Landing page pública - NO requiere autenticación"""
    return render_template('landing.html')

# ===============================
# RUTAS DE AUTENTICACIÓN
# ===============================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta para iniciar sesión"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        usuario = UserManager.validar_usuario(username, password)
        
        if usuario:
            session['user_id'] = usuario['id']
            session['username'] = usuario['username']
            session['email'] = usuario['email']
            session['rol'] = usuario['rol']
            
            flash(f'¡Bienvenido, {usuario["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Ruta para cerrar sesión"""
    username = session.get('username', 'Usuario')
    session.clear()
    flash(f'Sesión cerrada. ¡Hasta pronto, {username}!', 'info')
    return redirect(url_for('index'))  # CAMBIADO: Redirige a landing page

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Ruta para registrar nuevo usuario"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if UserManager.registrar_usuario(username, email, password):
            flash('Usuario registrado exitosamente. Puede iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error al registrar usuario. Nombre de usuario o email ya existe.', 'error')
    
    return render_template('register.html')

# ===============================
# RUTAS PROTEGIDAS DEL SISTEMA
# ===============================

@app.route('/sistema')
@login_required
def sistema():
    """NUEVA: Página principal del sistema - redirige a dashboard"""
    return redirect(url_for('dashboard'))

@app.route('/sistema/dashboard')
@login_required
def dashboard():
    """Dashboard principal después del login"""
    cotizaciones = DatabaseManager.obtener_cotizaciones_usuario(session['user_id'])
    return render_template('dashboard.html', cotizaciones=cotizaciones)

@app.route('/sistema/cotizar')
@login_required
def cotizar():
    """Ruta para crear cotizaciones - PROTEGIDA"""
    return render_template('cotizacion.html')  # CAMBIADO: ahora se llama cotizacion.html

@app.route('/sistema/generar-cotizacion', methods=['POST'])
@login_required
def generar_cotizacion():
    """Ruta para generar una nueva cotización con análisis de IA - PROTEGIDA"""
    try:
        # Recibir datos del formulario
        datos = request.get_json()
        
        # Validar datos básicos
        if not all([datos.get('nombreCliente'), datos.get('email'), 
                   datos.get('tipoServicio'), datos.get('descripcionCaso')]):
            return jsonify({'success': False, 'error': 'Datos incompletos'})
        
        print(f"📝 Procesando cotización para: {datos['nombreCliente']} (Usuario: {session['username']})")
        
        # Generar número único
        numero_cotizacion = CotizacionGenerator.generar_numero_cotizacion()
        
        # Calcular precio base
        precio_base = CotizacionGenerator.calcular_precio_base(datos['tipoServicio'])
        tipo_servicio_nombre = CotizacionGenerator.mapear_tipo_servicio(datos['tipoServicio'])
        
        print(f"💰 Precio base: S/ {precio_base}")
        
        # **ANÁLISIS CON IA DE GROQ**
        print("🤖 Iniciando análisis con Groq AI...")
        resultado_ia = IAAnalyzer.analizar_caso(datos['descripcionCaso'], tipo_servicio_nombre)
        
        if resultado_ia['success']:
            analisis = resultado_ia['analisis']
            
            # Calcular precio final con ajuste de IA
            ajuste_porcentaje = analisis.get('ajuste_precio', 0)
            precio_ajuste = precio_base * (ajuste_porcentaje / 100)
            precio_final = precio_base + precio_ajuste
            
            print(f"📊 Análisis completado: {analisis['complejidad']} complejidad, +{ajuste_porcentaje}% ajuste")
            print(f"💵 Precio final: S/ {precio_final}")
        else:
            # Fallback si IA falla completamente
            analisis = resultado_ia['analisis']
            precio_final = precio_base
            print("⚠️ Usando análisis por defecto")
        
        # Preparar datos para guardar
        cotizacion_data = {
            'numero_cotizacion': numero_cotizacion,
            'nombre_cliente': datos['nombreCliente'],
            'email': datos['email'],
            'tipo_servicio': tipo_servicio_nombre,
            'descripcion_caso': datos['descripcionCaso'],
            'precio_base': precio_base,
            'complejidad': analisis['complejidad'],
            'ajuste_precio': analisis.get('ajuste_precio', 0),
            'precio_final': precio_final,
            'servicios_adicionales': analisis.get('servicios_adicionales', []),
            'propuesta_texto': analisis.get('propuesta_texto', 'Propuesta generada automáticamente.')
        }
        
        # Guardar en base de datos
        if DatabaseManager.guardar_cotizacion(cotizacion_data):
            print(f"✅ Cotización {numero_cotizacion} procesada exitosamente")
            return jsonify({
                'success': True,
                'cotizacion': cotizacion_data
            })
        else:
            return jsonify({'success': False, 'error': 'Error al guardar cotización'})
            
    except Exception as e:
        print(f"❌ Error crítico en generar_cotizacion: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'})

# Ejecutar la aplicación
if __name__ == '__main__':
    # Crear tablas al iniciar la aplicación
    print("🗄️ Inicializando base de datos...")
    UserManager.crear_tabla_usuarios()
    DatabaseManager.crear_tabla()
    
    # ✅ NUEVA LÍNEA: Verificar y migrar BD
    DatabaseMigration.verificar_y_migrar()
    
    UserManager.crear_usuario_admin()
    print("🚀 Iniciando servidor Flask con autenticación...")
    print("🌐 Landing page: http://localhost:5000")
    print("🔐 Login: http://localhost:5000/login")
    print("👤 Usuario admin: admin/admin123")
    app.run(debug=True)