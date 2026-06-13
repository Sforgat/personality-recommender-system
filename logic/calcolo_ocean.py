def calcola_punteggi(risposte_utente, lista_domande):
    """
    Calcola i punteggi dei Big Five (OCEAN) basandosi sulle risposte dell'utente.
    Gestisce l'inversione dei punteggi per gli item con keyed='minus'.
    """
    # Inizializziamo i contatori a zero per i 5 tratti
    punteggi = {
        'O': 0, # Apertura (Openness)
        'C': 0, # Coscienziosità (Conscientiousness)
        'E': 0, # Estroversione (Extraversion)
        'A': 0, # Gradevolezza (Agreeableness)
        'N': 0  # Nevroticismo (Neuroticism)
    }

    # Trasformiamo la lista di domande in un dizionario per una ricerca più veloce
    mappa_domande = {d['id']: d for d in lista_domande}

    for id_domanda, risposta_stringa in risposte_utente.items():
        # Estraiamo il numero dalla stringa 
        valore_risposta = int(risposta_stringa.split(" - ")[0])
        
        # Recuperiamo i metadati della domanda dal nostro dataset
        domanda_info = mappa_domande[id_domanda]
        dominio = domanda_info['domain']
        segno = domanda_info['keyed']

        # Logica di calcolo IPIP
        if segno == 'plus':
            punteggi[dominio] += valore_risposta
        elif segno == 'minus':
            # Inversione matematica del punteggio per scala 1-5
            # 1 diventa 5, 2 diventa 4, 3 resta 3, 4 diventa 2, 5 diventa 1
            valore_invertito = 6 - valore_risposta
            punteggi[dominio] += valore_invertito

    return punteggi