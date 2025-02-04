from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
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
    collection_criador = db['Criador']
    collection_produtor = db['Produtor']
    collection_incluir = db['Incluir']
    collection_integrar = db['Integrar']
    collection_tocar = db['Tocar']
    collection_participar = db['Participar']
    print("connected with MongoDB Atlas")
except Exception as e:
    print(f"Erro ao conectar com MongoDB Atlas: {e}")

app = Flask(__name__, static_folder='static')

    # Função para converter documentos MongoDB em JSON serializável
def mongo_to_json(doc):
    if isinstance(doc, ObjectId):
        return str(doc)  # Converte ObjectId para string
    elif isinstance(doc, list):
        return [mongo_to_json(item) for item in doc]  # Recursivamente converte lista de documentos
    elif isinstance(doc, dict):
        return {key: mongo_to_json(value) for key, value in doc.items()}  # Recursivamente converte dicionário de documentos
    else:
        return doc  # Retorna valores não documentais inalterados
@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/musicos')
def show_musicos():
    try:
        musico_ids = collection_musico.distinct('_id')
        instrumentos = list(collection_instrumento.find())
        final_data_list = []
        for m in musico_ids:
            instrumentos_do_musico = list(collection_tocar.find({'musicoId': ObjectId(m)}))

            musico = list(collection_musico.find({'_id': ObjectId(m)}))
            musico_lista = []
            # Iterar sobre cada música do disco
            for musica in instrumentos_do_musico:
                musico_lista.append(list(collection_instrumento.find({'_id': ObjectId(musica['instrumentoId'])})))

            final_data = {
                "_id":           musico[0]['_id'],
                "url":           musico[0]['url'],
                "musico_gen":  musico[0]['genero'],
                "musico_tel":   musico[0]['telefone'],
                "musico_cep":    musico[0]['cep'],
                "musico_estado":   musico[0]['estado'],
                "musico_rua":  musico[0]['rua'],
                "musico_cidade":   musico[0]['cidade'],
                "musico_nome":   musico[0]['nome'],
                "instrumentos": mongo_to_json(musico_lista)  # Converter músicas para formato JSON serializável
            }
            
            final_data_list.append(mongo_to_json(final_data))  # Converter dados finais para formato JSON serializável
        return render_template('musicos.html', data=final_data_list, instrumentos=instrumentos)
    except Exception as e:
        return f"Erro ao recuperar instrumentos: {e}", 500

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
    

@app.route('/tocar', methods=['POST'])
def tocar():
    musicoId = request.form.get('musicoId')
    instrumentoId = request.form.get('instrumentoId')
    print(f"Received musicoId: {musicoId}, instrumentoId: {instrumentoId}")
    if not musicoId or not instrumentoId:
        return "MusicoId ou InstrumentoId não fornecido", 400
    try:
        query = {
            'musicoId': ObjectId(musicoId),
            'instrumentoId': ObjectId(instrumentoId)
        }
        print("Salvando...")
        collection_tocar.insert_one(query)
        return redirect(url_for('show_musicos'))
    except InvalidId as e:
        print(f"Erro de ID inválido: {e}")
        return f"Erro de ID inválido: {e}", 400
    except Exception as e:
        print(f"Erro ao salvar tocar: {e}")
        return f"Erro ao salvar tocar: {e}", 500


@app.route('/bandas')
def show_bandas():
    try:
        banda_ids = collection_banda.distinct('_id')
        musicos = list(collection_musico.find())
        final_data_list = []
        for b in banda_ids:
            musicos_da_banda = list(collection_integrar.find({'bandaId': ObjectId(b)}))
            banda = list(collection_banda.find({'_id': ObjectId(b)}))   
            musicod = []
            for m in musicos_da_banda:
                musicod.append(list(collection_musico.find({'_id': ObjectId(m['musicoId'])})))
                # ate aqui beleza
            print(musicod)
            final_data = {
                "_id": banda[0]['_id'],
                "url": banda[0]['url'],
                "banda_nome": banda[0]['nome'],
                "banda_desc": banda[0]['descricao'],
                "banda_gen": banda[0]['genero'],
                "banda_data": banda[0]['dataDeFormacao'],
                "musicos": mongo_to_json(musicod)
            }
            
            final_data_list.append(mongo_to_json(final_data))
        return render_template('bandas.html', data=final_data_list, musicos=musicos)
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

