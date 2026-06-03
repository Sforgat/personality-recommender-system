import streamlit as st
import json
import math
from logic.calcolo_ocean import calcola_punteggi

# Configurazione della pagina
st.set_page_config(page_title="Personality Recommender", page_icon="🧠", layout="centered")

# Custom CSS iniettato per creare una "Card" elegante intorno alla domanda
st.markdown("""
    <style>
    .question-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        margin-top: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #4A90E2;
    }
    .question-text {
        font-size: 18px;
        font-weight: 600;
        color: #1E293B;
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

# Funzione per caricare i dati del questionario
@st.cache_data
def carica_domande():
    try:
        with open("data/domande_20.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        with open("data/domande.json", "r", encoding="utf-8") as f:
            return json.load(f)

def main():
    st.title("Scopri il tuo Profilo Psicologico")
    st.write("Compila il seguente test per permetterci di raccomandarti i migliori contenuti in base alla tua personalità.")
    
    # 1. INIZIALIZZAZIONE STATO (Sempre in cima!)
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0
    if "risposte_utente" not in st.session_state:
        st.session_state.risposte_utente = {}
        
    # 2. CARICAMENTO DATI
    domande = carica_domande()
    total_domande = len(domande)
    
    # Parametro: domande per pagina
    DOMANDE_PER_PAGINA = 3
    total_pagine = math.ceil(total_domande / DOMANDE_PER_PAGINA)
    
    opzioni = [
        "1 - Molto impreciso",
        "2 - Moderatamente impreciso",
        "3 - Né impreciso né preciso",
        "4 - Moderatamente preciso",
        "5 - Molto preciso"
    ]
    
    # 3. --- FLUSSO DEL QUESTIONARIO ---
    if st.session_state.current_page < total_pagine:
        page = st.session_state.current_page
        
        # Calcolo del range di domande da mostrare in questa pagina
        start_idx = page * DOMANDE_PER_PAGINA
        end_idx = min(start_idx + DOMANDE_PER_PAGINA, total_domande)
        domande_pagina = domande[start_idx:end_idx]
        
        # Barra di avanzamento basata sulle pagine
        progress_val = page / total_pagine
        st.progress(progress_val)
        st.write(f"**Pagina {page + 1} di {total_pagine}** (Domande {start_idx + 1} - {end_idx})")
        
        # Ciclo per renderizzare il blocco di domande della pagina corrente
        for domanda in domande_pagina:
            st.markdown(f"""
                <div class="question-box">
                    <div class="question-text">{domanda['text']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Recupera la risposta se l'utente torna indietro
            risposta_precedente = st.session_state.risposte_utente.get(domanda['id'], None)
            default_idx = opzioni.index(risposta_precedente) if risposta_precedente in opzioni else 2
            
            # Salviamo la selezione direttamente nel nostro dizionario di stato
            st.session_state.risposte_utente[domanda['id']] = st.radio(
                f"Scelta per {domanda['id']}",
                options=opzioni,
                index=default_idx,
                key=f"radio_{domanda['id']}",
                horizontal=True,
                label_visibility="collapsed"
            )
            st.write("") # Spazio di respiro tra una card e l'altra
            
        st.markdown("---")
        
        # Pulsanti di navigazione del blocco
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if page > 0:
                if st.button("Indietro", use_container_width=True):
                    st.session_state.current_page -= 1
                    st.rerun()
                    
        with col2:
            is_last_page = (page == total_pagine - 1)
            label_bottone = "Calcola Personalità" if is_last_page else "Avanti"
            tipo_bottone = "primary" if is_last_page else "secondary"
            
            if st.button(label_bottone, type=tipo_bottone, use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()

    # 4. --- SCHERMATA DEI RISULTATI ---
    else:
        st.balloons()
        st.success("Test completato con successo!")
        
        # Inviamo i dati accumulati al tuo motore di calcolo OCEAN
        risultati_ocean = calcola_punteggi(st.session_state.risposte_utente, domande)
        
        st.subheader("I tuoi punteggi Big Five:")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Apertura (O)", risultati_ocean['O'])
        col2.metric("Coscienz. (C)", risultati_ocean['C'])
        col3.metric("Estrovers. (E)", risultati_ocean['E'])
        col4.metric("Gradevol. (A)", risultati_ocean['A'])
        col5.metric("Nevrotic. (N)", risultati_ocean['N'])
        
        st.write("")
        st.subheader("Grafico del tuo Profilo")
        st.bar_chart(risultati_ocean)
        
        st.divider()
        
        if st.button("Ripeti il Test", use_container_width=True):
            st.session_state.current_page = 0
            st.session_state.risposte_utente = {}
            st.rerun()

if __name__ == "__main__":
    main()