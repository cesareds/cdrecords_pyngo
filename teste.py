from pymongo import MongoClient
import configparser
import ssl
from bson import ObjectId  # Import necessário para usar ObjectId


config = configparser.ConfigParser()
config.read('database.properties')

uri = config.get('DATABASE', 'URI')

client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)
db = client['CDRecords']
collection = db['Integrar']
musico = db['Musico']
anda = db['Banda']

data = list(collection.find({'_id':ObjectId('665cae36d1e1161cc15d193b')}))
musicod = list(musico.find({'_id':ObjectId(data[0]['musicoId'])}))
bandad = list(anda.find({'_id':ObjectId(data[0]['bandaId'])}))

print(f"musico: {musicod}")
print(f"banda: {bandad}")