@app.route('/integrar', methods=['POST'])
def submit_integrar():
    musicoId = request.form.get('musicoId')
    bandaId = request.form.get('bandaId')
    print(f"Received musicoId: {musicoId}, bandaId: {bandaId}")
    if not musicoId or not bandaId:
        return "MusicoId ou BandaId não fornecido", 400
    try:
        query = {
            'musicoId': ObjectId(musicoId),
            'bandaId': ObjectId(bandaId)
        }
        print("Salvando...")
        collection_integrar.insert_one(query)
        return redirect(url_for('show_bandas'))
    except InvalidId as e:
        print(f"Erro de ID inválido: {e}")
        return f"Erro de ID inválido: {e}", 400
    except Exception as e:
        print(f"Erro ao salvar integração: {e}")
        return f"Erro ao salvar integração: {e}", 500



@app.route('/discos')
def show_discos():
    try:
        # Obter valores únicos de discoId usando distinct
        disco_ids = collection_disco.distinct('_id')
        musicas = list(collection_musica.find())
        # Lista para armazenar os dados finais
        final_data_list = []

        # Iterar sobre cada discoId encontrado
        for d in disco_ids:
            # Encontrar músicas do discoId atual
            musicas_do_disco = list(collection_incluir.find({'discoId': ObjectId(d)}))

            # Encontrar detalhes do disco usando o primeiro resultado de anda.find
            disco = list(collection_disco.find({'_id': ObjectId(d)}))

            # Lista para armazenar detalhes das músicas
            musicod = []

            # Iterar sobre cada música do disco
            for musica in musicas_do_disco:
                # Encontrar detalhes da música usando musico.find
                musicod.append(list(collection_musica.find({'_id': ObjectId(musica['musicaId'])})))

                # Montar dados finais para o disco atual
            final_data = {
                "_id":         disco[0]['_id'],
                "url":          disco[0]['url'],
                "disco_title":  disco[0]['titulo'],
                "disco_desc":   disco[0]['descricao'],
                "disco_gen":    disco[0]['genero'],
                "disco_data":   disco[0]['dataLancamento'],
                "disco_preco":  disco[0]['preco'],
                "disco_plat":   disco[0]['platinas'],
                "disco_form":   disco[0]['formato'],
                "songs": mongo_to_json(musicod)  # Converter músicas para formato JSON serializável
            }
            

            # Adicionar dados finais à lista de dados finais
            final_data_list.append(mongo_to_json(final_data))  # Converter dados finais para formato JSON serializável
        return render_template('discos.html', data=final_data_list, musicas=musicas)
    except Exception as e:
        return f"Erro ao recuperar disco: {e}", 500

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
    





@app.route('/incluir', methods=['POST'])
def submit_incluir():
    discoId = request.form.get('discoId')
    musicaId = request.form.get('musicaId')
    
    # Debugging: Print the received IDs
    print(f"Received discoId: {discoId}, musicaId: {musicaId}")
    
    # Verificar se os IDs estão presentes
    if not discoId or not musicaId:
        return "DiscoId ou MusicaId não fornecido", 400
    
    try:
        query = {
            'discoId': ObjectId(discoId),
            'musicaId': ObjectId(musicaId)
        }
        print("Salvando...")
        collection_incluir.insert_one(query)
        return redirect(url_for('show_discos'))
    except InvalidId as e:
        print(f"Erro de ID inválido: {e}")
        return f"Erro de ID inválido: {e}", 400
    except Exception as e:
        print(f"Erro ao salvar inclusão: {e}")
        return f"Erro ao salvar inclusão: {e}", 500

