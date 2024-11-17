from flask import Flask
from flask import render_template, request, redirect, session, flash
from flask_mysqldb import MySQL, MySQLdb
from datetime import datetime
import os
from flask import send_from_directory

app = Flask(__name__)
app.secret_key="develoteca"
mysql=MySQL()

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_DB'] = 'sitio'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/img/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'),imagen)

@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'), archivocss)


@app.route('/panes')
def panes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM panes")
    panes = cur.fetchall()
    cur.close()
    return render_template('sitio/panes.html', panes=panes)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@app.route('/admin/')
def admin_index():
    
    if not 'login' in session:
        return redirect("/admin/login")
    
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    print(_usuario)
    print(_password)
    
    if _usuario=="samuel" and _password=="2006":
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/admin")
    
    return render_template("admin/login.html", mensaje="Acceso denegado")

@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')

@app.route('/admin/panes')
def admin_panes():
    
    if not 'login' in session:
        return redirect("/admin/login")
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM panes")
    panes = cur.fetchall()
    cur.close()
    print(panes)
    return render_template('admin/panes.html', panes=panes)


@app.route('/admin/panes/guardar', methods=['POST'])
def admin_panes_guardar():
    
    if not 'login' in session:
        return redirect("/admin/login")
    
    _nombre = request.form['txtNombre']
    _url = request.form['txtURL']
    _archivo = request.files['txtImagen']
    
    tiempo= datetime.now()
    horaActual=tiempo.strftime('%Y$H%M%S')
    
    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/img/"+nuevoNombre)
    
    sql = "INSERT INTO `panes` (`id`, `nombre`, `imagen`, `url`) VALUES (NULL,%s,%s,%s);"
    datos = (_nombre, nuevoNombre, _url)
    
    cur = mysql.connection.cursor()
    cur.execute(sql, datos)
    mysql.connection.commit()
    cur.close()
    
    print(_nombre)
    print(_url)
    print(_archivo)

    return redirect('/admin/panes')

@app.route('/admin/panes/borrar',  methods=['POST'])
def admin_pan_borrar():
    
    if not 'login' in session:
        return redirect("/admin/login")
    
    _id=request.form['txtID']
    print(_id)
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT imagen FROM panes WHERE id=%s", (_id,))
    pan = cur.fetchall()
    cur.close()
    print(pan)
    
    if os.path.exists("templates/sitio/img/"+str(pan[0]['imagen'])):
        os.unlink("templates/sitio/img/"+str(pan[0]['imagen']))
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM panes WHERE id=%s", (_id,))
    mysql.connection.commit()
    cur.close()
    
    return redirect('/admin/panes')

@app.route('/sitio/panes/correo', methods=['POST'])
def admin_panes_correo():
    
    _nombre = request.form['txtNombre']
    _telefono = request.form['txtTelefono']
    _direccion = request.form['txtDireccion']
    _correo = request.form['txtCorreo']
    
    sql = "INSERT INTO `usuario`(`id`, `nombre`, `telefono`, `direccion`, `correo`) VALUES (NULL,%s,%s,%s,%s);"
    datos = (_nombre,_telefono,_direccion,_correo)
    
    cur = mysql.connection.cursor()
    cur.execute(sql, datos)
    mysql.connection.commit()
    cur.close()
    
    flash('Usuario agregado exitosamente', 'success')

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)