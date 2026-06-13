# regole_domini.py

def calcola_regole_film(O, C, E, A, N, genere_utente):
    raccomandazioni = []
    
    # Regole valide per tutti gli utenti
    if 3.0 < C <= 3.25 and 2.55 <= A <= 2.87: raccomandazioni.append("Film: Cult")
    if 3.6 < O <= 3.80 and 3.35 < E <= 3.62 and 3.52 < A <= 3.85: raccomandazioni.append("Film: Comedy")
    if 3.8 < O <= 4.0 and 3.25 < C <= 3.5 and 3.2 < A <= 3.52 and 2.85 < N <= 3.17: raccomandazioni.append("Film: Horror")
    if 4.88 < O <= 5.0: raccomandazioni.append("Film: Tragedy")
    if 4.4 < O <= 4.6 and 3.62 < E <= 3.89: raccomandazioni.append("Film: Foreign")
    if 3.6 < O <= 3.8 and 3.62 < E <= 3.89 and 3.2 < A <= 3.52: raccomandazioni.append("Film: Horror")
    if 3.6 < O <= 3.8 and 3.62 < E <= 3.89 and 3.20 < A <= 3.52 and 2.53 < N <= 2.85: raccomandazioni.append("Film: Horror")
    if 3.6 < O <= 3.8 and 3.2 < A <= 3.52 and 2.53 < N <= 2.85: raccomandazioni.append("Film: Horror")
    if 3.8 < O <= 4.0 and 3.62 < E <= 3.89 and 3.52 < A <= 3.85: raccomandazioni.append("Film: Comedy")

    # Regole valide solo per donne 
    if genere_utente == "female":
        if 2.37 < E <= 2.75 and 3.7 < N <= 4.02: raccomandazioni.append("Film: Animation")
        if 3.8 < O <= 4.1 and 3.5 < E <= 3.87 and 2.4 < N <= 2.72: raccomandazioni.append("Film: Cartoon")
        if 3.67 < C <= 3.98 and 3.3 < A <= 3.6 and 2.72 < N <= 3.05: raccomandazioni.append("Film: Romance")

    # Regole valide solo per uomini 
    if genere_utente == "male":
        if 4.2 < E <= 4.6 and 1.79 < N <= 2.1: raccomandazioni.append("Film: Independent")
        if 4.6 < O <= 4.8 and 3.25 < C <= 3.6: raccomandazioni.append("Film: Neo-noir")
        if 3.25 < C <= 3.6 and 1.47 < N <= 1.79: raccomandazioni.append("Film: Animation")
        if 4.2 < O <= 4.4 and 3.25 < C <= 3.6 and 3.8 < E <= 4.2: raccomandazioni.append("Film: Animation")
        if 4.2 < O <= 4.4 and 3.6 < C <= 3.95 and 2.74 < N <= 3.058: raccomandazioni.append("Film: Drama")
        if 1.85 < C <= 2.2: raccomandazioni.append("Film: Cult")
        if 3.4 < O <= 3.6 and 3.8 < E <= 4.2: raccomandazioni.append("Film: War")
        if 4.65 < C <= 5.0 and 3.7 < A <= 4.05: raccomandazioni.append("Film: Independent")
        if 3.3 < E <= 3.4 and 2.10 < N <= 2.42: raccomandazioni.append("Film: Adventure")
        if 3.8 < O <= 4.0 and 3.3 < E <= 3.4 and 2.42 < N <= 2.74: raccomandazioni.append("Film: Comedy")
        if 4.2 < O <= 4.4 and 3.35 < A <= 3.7 and 1.786 < N <= 2.104: raccomandazioni.append("Film: Adventure")
        if 3.6 < C <= 3.9 and 3.3 < E <= 3.4 and 2.74 < N <= 3.06: raccomandazioni.append("Film: Drama")
        if 3.6 < O <= 3.8 and 3.4 < E <= 3.8 and 3.7 < A <= 4.05 and 2.42 < N <= 2.74: raccomandazioni.append("Film: Action")

    return raccomandazioni

