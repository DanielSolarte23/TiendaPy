/* Funcion que responde al Evento
change del campo fileFoto y muestra
la foto seleccionada en un elemento del tipo
image del formulario llamado imageProducto */

// @parms {*} evento 

function visualizarFoto(evento){
    $fileFoto = document.querySelector('#fileFoto')
    $imagenPrevisualizacion = document.querySelector("#imagenProducto")
    const files = evento.files
    const archivo = files[0]
    let filename = archivo.name
    let extension = filename.split('.').pop()
    extension = extension.toLowerCase()
    if (extension!=="jpg") {
        $fileFoto.value=""
        alert("La imagen debe ser en formato jpg")
    }else{
        const objectURL = URL.createObjectURL(archivo)
        $imagenPrevisualizacion.src = objectURL
    }
}