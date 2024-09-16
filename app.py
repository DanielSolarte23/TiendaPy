from flask import Flask, render_template, request, redirect
import pymongo
import pymongo.errors
import os
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId

#Crear objeto de tipo flask

app = Flask(__name__)

#Crear la configuracion de la carpeta donde se van a guardar las imagenes 
app.config['UPLOAD_FOLDER']='./static/images'

#crear el objeto que se conecte a la bdd
miConexion = pymongo.MongoClient("mongodb://localhost:27017")

#crear un objeto que represente la bdd de mongo
baseDatos= miConexion['Tienda']

#Crear un objeto que represente la collecion de la bdd
productos = baseDatos['Productos']

@app.route("/")
def inicio():
    try:
        mensaje=''
        listaProductos = productos.find()
    except pymongo.errors as error:
        mensaje=str(error)
    
    return render_template("index.html", productos=listaProductos, mensaje=mensaje)

if __name__=="__main__":
    #arrancar el servidor en el puerto 8000
    app.run(port=8000,debug=True)
    
@app.route("/agregar", methods=['POST', 'GET'])
def agregar():
    if(request.method=='POST'):
        try:
            producto=None
            codigo = int(request.form['txtCodigo'])
            nombre = request.form['txtNombre']
            precio = int(request.form['textPrecio'])
            categoria = request.form['cbCategoria']
            foto = request.files['fileFoto']
            nombreArchivo = secure_filename(foto.filename)
            listaNombreArchivo = nombreArchivo.rsplit(".", 1)
            extension = listaNombreArchivo[1].lower()
            #nombre de la foto se compone del código y la extensión
            nombreFoto = f"{codigo}.{extension}"
            producto = {
                "codigo": codigo, "nombre": nombre, "precio": precio,
                "categoria": categoria, "foto": nombreFoto
            }
            #verificar si ya existe un producto con ese codigo
            existe = existeProducto(codigo)
            if (not existe):
                resultado = productos.insert_one(producto)
                if(resultado.acknowledged):
                    mensaje="Producto agregado correctamente"
                    foto.save(os.path.join(app.config["UPLOAD_FOLDER"],nombreFoto))
                    return redirect('/')# se redirecciona a la ruta de la raiz
                else:
                    mensaje="Problemas al agregar producto"
            else:
                mensaje="Ya existe un producto con ese codigo"
        except pymongo.errors as error:
            mensaje=error
            
        return render_template("frmAgregarProducto.html",mensaje=mensaje, producto=producto)
    
    
def existeProducto(codigo):
    try:
        consulta = {"codigo": producto}
        producto = productos.find_one(consulta)
        if(producto is not None):
            return True
        else:
            return False
    except pymongo.errors as error:
        print(error)
        return False


@app.route("/consultar/<string:id>", methods=["GET"])
def consultar(id):
    if(request.method=='GET'):
        try:
            id=ObjectId(id)
            consulta = {"_id":id}
            producto = productos.find_one(consulta)
            return render_template("frmActualizarProducto.html", producto=producto)
        except pymongo.errors as error:
            mensaje=error
            return redirect("/")
    
@app.route("/actualizar", methods=["POST"])
def actualizarProducto():
    try:
        if(request.method=="POST"):
            #Recibir los valores de la vista en variables locales
            codigo = int(request.form['txtCodigo'])
            nombre = request.form['txtNombre']
            precio = int(request.form['textPrecio'])
            categoria = request.form['cbCategoria']
            id=ObjectId(request.form["id"])
            #verificar si viene foto para actualizarla
            foto = request.file["fileFoto"]
            if(foto.filename!=""):
                nombreArchivo = secure_filename(foto.filename)
                listaNombreArchivo = nombreArchivo.rsplit(".",1)
                extension = listaNombreArchivo[1].lower()
                nombreFoto = f"{codigo}.{extension}"
                producto = {
                    "_id": id, "codigo":codigo, "nombre":nombre,
                    "precio":precio, "categoria":categoria, "foto": nombreFoto
                }
            else:
                producto = {
                    "_id": id, "codigo":codigo, "nombre":nombre,
                    "precio":precio, "categoria":categoria
                }
            criterio = {"_id":id}
            consulta = {"$set": producto}
            #verifica si el nuevo codigo ya existe de un producto diferente a si mismo
            existe = productos.find_one({"codigo": codigo, "_id":{"$ne":id}})
            if existe:
                mensaje="Producto ya existe con ese codigo"
                return render_template("frmActualizarProducto.html", producto=producto, mensaje=mensaje)
            else:
                resultado=productos.update_one(criterio,consulta)
                if(resultado.acknowledged):
                    mensaje="Producto Actualizado"
                    if(foto.filename!=""):
                        foto.save(os.path.join(app.config["UPLOAD_FOLDER"],nombreFoto))
                    return redirect("/")
    except pymongo.errors as error:
        mensaje=error
        return redirect("/")