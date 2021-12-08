from os import name
from flask import Flask
from flask import render_template,request,redirect,url_for,flash  
from flaskext.mysql import MySQL
from datetime import datetime 
import os
from flask import send_from_directory

app = Flask(__name__)
app.secret_key="ClaveSecreta"
mysql = MySQL() 
app.config['MYSQL_DATABASE_HOST']='localhost' 
app.config['MYSQL_DATABASE_USER']='root' 
app.config['MYSQL_DATABASE_PASSWORD']='' 
app.config['MYSQL_DATABASE_BD']='tinky' 


mysql.init_app(app)

CARPETA= os.path.join('uploads') 
app.config['CARPETA']=CARPETA

# CLASE CRUD IV - Se puede hacer una funcion para def query mysql

@app.route('/uploads/<nombreImagen>') 
def uploads(nombreImagen): 
    return send_from_directory(app.config['CARPETA'], nombreImagen)

@app.route('/')
def index():
    # sql = "INSERT INTO tinky.libros (`id`, `nombre`, `descripcion`, `Imagen`) VALUES (NULL, 'Rayuela', 'LALALALA', 'rayuela.jpg');" 
    sql = "SELECT * FROM tinky.libros;"
    conn = mysql.connect() 
    cursor = conn.cursor() 
    cursor.execute(sql) 
    libros=cursor.fetchall() 
    print(libros)
    conn.commit()
    return render_template('libros/index.html', libros=libros)


@app.route('/destroy/<int:id>') 
def destroy(id): 
    conn = mysql.connect() 
    cursor = conn.cursor()
    cursor.execute("SELECT imagen FROM tinky.libros WHERE id=%s", id) 
    # VER SI VA FETCHALL O FETCHONE()[0]
    fila= cursor.fetchall()
    # OJO - En CRUD IV min 14 se propone poner un "Try: instruccion" "Except: pass"
    # Esto se podria hacer tambien en UPDATE
    try:
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
    except:
        pass
    cursor.execute("DELETE FROM tinky.libros WHERE id=%s", (id)) 
    conn.commit() 
    return redirect('/')

@app.route('/create') 
def create(): 
    return render_template('libros/create.html')

@app.route('/store', methods=['POST']) 
def storage(): 
    _nombre=request.form['txtNombre'] 
    _descripcion=request.form['txtDescripcion'] 
    _imagen=request.files['txtImagen']
    _autor=request.form['txtAutor']
    if _nombre == '' or _descripcion == '' or _imagen =='' or _autor =='': 
        flash('Por favor complete todos los datos de los campos') 
        return redirect(url_for('create'))
    now= datetime.now() 
    tiempo= now.strftime("%Y%H%M%S") 
    if _imagen.filename!='':
        nuevoNombreImagen=tiempo+_imagen.filename 
        _imagen.save("uploads/"+nuevoNombreImagen)
    sql = "INSERT INTO tinky.libros (id, nombre, descripcion, imagen, autor) VALUES (NULL, %s, %s, %s, %s);" 
    datos = (_nombre, _descripcion, nuevoNombreImagen, _autor)
    conn = mysql.connect() 
    cursor = conn.cursor() 
    cursor.execute(sql, datos) 
    libros= cursor.fetchall() 
    print(libros)
    conn.commit() 
    # La linea que sigue esta comentada porque es el Punto 17 y no se si esta OK
    # return render_template('libros/index.html', libros=libros)
    return redirect('/')


@app.route('/update', methods=['POST']) 
def update(): 
    _nombre=request.form['txtNombre'] 
    _descripcion=request.form['txtDescripcion']
    _imagen=request.files['txtImagen']
    _autor=request.form['txtAutor']  
    id=request.form['txtID'] 
    
    sql = "UPDATE tinky.libros SET nombre=%s, descripcion=%s, autor=%s WHERE id=%s;" 
    datos=(_nombre,_descripcion,_autor,id) 
    conn = mysql.connect() 
    cursor = conn.cursor()
    now= datetime.now() 
    tiempo= now.strftime("%Y%H%M%S")
    if _imagen.filename!='': 
        nuevoNombreImagen=tiempo+_imagen.filename 
        _imagen.save("uploads/"+nuevoNombreImagen) 
        cursor.execute("SELECT imagen FROM tinky.libros WHERE id=%s", id) 
        # VER SI VA FETCHALL O FETCHONE()[0]
        fila= cursor.fetchall()
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) 
        cursor.execute("UPDATE tinky.libros SET imagen=%s WHERE id=%s", (nuevoNombreImagen, id)) 
        conn.commit() 
        return redirect('/')
     
    cursor.execute(sql, datos) 
    conn.commit() 
    return redirect('/')

@app.route('/edit/<int:id>') 
def edit(id): 
    conn = mysql.connect() 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM tinky.libros WHERE id=%s", (id)) 
    # VER SI VA FETCHALL O FETCHONE()[0]
    libros=cursor.fetchall() 
    conn.commit() 
    return render_template('libros/edit.html', libros=libros)


if __name__=='__main__':
    app.run(debug=True)