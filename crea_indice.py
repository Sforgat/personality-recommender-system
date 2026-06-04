import pandas as pd
from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import BulkIndexError
import logging
logging.basicConfig(level=logging.WARNING)
# Attiviamo la modalità "spia" (DEBUG) per vedere tutte le query verso Elasticsearch
logging.getLogger("elastic_transport.transport").setLevel(logging.DEBUG)

# 1. Connessione al database locale
es = Elasticsearch(
    "http://localhost:9200",
    request_timeout=60,
    max_retries=3,
    retry_on_timeout=True
)

def crea_indici():
    print("Pulizia e creazione indici in corso...")
    indici = ["catalogo_film", "catalogo_musica", "catalogo_libri"]
    
    for indice in indici:
        # Se l'indice esiste già, eliminalo
        if es.indices.exists(index=indice):
            es.indices.delete(index=indice)
            
        # Creiamo l'indice dicendogli: 0 repliche e NON ASPETTARE!
        es.indices.create(
            index=indice, 
            wait_for_active_shards="0",  # <--- Il comando che azzera i 30 secondi
            body={
                "settings": {
                    "number_of_replicas": 0
                }
            }
        )
    print("Indici vuoti creati")

def indicizza_film():
    print("Inizio indicizzazione Film...")
    df = pd.read_csv("data/IMDB-top-1000.csv")
    df = df.fillna("")
    azioni = []
    
    for _, row in df.iterrows():
        # L'IMDB ha i generi separati da virgola (es. "Action, Adventure, Sci-Fi"). 
        # Prendiamo il primo genere principale.
        genere_primario = str(row['Genre']).split(',')[0].strip()
        
        # Mappiamo il nome per combaciare con il nostro motore (es. "Film: Action")
        genere_formattato = f"Film: {genere_primario}"
        
        doc = {
            "_index": "catalogo_film",
            "_source": {
                "titolo": row['Movie Name'],
                "regista": row['Director'],
                "genere_motore": genere_formattato, # Quello che cercherà Streamlit
                "rating": float(row['IMDb Rating']) if pd.notna(row['IMDb Rating']) else 0.0,
            }
        }
        azioni.append(doc)
        
    try:
        # Usiamo .options() come richiesto dalla nuova versione, con ben 300 secondi di pazienza!
        helpers.bulk(es.options(request_timeout=300, max_retries=5), azioni, chunk_size=100)
        print(f"Inseriti {len(azioni)} item.")
    except BulkIndexError as e:
        print("ERRORE SUI DATI! Ecco i dettagli del primo documento fallito:")
        # Stampa i dettagli del primo errore riscontrato
        print(e.errors[0])
    except Exception as e:
        print(f"ERRORE DI RETE/TIMEOUT: {e}")
    

def indicizza_musica():
    print("Inizio indicizzazione Musica...")
    df = pd.read_csv("data/spotify-tracks-dataset.csv")
    df = df.fillna("")

    # Prendiamo solo le 100 canzoni più popolari per ogni genere (altrimenti sarebbero 114mila item da indicizzare, 
    # sbilanciato rispetto ai libri e ai film che sono 1000)
    df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce').fillna(0)
    # 2. Prima ordiniamo tutto l'elenco dal più famoso al meno famoso
    df = df.sort_values(by='popularity', ascending=False)
    
    # 3. IL TOCCO MAGICO: Raggruppiamo per genere e prendiamo solo i primi 100 per ogni categoria
    df = df.groupby('track_genre').head(50)

    azioni = []
    
    for _, row in df.iterrows():
        genere_grezzo = str(row['track_genre']).strip().title()
        genere_formattato = f"Musica: {genere_grezzo}"
        
        doc = {
            "_index": "catalogo_musica",
            "_source": {
                "titolo": row['track_name'],
                "artista": row['artists'],
                "genere_motore": genere_formattato,
                "popolarita": int(row['popularity']) if pd.notna(row['popularity']) else 0
            }
        }
        azioni.append(doc)
        
        # Inseriamo a blocchi di 10.000 per non saturare la RAM, dato che il file è grande
        if len(azioni) >= 10000:
            try:
                helpers.bulk(es.options(request_timeout=300, max_retries=5), azioni, chunk_size=100)
                print(f"Inseriti {len(azioni)} item musicali.")
            except BulkIndexError as e:
                print("ERRORE SUI DATI! Ecco i dettagli del primo documento fallito:")
                # Stampa i dettagli del primo errore riscontrato
                print(e.errors[0])
            except Exception as e:
                print(f"ERRORE DI RETE/TIMEOUT: {e}")
                azioni = []
            
    if azioni:
        try:
            helpers.bulk(es.options(request_timeout=300, max_retries=5), azioni, chunk_size=100)
            print(f"Inseriti {len(azioni)} item musicali.")
        except BulkIndexError as e:
            print("ERRORE SUI DATI! Ecco i dettagli del primo documento fallito:")
            # Stampa i dettagli del primo errore riscontrato
            print(e.errors[0])
        except Exception as e:
            print(f"ERRORE DI RETE/TIMEOUT: {e}")
    

def indicizza_libri():
    print("📚 Inizio indicizzazione Libri...")
    df = pd.read_csv("data/bookstoscrape.csv", encoding="latin-1")
    df = df.fillna("")
    
    # Mappa per convertire il testo in numeri veri
    mappa_voti = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    
    azioni = []
    
    for _, row in df.iterrows():
        genere_grezzo = str(row.get('Genre')).strip().title()
        genere_formattato = f"Libri: {genere_grezzo}"
        
        # Estraiamo la parola e la convertiamo in numero (se non la trova, mettiamo 0)
        voto_testo = str(row.get('Star Rating')).strip().title()
        voto_numerico = mappa_voti.get(voto_testo, 0)
        
        doc = {
            "_index": "catalogo_libri",
            "_source": {
                "titolo": row['Title'],
                "prezzo": str(row.get('Price')),
                "genere_motore": genere_formattato,
                "rating": voto_numerico  
            }
        }
        azioni.append(doc)
        
    try:
        helpers.bulk(es.options(request_timeout=300, max_retries=5), azioni, chunk_size=100)
        print(f"✅ Inseriti {len(azioni)} libri.")
    except BulkIndexError as e:
        print("🚨 ERRORE SUI DATI! Ecco i dettagli del primo documento fallito:")
        print(e.errors[0])
    except Exception as e:
        print(f"🚨 ERRORE DI RETE/TIMEOUT: {e}")
    

if __name__ == "__main__":
    crea_indici()
    try:
        indicizza_film()
    except Exception as e:
        print(f"Errore Film: {e}")
        
    try:
        indicizza_libri()
    except Exception as e:
        print(f"Errore Libri: {e}")
        
    try:
        indicizza_musica()
    except Exception as e:
        print(f"Errore Musica: {e}")
        
    print("Indicizzazione completata! Elasticsearch è pronto.")