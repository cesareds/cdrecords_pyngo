from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
import configparser
import ssl

config = configparser.ConfigParser()
config.read('database.properties')

uri = config.get('DATABASE', 'URI')

try:
    # Configuração da conexão com desativação da verificação de certificado SSL
    client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)
    db = client['CDRecords']
    collection_musico = db['Musico']
    collection_banda = db['Banda']
    collection_disco = db['Disco']
    collection_musica = db['Musica']
    collection_instrumento = db['Instrumento']
    print("connected with MongoDB Atlas")
except Exception as e:
    print(f"Erro ao conectar com MongoDB Atlas: {e}")

app = Flask(__name__, static_folder='static')

@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/musicos')
def show_musicos():
    try:
        musicos = list(collection_musico.find())
        return render_template('musicos.html', data=musicos)
    except Exception as e:
        return f"Erro ao recuperar músicos: {e}", 500

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
    query = {
        'nome': nome,
        'descricao': descricao,
        'genero': genero,
        'cep': cep,
        'rua': rua,
        'estado': estado,
        'telefone': telefone,
        'cidade': cidade,
        'url': url
    }
    try:
        print("Salvando...")
        collection_musico.insert_one(query)
        return redirect(url_for('show_musicos'))
    except Exception as e:
        print(f"Erro ao salvar músico: {e}")
        return f"Erro ao salvar músico: {e}", 500

@app.route('/bandas')
def show_bandas():
    try:
        bandas = list(collection_banda.find())
        return render_template('bandas.html', data=bandas)
    except Exception as e:
        return f"Erro ao recuperar bandas: {e}", 500

@app.route('/submit_banda', methods=['POST'])
def submit_banda():
    print(request.form)
    nome = request.form['nome']
    descricao = request.form['descricao']
    genero = request.form['genero']
    dataDeFormacao = request.form['dataDeFormacao']
    url = request.form['url']
    query = {
        'nome': nome,
        'descricao': descricao,
        'genero': genero,
        'dataDeFormacao': dataDeFormacao,
        'url': url
    }
    try:
        print("Salvando...")
        collection_banda.insert_one(query)
        print("Banda salva com sucesso.")
        return redirect(url_for('show_bandas'))
    except Exception as e:
        print(f"Erro ao salvar banda: {e}")
        return f"Erro ao salvar banda: {e}", 500


@app.route('/discos')
def show_discos():
    try:
        discos = list(collection_disco.find())
        return render_template('discos.html', data=discos)
    except Exception as e:
        return f"Erro ao recuperar discos: {e}", 500

@app.route('/submit_disco', methods=['POST'])
def submit_disco():
    print(request.form)
    titulo = request.form['titulo']
    artista = request.form['artista']
    genero = request.form['genero']
    dataLancamento = request.form['dataLancamento']
    preco = request.form['preco']
    platinas = request.form['platinas']
    formato = request.form['formato']
    descricao = request.form['descricao']
    url = request.form['url']
    query = {
        'titulo': titulo,
        'artista': artista,
        'genero': genero,
        'dataLancamento': dataLancamento,
        'preco': preco,
        'platinas': platinas,
        'formato': formato,
        'descricao': descricao,
        'url': url
    }
    try:
        print("Salvando...")
        collection_disco.insert_one(query)
        return redirect(url_for('show_discos'))
    except Exception as e:
        print(f"Erro ao salvar disco: {e}")
        return f"Erro ao salvar disco: {e}", 500

@app.route('/musicas')
def show_musicas():
    try:
        musicas = list(collection_musica.find())
        return render_template('musicas.html', data=musicas)
    except Exception as e:
        return f"Erro ao recuperar músicas: {e}", 500

@app.route('/submit_musica', methods=['POST'])
def submit_musica():
    print(request.form)
    titulo = request.form['titulo']
    faixa = request.form['faixa']
    autores = request.form['autores']
    duracao = request.form['duracao']
    letra = request.form['letra']
    query = {
        'titulo': titulo,
        'faixa': faixa,
        'autores': autores,
        'duracao': duracao,
        'letra': letra
    }
    try:
        print("Salvando...")
        collection_musica.insert_one(query)
        return redirect(url_for('show_musicas'))
    except Exception as e:
        print(f"Erro ao salvar música: {e}")
        return f"Erro ao salvar música: {e}", 500
    
@app.route('/search', methods=['POST'])
def show_sorted():
    types = ['bandas', 'discos', 'musicas', 'musicos', 'instrumentos']
    template = ''
    sort = ''
    for t in types:
        try:
            sort = request.form[f'sort_{t}']
            print(sort)
            template = f'{t}.html'
            break
        except KeyError as e:
            oi = 1

    try:
        if t == 'bandas':
            data = list(collection_banda.find({ 'nome': { '$regex': sort, '$options': 'i' } }).sort('nome', 1))  # Ordena por nome ascendente
        elif t == 'musicos':
            data = list(collection_musico.find({ 'nome': { '$regex': sort, '$options': 'i' } }).sort('nome', 1))  # Ordena por nome ascendente
        elif t == 'discos':
            data = list(collection_disco.find({ 'titulo': { '$regex': sort, '$options': 'i' } }).sort('nome', 1))  # Ordena por nome ascendente
        elif t == 'musicas':
            data = list(collection_musica.find({ 'titulo': { '$regex': sort, '$options': 'i' } }).sort('nome', 1))  # Ordena por nome ascendente
        elif t == 'instrumentos':
            data = list(collection_instrumento.find({ 'nome': { '$regex': sort, '$options': 'i' } }).sort('nome', 1))  # Ordena por nome ascendente
        return render_template(template, data=data)
    except Exception as e:
        return f"Erro ao recuperar músicos: {e}", 500


@app.route('/instrumentos')
def show_instrumentos():
    try:
        instrumentos = list(collection_instrumento.find())
        return render_template('instrumentos.html', data=instrumentos)
    except Exception as e:
        return f"Erro ao recuperar instrumentos: {e}", 500
    
@app.route('/submit_instrumento', methods=['POST'])
def submit_instrumento():
    print(request.form)
    nome = request.form['nome']
    descricao = request.form['descricao']
    query = {
        'nome': nome,
        'descricao': descricao
    }
    try:
        print("Salvando...")
        collection_instrumento.insert_one(query)
        return redirect(url_for('show_instrumentos'))
    except Exception as e:
        print(f"Erro ao salvar instrumento: {e}")
        return f"Erro ao salvar instrumento: {e}", 500
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) #se a porta 8080 estiver ocupada, botar outra