def calcola_regole_musica(O, C, E, A, N, genere_utente):
    raccomandazioni = []
    
    # Regole valide per tutti gli utenti
    if 3.64 < C <= 3.76 and 3.635 < E <= 3.774 and 3.598 < A <= 3.731: raccomandazioni.append("Musica: Jazz")        
    if 3.75 < O <= 3.875 and 3.465 < A <= 3.598: raccomandazioni.append("Musica: Reggae")        
    if 3.64 < C <= 3.76 and 3.913 < E <= 4.052: raccomandazioni.append("Musica: Salsa")        
    if 3.625 < O <= 3.75 and 3.4 < C <= 3.52 and 3.496 < E <= 3.635: raccomandazioni.append("Musica: Country")        
    if 3.635 < E <= 3.774 and 3.598 < A <= 3.731 and 2.49 < N <= 2.61: raccomandazioni.append("Musica: Jazz")        
    if 3.218 < E <= 3.357 and 2.97 < N <= 3.09: raccomandazioni.append("Musica: Metal")        
    if 3.625 < O <= 3.75 and 3.496 < E <= 3.635 and 2.49 < N <= 2.61: raccomandazioni.append("Musica: Country")

    # Regole valide solo per donne 
    if genere_utente == "female":
        if 4.25 < O <= 4.375 and 3.42 < C <= 3.57: raccomandazioni.append("Musica: Classic")            
        if 3.625 < O <= 3.75 and 3.42 < C <= 3.57 and 3.4 < E <= 3.55: raccomandazioni.append("Musica: Country")            
        if 3.625 < O <= 3.75 and 3.42 < C <= 3.57 and 3.652 < A <= 3.789: raccomandazioni.append("Musica: Country")            
        if 3.375 < O <= 3.5 and 2.91 < N <= 3.058: raccomandazioni.append("Musica: R&B")

    # Regole valide solo per uomini 
    if genere_utente == "male":
        if 1.0 <= A <= 2.915: raccomandazioni.append("Musica: Rap")            
        if 3.35 < O <= 3.525 and 2.9 < C <= 3.05: raccomandazioni.append("Musica: Pop")            
        if 3.7 < O <= 3.875 and 3.35 < C <= 3.5 and 3.41 < A <= 3.575: raccomandazioni.append("Musica: Country")            
        if 3.2 < C <= 3.35 and 3.47 < E <= 3.625 and 2.618 < N <= 2.776: raccomandazioni.append("Musica: R&B")            
        if 2.9 < C <= 3.05 and 2.915 < A <= 3.08: raccomandazioni.append("Musica: Metal")            
        if 3.875 < O <= 4.05 and 2.915 < A <= 3.08: raccomandazioni.append("Musica: Metal")            
        if 3.35 < C <= 3.5 and 3.41 < A <= 3.575 and 2.144 < N <= 2.302: raccomandazioni.append("Musica: Country")
            
    return raccomandazioni

def calcola_regole_libri(O, C, E, A, N, genere_utente):
    raccomandazioni = []

    # Regole valide per tutti gli utenti
    if 4.09 < O <= 4.28 and 3.9 < C <= 4.07: raccomandazioni.append("Libri: Education")
    if 3.91 < O <= 4.09 and 3.375 < C <= 3.55: raccomandazioni.append("Libri: Science Fiction")
    if 1 < O <= 3.37: raccomandazioni.append("Libri: Classics")
    if 3.91 < O <= 4.09 and 3.5 < A <= 3.65: raccomandazioni.append("Libri: Science Fiction")

    # Regole valide solo per donne 
    if genere_utente == "female":
        if 3.4 < O <= 3.6 and 3.95 < A <= 4.3: raccomandazioni.append("Libri: Crime")
        if 3.8 < O <= 4.0 and 3.62 < E <= 3.9 and 3.0 < N <= 3.4: raccomandazioni.append("Libri: Horror")
        if 2.52 < E <= 2.8: raccomandazioni.append("Libri: Poetry")
        if 4.6 < O <= 4.8: raccomandazioni.append("Libri: Poetry")

    # Regole valide solo per uomini 
    if genere_utente == "male":
        if 3.52 < O <= 3.89 and 3.25 < A <= 3.55 and 2.04 < N <= 2.32: raccomandazioni.append("Libri: Humor")
        if 3.86 < E <= 4.16 and 2.04 < N <= 2.32: raccomandazioni.append("Libri: Humor")  
        if 3.52 < O <= 3.89 and 2.04 < N <= 2.32: raccomandazioni.append("Libri: Humor")
        
    return raccomandazioni