@app.route('/musicas')
def show_musicas():
    try:
        musica_ids = collection_musica.distinct('_id')
        criadores = list(collection_criador.find())
        final_data_list = []
        for m in musica_ids:
            criador_da_musica = list(collection_participar.find({'musicaId': ObjectId(m)}))
            musica = list(collection_musica.find({'_id': ObjectId(m)}))
            musica_lista = []
            # Iterar sobre cada música do disco
            for c in criador_da_musica:
                musica_lista.append(list(collection_criador.find({'_id': ObjectId(c['criadorId'])})))

            final_data = {
                "_id":           musica[0]['_id'],
                "musica_titulo":  musica[0]['titulo'],
                "musica_faixa":   musica[0]['faixa'],
                "musica_autores":    musica[0]['autores'],
                "musica_duracao":   musica[0]['duracao'],
                "musica_letra":  musica[0]['letra'],
                "criadores": mongo_to_json(musica_lista)  # Converter músicas para formato JSON serializável
            }
            final_data_list.append(mongo_to_json(final_data))  # Converter dados finais para formato JSON serializável
        return render_template('musicas.html', data=final_data_list, criadores=criadores)
    except Exception as e:
        return f"Erro ao recuperar musicas: {e}", 500
    
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
    marca = request.form['marca']
    tipo = request.form['tipo']
    nome = request.form['nome']
    url = request.form['url']

    query = {
        'nome': nome,
        'tipo': tipo,
        'nome': nome,
        'url': url,
        'marca': marca
    }
    try:
        print("Salvando...")
        collection_instrumento.insert_one(query)
        return redirect(url_for('show_instrumentos'))
    except Exception as e:
        print(f"Erro ao salvar instrumento: {e}")
        return f"Erro ao salvar instrumento: {e}", 500
    

@app.route('/produtores')
def show_produtores():
    try:
        produtores = list(collection_produtor.find())
        return render_template('produtores.html', produtores=produtores)
    except Exception as e:
        return f"Erro ao recuperar produtores: {e}", 500
@app.route('/submit_produtor', methods=['POST'])
def submit_produtor():
    print(request.form)
    nome = request.form['nome']
    descricao = request.form['descricao']
    url = request.form['url']
    query = {
        'nome': nome,
        'descricao': descricao,
        'url': url
    }
    try:
        print("Salvando...")
        collection_produtor.insert_one(query)
        return redirect(url_for('show_produtores'))
    except Exception as e:
        print(f"Erro ao salvar produtor: {e}")
        return f"Erro ao salvar produtor: {e}", 500
    



# @app.route('/incluir')
# def show_incluir():
#     try:
#         # Obter valores únicos de discoId usando distinct
#         disco_ids = collection_incluir.distinct('discoId')

#         # Lista para armazenar os dados finais
#         final_data_list = []

#         # Iterar sobre cada discoId encontrado
#         for d in disco_ids:
#             # Encontrar músicas do discoId atual
#             musicas_do_disco = list(collection_incluir.find({'discoId': ObjectId(d)}))

#             # Encontrar detalhes do disco usando o primeiro resultado de anda.find
#             disco = list(collection_disco.find({'_id': ObjectId(d)}))

#             # Lista para armazenar detalhes das músicas
#             musicod = []

#             # Iterar sobre cada música do disco
#             for musica in musicas_do_disco:
#                 # Encontrar detalhes da música usando musico.find
#                 musicod.append(list(collection_musica.find({'_id': ObjectId(musica['musicaId'])})))

#             # Montar dados finais para o disco atual
#             final_data = {
#                 "url": disco[0]['url'],
#                 "disco_title": disco[0]['titulo'],
#                 "songs": mongo_to_json(musicod)  # Converter músicas para formato JSON serializável
#             }

#             # Adicionar dados finais à lista de dados finais
#             final_data_list.append(mongo_to_json(final_data))  # Converter dados finais para formato JSON serializável

#         return render_template('incluir.html', data=final_data_list)
#     except Exception as e:
#         return f"Erro ao recuperar instrumentos: {e}", 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) #se a porta 8080 estiver ocupada, botar outra
