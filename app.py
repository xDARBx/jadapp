from os import name
from flask import Flask
from flask import render_template, request, redirect, url_for, flash  
from flaskext.mysql import MySQL
from datetime import datetime 
import os
from flask import send_from_directory

app = Flask(__name__)
# Punto 24 de la guia - Revisar porque lo hice sola 
app.secret_key="ClaveSecreta"
mysql = MySQL() 
app.config['MYSQL_DATABASE_HOST']='localhost' 
app.config['MYSQL_DATABASE_USER']='root' 
app.config['MYSQL_DATABASE_PASSWORD']='' 
app.config['MYSQL_DATABASE_BD']='biblioteca' 
mysql.init_app(app)

# Punto 15 de la guia - Revisar porque lo hice sola 
CARPETA= os.path.join('uploads') 
app.config['CARPETA']=CARPETA

# Punto 18 de la guia - Revisar porque lo hice sola 
@app.route('/uploads/<nombreImagen>') 
def uploads(nombreImagen): 
    return send_from_directory(app.config['CARPETA'], nombreImagen)

@app.route('/')
def index():
    sql = "SELECT * FROM biblioteca.libros" 
    conn = mysql.connect() 
    cursor = conn.cursor() 
    cursor.execute(sql)
    libros=cursor.fetchall() 
    print(libros)
    conn.commit() 
    #return render_template('libros/index.html')
    return render_template('libros/index.html', libros=libros)
    
@app.route('/create') 
def create(): 
    return render_template('libros/create.html')


@app.route('/store', methods=['POST']) 
def storage(): 
    _nombre=request.form['txtNombre'] 
    _descripcion=request.form['txtDescripcion'] 
    _imagen=request.files['txtImagen']
    # Punto 24 de la guia - Revisar porque lo hice sola
    if _nombre == '' or _descripcion == '' or _imagen =='': 
        flash('Por favor complete todos los datos de los campos') 
        return redirect(url_for('create'))
    now= datetime.now() 
    tiempo= now.strftime("%Y%H%M%S") 
    if _imagen.filename!='':
        nuevoNombreimagen=tiempo+_imagen.filename 
        _imagen.save("uploads/"+nuevoNombreimagen)

    sql = "INSERT INTO biblioteca.libros (nombre, descripcion, imagen) VALUES (%s, %s, %s);" 
    datos = (_nombre, _descripcion, nuevoNombreimagen)
    conn = mysql.connect() 
    cursor = conn.cursor() 
    cursor.execute(sql, datos) 
    libros= cursor.fetchall() 
    print(libros)
    # no se si va el conn.commit de la siguiente linea
    #conn.commit() 
    # libros me queda coloreado distinto...raro...
    # La linea que sigue esta comentada porque es el Punto 17 y no se si esta OK
    #return render_template('libros/index.html', libros=libros)
    return redirect('/')

@app.route('/destroy/<int:id>') 
def destroy(id): 
    conn = mysql.connect() 
    cursor = conn.cursor()
    # Punto 16 de la guia - Revisar porque lo hice sola y creo que hice LIO
    cursor.execute("SELECT imagen FROM biblioteca.libros WHERE id=%s;") 
    fila= cursor.fetchall() 
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
    sql = "DELETE FROM biblioteca.libros WHERE id=%s;" 
    cursor.execute(sql, (id))
    conn.commit() 
    return redirect('/')

# Punto 14 de la guia - revisar que lo hice sola 
@app.route('/update', methods=['POST']) 
def update(): 
    _nombre=request.form['txtNombre'] 
    _descripcion=request.form['txtDescripcion']
    _imagen=request.files['txtImagen'] 
    id=request.form['txtID'] 
    
    sql = "UPDATE biblioteca.libros SET nombre=%s, descripcion=%s WHERE id=%s;" 
    datos=(_nombre,_descripcion,id) 
    conn = mysql.connect() 
    cursor = conn.cursor()
    now= datetime.now() 
    tiempo= now.strftime("%Y%H%M%S")
    if _imagen.filename!='': 
        nuevoNombreImagen=tiempo+_imagen.filename 
        _imagen.save("uploads/"+nuevoNombreImagen) 
        cursor.execute("SELECT imagen FROM biblioteca.libros WHERE id=%s;") 
        fila= cursor.fetchall()
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) 
        cursor.execute("UPDATE biblioteca.libros SET imagen=%s WHERE id=%s", (nuevoNombreImagen, id)) 
        conn.commit() 
        return redirect('/')
     
    cursor.execute(sql,datos) 
    conn.commit() 
    return redirect('/')

@app.route('/edit/<int:id>') 
def edit(id): 
    conn = mysql.connect() 
    cursor = conn.cursor()
    sql = "SELECT * FROM biblioteca.libros WHERE id=%s;" 
    cursor.execute(sql, (id))
    libros=cursor.fetchall() 
    conn.commit() 
    return render_template('libros/edit.html', libros=libros)



if __name__=='__main__':
    app.run(debug=True)