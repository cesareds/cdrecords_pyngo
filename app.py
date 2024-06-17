from flask import Flask, request, render_template, redirect, url_for
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import configparser

config = configparser.ConfigParser()
config.read('database.properties')

uri = config.get('URI')


# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['CDRecords']
collection = db['Musico']

app = Flask(__name__, static_folder='static')

@app.route('/home')
def index():
    return render_template('home.html')

@app.route('/musicos')
def show_musicos():
    collection = db['Musico']
    musicos = list(collection.find())
    # musicos = client.teste.musicos.find()
    return render_template('musicos.html', musicos=musicos)

@app.route('/submit_musico', methods=['POST'])
def submit_musico():
    print(request.form)
    nome = request.form['nome']
    descricao = request.form['descricao']
    genero = request.form['genero']
    cep = request.form['cep']
    rua = request.form['rua']
    estado = request.form['estado']
    telefone = request.form['telefone']
    cidade = request.form['cidade']
    url = request.form['url']
    query = {'nome': nome, 'descricao': descricao, 'genero': genero, 'cep': cep, 'rua': rua, 'estado': estado, 'telefone': telefone, 'cidade': cidade, 'url': url}
    try:
        print("Salvando...")
        collection.insert_one(query)
    except Exception as e:
        print("Error ----------------------------\n f{e}")
        
    return redirect(url_for('show_musicos'))

if __name__ == '__main__':
    app.run(debug=True)
