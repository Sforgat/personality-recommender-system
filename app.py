import streamlit as st
import json
from logic.calcolo_ocean import calcola_punteggi
# Configurazione della pagina
st.set_page_config(page_title="Personality Recommender", page_icon="🧠", layout="centered")

# Funzione per caricare i dati del questionario
@st.cache_data # Mantiene in cache il file per non ricaricarlo ad ogni interazione
def carica_domande():
    with open("data/domande_20.json", "r", encoding="utf-8") as f:
    #with open("data/domande.json", "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    st.title("Scopri il tuo Profilo Psicologico")
    st.write("Compila il seguente test per permetterci di raccomandarti i migliori film, libri e programmi TV basati sulla tua vera personalità.")
    
    domande = carica_domande()
    
    # Opzioni temporanee in attesa di elaborare choices.ts
    opzioni = [
        "1 - Molto impreciso",
        "2 - Moderatamente impreciso",
        "3 - Né impreciso né preciso",
        "4 - Moderatamente preciso",
        "5 - Molto preciso"
    ]
    
    # Usiamo un form per raggruppare tutte le risposte
    with st.form(key="questionario_ipip"):
        st.subheader("Questionario IPIP-NEO")
        
        # Dizionario per memorizzare le risposte dell'utente
        risposte_utente = {}
        
        # Ciclo per generare l'interfaccia di ogni domanda
        for i, domanda in enumerate(domande):
            # Usiamo l'ID univoco della domanda come "key" per Streamlit
            risposta_selezionata = st.radio(
                label=f"{i+1}. {domanda['text']}",
                options=opzioni,
                index=2, # Imposta di default il valore neutro
                key=domanda['id'] 
            )
            risposte_utente[domanda['id']] = risposta_selezionata
            
            st.divider() # Linea di separazione grafica
            
        # Pulsante di invio
        submit_button = st.form_submit_button(label="Calcola Personalità")
        
    # Logica eseguita DOPO aver premuto il pulsante
    if submit_button:
        st.success("Test completato con successo!")
        st.write("Ecco i dati grezzi raccolti (pronti per essere inviati al motore di calcolo):")
        # Mostriamo i dati a schermo per scopi di debug
        st.json(risposte_utente)

        # Chiamiamo il motore di calcolo passando i dati
        risultati_ocean = calcola_punteggi(risposte_utente, domande)
        
        st.success("Test completato con successo!")
        st.subheader("I tuoi punteggi Big Five:")
        
        # Mostriamo i risultati in modo elegante con le colonne di Streamlit
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Apertura (O)", risultati_ocean['O'])
        col2.metric("Coscienz. (C)", risultati_ocean['C'])
        col3.metric("Estrovers. (E)", risultati_ocean['E'])
        col4.metric("Gradevol. (A)", risultati_ocean['A'])
        col5.metric("Nevrotic. (N)", risultati_ocean['N'])

        # Mostra anche un grafico a barre per visualizzare il profilo
        st.bar_chart(risultati_ocean)

if __name__ == "__main__":
    main()