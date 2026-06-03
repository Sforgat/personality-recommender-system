import streamlit as st
import json
import random
from logic.calcolo_ocean import calcola_punteggi
from logic.recommender import genera_raccomandazioni

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


    
    # === INIZIO AREA DI DEBUG (Da cancellare prima della consegna) ===
    st.info("🛠️ Modalità Sviluppatore attiva")
    if st.button("🎲 Compila tutto a caso"):
        # Selezioniamo casualmente "Uomo" o "Donna"
        st.session_state['scelta_genere_test'] = random.choice(["Uomo", "Donna"])
        
        # Assegniamo una risposta casuale (da 1 a 5) per ogni domanda del file JSON
        for domanda in domande:
            st.session_state[domanda['id']] = random.choice(opzioni)
            
    # === FINE AREA DI DEBUG ===


    # Usiamo un form per raggruppare tutte le risposte
    with st.form(key="questionario_ipip"):
        st.subheader("Dati Demografici")
        
        # Inseriamo la domanda sul genere
        scelta_genere = st.radio(
            "Identità di genere (opzionale, utilizzato per raffinare l'algoritmo):",
            options=["Preferisco non specificare", "Uomo", "Donna"],
            horizontal=True # Mette i bottoni in orizzontale per risparmiare spazio
        )
        
        st.divider()
        st.subheader("Questionario IPIP-NEO")
        risposte_utente = {}
        
        for i, domanda in enumerate(domande):
            risposta_selezionata = st.radio(
                label=f"{i+1}. {domanda['text']}",
                options=opzioni,
                index=2, 
                key=domanda['id'] 
            )
            risposte_utente[domanda['id']] = risposta_selezionata
            st.divider()
            
        submit_button = st.form_submit_button(label="Calcola Personalità e Raccomandazioni")
        
        

    # Logica eseguita DOPO aver premuto il pulsante
    if submit_button:
        #st.success("Test completato con successo!")
        #st.write("Ecco i dati grezzi raccolti (pronti per essere inviati al motore di calcolo):")
        # Mostriamo i dati a schermo per scopi di debug
        #st.json(risposte_utente)

        mappa_genere = {
            "Preferisco non specificare": "all",
            "Uomo": "male",
            "Donna": "female"
        }
        genere_chiave = mappa_genere[scelta_genere]

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

        st.divider()
        st.header("Le Tue Raccomandazioni")
        
       # 3. Passiamo al motore SIA il profilo CHE il genere chiave
        motore_raccomandazione = genera_raccomandazioni(risultati_ocean, genere_chiave)
        
        # 1. Mostriamo i match perfetti (Apriori) se ce ne sono
        match = motore_raccomandazione["match_esatti"]
        if len(match) > 0:
            st.success("🌟 Abbiamo trovato delle affinità assolute (Regole di Associazione):")
            for item in match:
                st.write(f"- **{item}**")
        else:
            st.info("Nessuna affinità assoluta trovata con le regole, ma abbiamo ordinato i generi in base al tuo profilo!")
            
        
        st.subheader("I generi più affini al tuo profilo")
        ranking = motore_raccomandazione["ranking_completo"]
        
        # 1. Filtriamo i risultati separandoli per dominio
        ranking_libri = [r for r in ranking if r["genere"].startswith("Libri:")]
        ranking_film = [r for r in ranking if r["genere"].startswith("Film:")]
        ranking_musica = [r for r in ranking if r["genere"].startswith("Musica:")]
        
        # 2. Creiamo le schede (Tabs) interattive di Streamlit
        tab_libri, tab_film, tab_musica = st.tabs(["📚 Libri", "🎬 Film", "🎵 Musica"])
        
        # 3. Popoliamo la scheda Libri
        with tab_libri:
            st.write("I 3 generi letterari perfetti per te:")
            for i in range(min(3, len(ranking_libri))):
                # Rimuoviamo il prefisso "Libri: " per una visualizzazione più pulita
                nome_pulito = ranking_libri[i]["genere"].replace("Libri: ", "")
                distanza = ranking_libri[i]["distanza"]
                st.write(f"{i+1}. **{nome_pulito}** (Distanza: {distanza:.2f})")
                
        # 4. Popoliamo la scheda Film
        with tab_film:
            st.write("I 3 generi cinematografici perfetti per te:")
            for i in range(min(3, len(ranking_film))):
                nome_pulito = ranking_film[i]["genere"].replace("Film: ", "")
                distanza = ranking_film[i]["distanza"]
                st.write(f"{i+1}. **{nome_pulito}** (Distanza: {distanza:.2f})")
                
        # 5. Popoliamo la scheda Musica
        with tab_musica:
            st.write("I 3 generi musicali perfetti per te:")
            for i in range(min(3, len(ranking_musica))):
                nome_pulito = ranking_musica[i]["genere"].replace("Musica: ", "")
                distanza = ranking_musica[i]["distanza"]
                st.write(f"{i+1}. **{nome_pulito}** (Distanza: {distanza:.2f})")



if __name__ == "__main__":
    main()