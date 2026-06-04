# logic/database.py
from elasticsearch import Elasticsearch

# Ci connettiamo al nostro server locale
try:
    es = Elasticsearch("http://localhost:9200", request_timeout=5)
except Exception as e:
    es = None
    print(f"Errore di connessione a Elasticsearch: {e}")

def ottieni_item_per_genere(indice, genere_richiesto, campo_ordinamento, limite=3):
    # 1. DIZIONARIO DI TRADUZIONE (Con prefisso, a prova di collisione!)
    mappa_traduzioni = {
        # ==================== FILM ====================
        "Film: Neo-Noir": "Film-Noir", 
        "Film: Foreign": "Drama",       
        "Film: Cartoon": "Animation",
        "Film: Science Fiction": "Sci-Fi", 
        "Film: Parody": "Comedy",
        "Film: Tragedy": "Drama",
        
        # ==================== LIBRI ====================
        "Libri: Comic": "Comics",
        "Libri: Educational": "Non-Fiction",
        "Libri: Non Fiction": "Non-Fiction", 
        "Libri: Humor": "Humor and ComedyHumor and Comedy", 
        "Libri: War": "History", # Solo per i libri 'War' diventa 'History'!
        "Libri: Scary": "Horror",
        
        # ==================== MUSICA ====================
        "Musica: Classic": "classical", 
        "Musica: Rap": "hip-hop",
        "Musica: Hip Hop": "hip-hop",
        "Musica: R&B": "r-n-b",            
        "Musica: Oldies": "rock-n-roll"    
    }
    
    # 2. TRADUZIONE IMMEDIATA
    # Se la chiave intera (es. "Libri: War") esiste, la traduce in "History".
    # Se non esiste (es. "Film: War"), la lascia esattamente com'era: "Film: War".
    genere_tradotto = mappa_traduzioni.get(genere_richiesto, genere_richiesto)
    
    # 3. RIMOZIONE DEL PREFISSO 
    # Ora tagliamo via "Film:", "Libri:" o "Musica:" se sono ancora presenti.
    if ": " in genere_tradotto:
        termine_finale = genere_tradotto.split(": ")[1]
    else:
        termine_finale = genere_tradotto

    # 4. LA QUERY ELASTICSEARCH CON "AND"
    query = {
        "size": 3,
        "query": {
            "match": {
                # ATTENZIONE: Assicurati che "genere_motore" sia il nome VERO 
                # della colonna su Elasticsearch (potrebbe essere "genere" o "Genre")
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
        
        # Estraiamo i dati utili dalla risposta complessa di Elasticsearch
        for hit in risposta['hits']['hits']:
            sorgente = hit['_source']
            risultati.append(sorgente)
            
        return risultati
    except Exception as e:
        print(f"Errore durante la ricerca: {e}")
        return []