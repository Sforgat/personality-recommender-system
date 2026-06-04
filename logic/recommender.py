# logic/recommender.py
import math
from data.stereotipi import STEREOTIPI_GENERI
from logic.regole_domini import calcola_regole_film, calcola_regole_libri, calcola_regole_musica

def normalizza_profilo(profilo_grezzo, num_domande_per_tratto=4):
    profilo_norm = {}
    for tratto, valore in profilo_grezzo.items():
        profilo_norm[tratto] = valore / num_domande_per_tratto
    return profilo_norm

def calcola_distanza(profilo_utente, profilo_genere):
    distanza = math.sqrt(
        (profilo_utente['O'] - profilo_genere['O'])**2 +
        (profilo_utente['C'] - profilo_genere['C'])**2 +
        (profilo_utente['E'] - profilo_genere['E'])**2 +
        (profilo_utente['A'] - profilo_genere['A'])**2 +
        (profilo_utente['N'] - profilo_genere['N'])**2
    )
    return distanza

# AGGIUNTO IL PARAMETRO genere_selezionato
def approccio_euclideo(profilo_norm, genere_selezionato):
    risultati = []
    for genere_item, stereotipi_demografici in STEREOTIPI_GENERI.items():
        # Estraiamo il vettore corretto in base alla scelta dell'utente
        stereotipo_da_usare = stereotipi_demografici[genere_selezionato]
        
        dist = calcola_distanza(profilo_norm, stereotipo_da_usare)
        risultati.append({"genere": genere_item, "distanza": dist})
    
    return sorted(risultati, key=lambda x: x["distanza"])

def approccio_rule_based(profilo_norm, genere_utente):
    """
    Regole di associazione (Apriori) estratte dalla Sezione 4.2 dell'articolo.
    Ritorna una lista di "Match Assoluti" delegando la logica ai sottomoduli.
    """
    # Estraiamo le variabili per comodità
    O = profilo_norm['O']
    C = profilo_norm['C']
    E = profilo_norm['E']
    A = profilo_norm['A']
    N = profilo_norm['N']

    # Uniamo le liste restituite dalle tre funzioni
    raccomandazioni_forti = (
        calcola_regole_film(O, C, E, A, N, genere_utente) +
        calcola_regole_musica(O, C, E, A, N, genere_utente) +
        calcola_regole_libri(O, C, E, A, N, genere_utente)
    )

    # Per evitare duplicati usiamo set()
    return list(set(raccomandazioni_forti))


def genera_raccomandazioni(profilo_grezzo, genere_selezionato="all"):
    profilo_norm = normalizza_profilo(profilo_grezzo)
    ranking_euclideo = approccio_euclideo(profilo_norm, genere_selezionato)
    
    # ECCO LA RIGA MODIFICATA DA AGGIORNARE:
    match_apriori = approccio_rule_based(profilo_norm, genere_selezionato)
    
    return {
        "profilo_normalizzato": profilo_norm,
        "ranking_completo": ranking_euclideo,
        "match_esatti": match_apriori
    }