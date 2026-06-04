# logic/recommender.py
import math
from data.stereotipi import STEREOTIPI_GENERI


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
    REgole di associazione (Apriori) estratte dalla Sezione 4.2 dell'articolo.
    Ritorna una lista di "Match Assoluti".
    """
    raccomandazioni_forti = []
    
    # Rinominiamo le variabili per comodità di lettura e per ricalcare l'articolo
    O = profilo_norm['O'] # Openness (Apertura)
    C = profilo_norm['C'] # Conscientiousness (Coscienziosità)
    E = profilo_norm['E'] # Extraversion (Estroversione)
    A = profilo_norm['A'] # Agreeableness (Gradevolezza)
    N = profilo_norm['N'] # Neuroticism (Nevroticismo)

    # ==========================================
    # REGOLE DOMINIO: FILM (Movies)
    # ==========================================
    # "If a user with high OPE and EXT factors has high AGR, then she is likely to prefer comedy"
    if O >= 3.8 and E >= 3.5 and A >= 3.6:
        raccomandazioni_forti.append("Film: Comedy")
        
    # "...but if she has low NEU, she is likely to prefer horror movies."
    # "Horror movies are also preferred by people with high OPE, EXT, and AGR but low NEU."
    if O >= 3.8 and E >= 3.5 and A >= 3.5 and N <= 2.9:
        raccomandazioni_forti.append("Film: Horror")
        
    # "Additionally, cult movies tend to be liked by people with moderate CON and low AGR."
    if 3.0 <= C <= 3.3 and A <= 3.4:
        raccomandazioni_forti.append("Film: Cult")
        
    # Differenza di genere specificata per l'Animazione:
    # "animation genre, which is preferred by female users with low EXT and high NEU..."
    if genere_utente == "female" and E <= 3.2 and N >= 3.1:
        raccomandazioni_forti.append("Film: Animation")
    # "...and by male users with low CON and (much lower than female) NEU."
    if genere_utente == "male" and C <= 3.3 and N <= 2.6:
        raccomandazioni_forti.append("Film: Animation")

    # ==========================================
    # REGOLE DOMINIO: MUSICA
    # ==========================================
    # "people with high scores of OPE and EXT but low scores of NEU tend to like country music"
    if O >= 3.8 and E >= 3.6 and N <= 2.8:
        raccomandazioni_forti.append("Musica: Country")
        
    # "Jazz is liked by people with high EXT and AGR, and high CON or low NEU"
    if E >= 3.5 and A >= 3.5 and (C >= 3.6 or N <= 2.7):
        raccomandazioni_forti.append("Musica: Jazz")
        
    # "salsa is preferred by people with high scores of CON and EXT."
    if C >= 3.5 and E >= 3.7:
        raccomandazioni_forti.append("Musica: Salsa")
        
    # "reggae is preferred by people with high OPE and AGR"
    if O >= 3.9 and A >= 3.5:
        raccomandazioni_forti.append("Musica: Reggae")

    # Differenza di genere per R&B:
    if genere_utente == "female" and N >= 2.8 and O >= 3.8:
        raccomandazioni_forti.append("Musica: R&B")
    if genere_utente == "male" and C <= 3.4 and E >= 3.6:
        raccomandazioni_forti.append("Musica: R&B")

    # ==========================================
    # REGOLE DOMINIO: LIBRI
    # ==========================================
    # "people with high OPE and CON tend to like education books"
    if O >= 4.0 and C >= 3.6:
        raccomandazioni_forti.append("Libri: Educational")
        
    # "if CON is lower and OPE and AGR are high, people prefer science fiction books."
    if C <= 3.4 and O >= 4.1 and A >= 3.5:
        raccomandazioni_forti.append("Libri: Science Fiction")
        
    # Regole specifiche per genere (Libri):
    if genere_utente == "female" and N >= 3.0:
        raccomandazioni_forti.append("Libri: Crime")
        raccomandazioni_forti.append("Libri: Horror")
    if genere_utente == "male" and E >= 3.6:
        raccomandazioni_forti.append("Libri: Humor")

    # Per evitare duplicati (nel caso l'utente scatti due regole simili) usiamo set()
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