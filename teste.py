import json
from pymongo import MongoClient
import configparser
from bson import ObjectId  # Import necessário para usar ObjectId

config = configparser.ConfigParser()
config.read('database.properties')

uri = config.get('DATABASE', 'URI')

client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)
db = client['CDRecords']
collection = db['Incluir']
musico = db['Musica']
anda = db['Disco']

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

# Obter valores únicos de discoId usando distinct
disco_ids = collection.distinct('discoId')

# Lista para armazenar os dados finais
final_data_list = []

# Iterar sobre cada discoId encontrado
for d in disco_ids:
    # Encontrar músicas do discoId atual
    musicas_do_disco = list(collection.find({'discoId': ObjectId(d)}))

    # Encontrar detalhes do disco usando o primeiro resultado de anda.find
    disco = list(anda.find({'_id': ObjectId(d)}))

    # Lista para armazenar detalhes das músicas
    musicod = []

    # Iterar sobre cada música do disco
    for musica in musicas_do_disco:
        # Encontrar detalhes da música usando musico.find
        musicod.append(list(musico.find({'_id': ObjectId(musica['musicaId'])})))

    # Montar dados finais para o disco atual
    final_data = {
        "url": disco[0]['url'],
        "disco_title": disco[0]['titulo'],
        "songs": mongo_to_json(musicod)  # Converter músicas para formato JSON serializável
    }

    # Adicionar dados finais à lista de dados finais
    final_data_list.append(mongo_to_json(final_data))  # Converter dados finais para formato JSON serializável

# Salvar final_data_list como um arquivo JSON
with open('teste.json', 'w', encoding='utf-8') as f:
    json.dump(final_data_list, f, indent=2, ensure_ascii=False)
