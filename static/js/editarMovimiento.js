// Obtener todos los botones "Editar"
var editarBotones = document.querySelectorAll('.editar-movimiento-btn');

// Agregar un manejador de eventos a cada botón "Editar"
editarBotones.forEach(function(boton) {
    boton.addEventListener('click', function() {
        // Obtener el ID del movimiento del atributo de datos del botón
        var movimientoId = this.getAttribute('data-movimiento-id');

        // Realizar una solicitud AJAX para obtener los datos del movimiento
        fetch(`/obtener_datos_movimiento/${movimientoId}/`)
            .then(response => response.json())
            .then(data => {
                // Actualizar el contenido del modal con los datos del movimiento
                document.getElementById('movimiento_id').value = movimientoId;
                document.getElementById('numero_endoso').value = data.numero_endoso;
                document.getElementById('motivo_endoso').value = data.motivo_endoso;
                document.getElementById('numero_orden').value = data.numero_orden;
                document.getElementById('fecha_alta_op').value = data.fecha_alta_op;
                // Actualiza otros campos según sea necesario
            })
            .catch(error => {
                console.error('Error al obtener los datos del movimiento:', error);
            });
    });
});
