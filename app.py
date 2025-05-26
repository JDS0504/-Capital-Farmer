# app.py
from flask import Flask, render_template, request, jsonify
import sqlite3
import datetime
import random
import requests
import json
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
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
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
                 precio_final, servicios_adicionales, propuesta_texto)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                cotizacion_data['propuesta_texto']
            ))
            
            conn.commit()
            print(f"✓ Cotización {cotizacion_data['numero_cotizacion']} guardada")
            return True
            
        except Exception as e:
            print(f"✗ Error al guardar cotización: {e}")
            return False
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

# Agregar ruta para generar cotización
@app.route('/generar-cotizacion', methods=['POST'])
def generar_cotizacion():
    try:
        # Recibir datos del formulario
        datos = request.get_json()
        
        # Validar datos básicos
        if not all([datos.get('nombreCliente'), datos.get('email'), 
                   datos.get('tipoServicio'), datos.get('descripcionCaso')]):
            return jsonify({'success': False, 'error': 'Datos incompletos'})
        
        # Generar número único
        numero_cotizacion = CotizacionGenerator.generar_numero_cotizacion()
        
        # Calcular precio base
        precio_base = CotizacionGenerator.calcular_precio_base(datos['tipoServicio'])
        
        # Por ahora, precio final igual al base (después agregaremos IA)
        precio_final = precio_base
        
        # Preparar datos para guardar
        cotizacion_data = {
            'numero_cotizacion': numero_cotizacion,
            'nombre_cliente': datos['nombreCliente'],
            'email': datos['email'],
            'tipo_servicio': CotizacionGenerator.mapear_tipo_servicio(datos['tipoServicio']),
            'descripcion_caso': datos['descripcionCaso'],
            'precio_base': precio_base,
            'complejidad': 'Media',  # Temporal, después será calculado por IA
            'ajuste_precio': 0,      # Temporal
            'precio_final': precio_final,
            'servicios_adicionales': [],  # Temporal
            'propuesta_texto': 'Propuesta profesional generada automáticamente.'  # Temporal
        }
        
        # Guardar en base de datos
        if DatabaseManager.guardar_cotizacion(cotizacion_data):
            return jsonify({
                'success': True,
                'cotizacion': cotizacion_data
            })
        else:
            return jsonify({'success': False, 'error': 'Error al guardar cotización'})
            
    except Exception as e:
        print(f"Error en generar_cotizacion: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'})

# Modificar la función principal para crear la tabla al inicio
if __name__ == '__main__':
    # Crear tabla al iniciar la aplicación
    DatabaseManager.crear_tabla()
    app.run(debug=True)
    
app = Flask(__name__)

# Configuración básica
app.config['SECRET_KEY'] = 'clave-secreta-para-examen'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)