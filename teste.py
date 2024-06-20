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
musico = db['Musico']
anda = db['Disco']
participar = db['Participar']
criador = db['Criador']

for x in list(criador.find()):
    print(x)