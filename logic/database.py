# logic/database.py
from elasticsearch import Elasticsearch

# Ci connettiamo al nostro server locale
try:
    es = Elasticsearch("http://localhost:9200", request_timeout=5)
except Exception as e:
    es = None
    print(f"Errore di connessione a Elasticsearch: {e}")

def ottieni_item_per_genere(indice, genere_richiesto, campo_ordinamento, limite=3):
    """
    Interroga Elasticsearch per trovare i migliori item di un certo genere.
    """
    if es is None or not es.ping():
        return [{"titolo": "Database offline", "extra": "Assicurati di aver avviato Elasticsearch"}]

    # Costruiamo la query JSON per Elasticsearch
    query = {
        "size": limite, # Vogliamo solo i primi X risultati
        "query": {
            "match": {
                "genere_motore": genere_richiesto # Es. "Film: Comedy"
            }
        },
        "sort": [
            {campo_ordinamento: {"order": "desc"}} # Ordina dal voto/popolarità più alto al più basso
        ]
    }

    try:
        risposta = es.search(index=indice, body=query)
        risultati = []
        
        # Estraiamo i dati utili dalla risposta complessa di Elasticsearch
        for hit in risposta['hits']['hits']:
            sorgente = hit['_source']
            risultati.append(sorgente)
            
        return risultati
    except Exception as e:
        print(f"Errore durante la ricerca: {e}")
        return []