# logic/database.py
from elasticsearch import Elasticsearch

# Ci connettiamo al nostro server locale
try:
    es = Elasticsearch("http://localhost:9200", request_timeout=5)
except Exception as e:
    es = None
    print(f"Errore di connessione a Elasticsearch: {e}")

def ottieni_item_per_genere(indice, genere_richiesto, campo_ordinamento, limite=3):
    # 2. DIZIONARIO DI TRADUZIONE 
    mappa_traduzioni = {
        # FILM 
        "Film: Neo-Noir": "Film-Noir", 
        "Film: Science Fiction": "Sci-Fi", 
        
        # LIBRI
        "Libri: Comic": "Comics",
        "Libri: Scary": "Horror",
        "Libri: Humor": "Humor and ComedyHumor and Comedy",
        
        # MUSICA 
        "Musica: Classic": "classical", 
        "Musica: Hip Hop": "hip-hop",
        "Musica: R&B": "r-n-b"    
    }
    
    
    genere_tradotto = mappa_traduzioni.get(genere_richiesto, genere_richiesto)
    
    # 3. RIMOZIONE DEL PREFISSO 
    # Tagliamo via "Film:", "Libri:" o "Musica:" se sono ancora presenti.
    if ": " in genere_tradotto:
        termine_finale = genere_tradotto.split(": ")[1]
    else:
        termine_finale = genere_tradotto

    # 4. LA QUERY ELASTICSEARCH CON "AND"
    query = {
        "size": 3,
        "query": {
            "match": {
                "genere_motore": { 
                    "query": termine_finale,
                    "operator": "and"
                }
            }
        },
        "sort": [
            {campo_ordinamento: {"order": "desc"}}
        ]
    }

    try:
        risposta = es.search(index=indice, body=query)
        risultati = []
        
        # Estraiamo i dati utili dalla risposta di Elasticsearch
        for hit in risposta['hits']['hits']:
            sorgente = hit['_source']
            risultati.append(sorgente)
            
        return risultati
    except Exception as e:
        print(f"Errore durante la ricerca: {e}")
        return []