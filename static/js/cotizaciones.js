// static/js/cotizaciones.js

// Aplicando principio de Single Responsibility
class FormValidator {
    static validarFormulario(formData) {
        if (!formData.nombreCliente.trim()) {
            return { valido: false, mensaje: 'El nombre es obligatorio' };
        }
        if (!formData.email.trim() || !this.validarEmail(formData.email)) {
            return { valido: false, mensaje: 'Email inválido' };
        }
        if (!formData.tipoServicio) {
            return { valido: false, mensaje: 'Debe seleccionar un tipo de servicio' };
        }
        if (!formData.descripcionCaso.trim()) {
            return { valido: false, mensaje: 'La descripción del caso es obligatoria' };
        }
        return { valido: true };
    }

    static validarEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }
}

// Clase para manejar alertas con SweetAlert2
class AlertManager {
    static mostrarCargando() {
        Swal.fire({
            title: 'Generando Cotización',
            text: 'Analizando su caso...',
            icon: 'info',
            allowOutsideClick: false,
            showConfirmButton: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
    }

    static mostrarError(mensaje) {
        Swal.fire({
            title: 'Error',
            text: mensaje,
            icon: 'error',
            confirmButtonText: 'Entendido',
            confirmButtonColor: '#3273dc'
        });
    }

    static mostrarCotizacion(cotizacion) {
        const serviciosAdicionales = cotizacion.servicios_adicionales.length > 0 
            ? `<br><strong>Servicios adicionales sugeridos:</strong><br>${cotizacion.servicios_adicionales.join(', ')}`
            : '';

        Swal.fire({
            title: '¡Cotización Generada!',
            html: `
                <div class="has-text-left">
                    <p><strong>Número:</strong> ${cotizacion.numero_cotizacion}</p>
                    <p><strong>Cliente:</strong> ${cotizacion.nombre_cliente}</p>
                    <p><strong>Servicio:</strong> ${cotizacion.tipo_servicio}</p>
                    <p><strong>Complejidad:</strong> <span class="tag ${this.getComplejidadColor(cotizacion.complejidad)}">${cotizacion.complejidad}</span></p>
                    <p><strong>Precio Final:</strong> <span style="font-size: 1.2em; color: #48c774;">S/ ${cotizacion.precio_final}</span></p>
                    ${serviciosAdicionales}
                    <br>
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
                        <strong>Propuesta:</strong><br>
                        ${cotizacion.propuesta_texto}
                    </div>
                </div>
            `,
            icon: 'success',
            confirmButtonText: 'Nueva Cotización',
            confirmButtonColor: '#48c774',
            width: '600px'
        }).then(() => {
            document.getElementById('cotizacionForm').reset();
        });
    }

    static getComplejidadColor(complejidad) {
        switch(complejidad.toLowerCase()) {
            case 'baja': return 'is-success';
            case 'media': return 'is-warning';
            case 'alta': return 'is-danger';
            default: return 'is-info';
        }
    }
}

// Manejador principal del formulario
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('cotizacionForm');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Recopilar datos del formulario
        const formData = {
            nombreCliente: document.getElementById('nombreCliente').value,
            email: document.getElementById('email').value,
            tipoServicio: document.getElementById('tipoServicio').value,
            descripcionCaso: document.getElementById('descripcionCaso').value
        };
        
        // Validar formulario
        const validacion = FormValidator.validarFormulario(formData);
        if (!validacion.valido) {
            AlertManager.mostrarError(validacion.mensaje);
            return;
        }
        
        // Mostrar confirmación antes de enviar
        Swal.fire({
            title: '¿Generar Cotización?',
            text: 'Se analizará su caso y se generará una cotización profesional',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#3273dc',
            cancelButtonColor: '#dbdbdb',
            confirmButtonText: 'Sí, generar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                enviarFormulario(formData);
            }
        });
    });
});

// Función para enviar formulario al backend
function enviarFormulario(formData) {
    AlertManager.mostrarCargando();
    
    fetch('/generar-cotizacion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        console.log('Respuesta recibida:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Datos recibidos:', data);
        if (data.success) {
            AlertManager.mostrarCotizacion(data.cotizacion);
        } else {
            AlertManager.mostrarError(data.error || 'Error al generar cotización');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        AlertManager.mostrarError('Error de conexión. Intente nuevamente.');
    });
}