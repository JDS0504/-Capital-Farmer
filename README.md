
## Sistema web profesional para generar cotizaciones legales automáticas con análisis de inteligencia artificial integrado. Desarrollado con Flask, Bulma CSS y potenciado por Groq AI.

## 🚀 Características Principales

- ✅ Cotizaciones Automáticas: Generación de cotizaciones legales profesionales
- 🤖 Inteligencia Artificial: Análisis automático de complejidad de casos con Groq API
- 🔐 Sistema de Autenticación: Login/logout seguro con sesiones
- 📱 Diseño Responsive: Interfaz moderna y adaptable a todos los dispositivos
- 🎨 UI/UX Profesional: Diseñado con Bulma CSS y SweetAlert2
- 📊 Dashboard Personalizado: Panel de control para cada usuario
- 💾 Base de Datos: Almacenamiento persistente con SQLite

✅ Parte 1 - Sistema Base
 Frontend completo con formulario HTML
 Backend Flask funcional
 Endpoint JSON para cotizaciones
 Números únicos de cotización (COT-2025-XXXX)
 Precios según tipo de servicio
 Base de datos SQLite operativa
 Almacenamiento de todas las cotizaciones

 ✅ Parte 2 - Integración IA 
 API Groq integrada y funcional
 Análisis automático de complejidad
 Ajuste inteligente de precios (0%, 25%, 50%)
 Servicios adicionales sugeridos
 Generación automática de propuestas profesionales
 Manejo robusto de errores de API
 Sistema de fallback si la IA falla

✅ Autenticación Básica 
 Sistema completo de login/logout
 Registro de nuevos usuarios
 Sesiones seguras con Flask sessions
 Contraseñas hasheadas con Werkzeug
 Rutas protegidas con decoradores
 Dashboard personalizado por usuario

## 📋 Servicios Legales Disponibles
Constitución de Empresa: S/ 1,500  Trámites SUNARP, minuta, RUC 
Defensa Laboral:  S/ 2,000  Despidos, liquidaciones, demandas 
Consultoría Tributaria:  S/ 800  Asesoría SUNAT, planificación fiscal 

> **💡 Precios Dinámicos**: La IA ajusta el precio automáticamente según la complejidad del caso (0%, 25% o 50%)

## 🛠️ Instalación

### Prerrequisitos
- Python 3.10 o superior
- Git

### Pasos de Instalación

1. Clonar el repositorio

2. Instalar dependencias
pip install -r requirements.txt

3. Ejecutar la aplicación
python app.py

4. Acceder a la aplicación en tu navegador: 
http://localhost:5000