import os.path
import os
import datetime
import time
import getpass
import threading
import thread
import json
import subprocess
import urllib
from urllib import quote_plus
from subprocess import call
from subprocess import Popen, PIPE
from datetime import datetime
from functools import wraps
from flask import g, request, redirect, url_for
from flask import Flask, request, render_template, send_from_directory
app = Flask(__name__, template_folder='templates')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/home")
def index():
    return render_template("home.html")

@app.route("/deleteImmaginiEvento")
def deleteImmaginiEvento():
    immagini = request.args.get('immagini')
    print(immagini)
    os.remove(immagini)
    return 'delete immagini'

#esegue il comando di feh per la riproduzione delle immagini a seconda dell'evento richiesto
@app.route("/show")
def show():
    folder = request.args.get('folder')
    print(folder)
    subprocess.Popen(['killall', '-9', 'feh'])
    time.sleep(0.5)
    subprocess.Popen(['feh', '-F', '-Y', '-D', '5', '-Z', folder])
    return 'ok'

@app.route("/deleteEvento")
def deleteEvento():
    evento = request.args.get('folder')
    if os.path.isdir(evento):
        for file in os.listdir(evento):
            file_path = os.path.join(evento, file)
            os.remove(file_path)
        os.rmdir(evento)

#esegue il comando per visualizzare le locandine
@app.route("/riproduzione_locandine")
def riproduzione_locandine():
    folderLocandine = request.args.get('folderLocandine')
    subprocess.Popen(['killall', '-9', 'feh'])
    time.sleep(0.5)
    subprocess.Popen(['feh', '-F', '-Y', '-D', '5', '-Z', folderLocandine])
    return 'ok'

@app.route("/")
def login():
    return render_template("login.html")

#avviene il controllo per il login
@app.route("/controllo", methods=["POST"])
def admin():
    password = request.form.get("password")
    username = request.form.get("username")
    if(username == "admin" and password == "admin"):
        print("Corretto")
        return render_template("home.html")
    else:
        print("Sbagliato")
        return render_template("login.html")

@app.route("/upload_programmato")
def upload_programmato():
    return render_template("upload_programmato.html")

@app.route("/upload_locandine")
def upload_locandine():
    return render_template("upload_locandine.html")

@app.route("/gestione_file")
def gestione_file():
    locandine = os.listdir('locandine')
    nome_locandine = []
    for l in locandine:
        percorso_locandina = os.path.abspath(os.path.join('locandine', l))
        print(percorso_locandina)
        nome_locandine.append('<tr><td>' + l + '</td><td><button class="btn waves-effect waves-light delete" id="show-button" locandina="' + percorso_locandina + '"><i class="material-icons">delete</i></button></td></tr>')
    return render_template("gestione_file.html", nome_locandine=nome_locandine)

@app.route("/delete")
def delete():
    locandina = request.args.get('locandina')
    print(locandina)
    os.remove(locandina)
    return 'delete'

@app.route("/upload_immediato") #carica il nome la data e l'ora dell'evento sulla lista html
def upload_immediato():
    folders = [d for d in os.listdir('images') if os.path.isdir(os.path.join('images', d))]
    eventi = []
    for f in folders:
        evento = f[14:] #prende quello che trova dopo 14 caratteri
        data = f[:8]    #prende i primi 8 caratteri
        data = data[0:4] + "/" + data[4:6] + "/" + data[6:8]
        ora = f[9:13]
        ora = ora[0:2] + ":" + ora[2:4]
        print(evento, data, ora)
        folder = os.path.abspath(os.path.join('images', f))
        eventi.append('<tr><td>' + evento + '</td><td>' + data + '</td><td>' + ora + '</td><td><button class="btn waves-effect waves-light click" id="show-button" folder="' + folder + '"><i class="material-icons">play_circle_filled</i></button></td><td><button class="btn waves-effect waves-light deleteEventi" id="show-button" folder="' + folder + '"><i class="material-icons">delete</i></button></td></tr>')
    return render_template("upload_immediato.html", eventi=eventi)

@app.route("/locandine", methods=["POST"])  #gestione delle locandine, salvataggio del file nell'appostita cartella
def locandine():
    target = os.path.join(APP_ROOT, 'locandine')
    print("Target:" + target)
    if not os.path.isdir(target):
            os.mkdir(target)
    else:
        print("Impossibile creare la directory di caricamento: {}".format(target))
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} e' il nome del file".format(upload.filename))
        filename = upload.filename
        destination = "/".join([target, filename])
        print ("Accetta il file in arrivo:", filename)
        print ("Il file viene salvato in:", destination)
        upload.save(destination)
    return render_template("completatoLocandine.html", image_name=filename)

@app.route("/upload", methods=["POST"])
def upload():
    nome_evento = request.form.get("nome_evento")   #recupera la variabile contenente il testo digitato dall'utente nella label 
    data_evento = request.form.get("data_evento")
    ora_evento = request.form.get("ora_evento")

    st = (data_evento.replace('-', '') + "_" + ora_evento.replace(':', '') + "_" + nome_evento)
    print(data_evento)

    print("Data dell'evento:" + data_evento)
    print("Ora dell'evento:" + ora_evento)
    target = os.path.join(APP_ROOT, 'images/' + st + '/')
    print("Target:" + target)
    if not os.path.isdir(target):
            os.mkdir(target)
    else:
        print("Impossibile creare la directory di caricamento: {}".format(target))
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} e' il nome del file".format(upload.filename))
        filename = upload.filename
        destination = "/".join([target, filename])
        print ("Accetta il file in arrivo:", filename)
        print ("Il file viene salvato in:", destination)
        upload.save(destination)
        
    nomeCompleto = ('information_' + nome_evento + '.json')
    path = os.path.join(APP_ROOT, 'images/' + st + '/' + nomeCompleto)
    obj = open(path, "w+")
    obj.write('{ "nomeEvento":"%s", "inizioEvento":"%s", "InizioOra":"%s" }' % (nome_evento, data_evento, ora_evento))
    obj.close()

    return render_template("completato.html", image_name=filename)

if __name__ == "__main__":
    subprocess.Popen(['feh', '-F', '-Y', '-D', '5', '-Z', '/home/pi/scripts/RaspberryScreen/locandine'])    #avvia la riproduzione delle locandine
    app.run(host='0.0.0.0', port=5000 , debug=True)