import streamlit as st
import json
import random
import math
import pandas as pd
import altair as alt
from logic.calcolo_ocean import calcola_punteggi
from logic.recommender import genera_raccomandazioni
from logic.database import ottieni_item_per_genere

# 1. Configurazione della pagina
st.set_page_config(page_title="Personality Recommender", page_icon="🧠", layout="centered")

# Custom CSS per le card delle domande
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

# Dizionario per mappare le sigle OCEAN ai nomi completi in italiano
NOMI_OCEAN = {
    'O': "Apertura all'Esperienza",
    'C': "Coscienziosità",
    'E': "Estroversione",
    'A': "Gradevolezza",
    'N': "Nevroticismo"
}

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
    # 2. INIZIALIZZAZIONE STATO
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0
    if "risposte_utente" not in st.session_state:
        st.session_state.risposte_utente = {}
    if "scelta_genere" not in st.session_state:
        st.session_state.scelta_genere = "Preferisco non specificare"
    if "dev_mode" not in st.session_state:
        st.session_state.dev_mode = False
        
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
    
    # === AREA DI DEBUG ===
    if st.session_state.current_page <= total_pagine:
        st.info("Modalità Sviluppatore attiva")
        if st.button("Compila tutto a caso", use_container_width=True):
            st.session_state.scelta_genere = random.choice(["Uomo", "Donna"])
            st.session_state.dev_mode = True
            for domanda in domande:
                st.session_state.risposte_utente[domanda['id']] = random.choice(opzioni)
            st.session_state.current_page = total_pagine + 1
            st.rerun()
        st.divider()

    # 3. --- FLUSSO DEL QUESTIONARIO ---
    
    # FASE A: Onboarding Genere (Pagina 0)
    if st.session_state.current_page == 0:
        st.title("Scopri il tuo Profilo Psicologico")
        st.write("Compila il seguente test per permetterci di raccomandarti i migliori film, libri e programmi TV basati sulla tua vera personalità.")
        st.subheader("Prima di iniziare:")
        opzioni_genere = ["Preferisco non specificare", "Uomo", "Donna"]
        def_genere_idx = opzioni_genere.index(st.session_state.scelta_genere)
        
        st.session_state.scelta_genere = st.radio(
            "Identità di genere:",
            options=opzioni_genere,
            index=def_genere_idx,
            horizontal=True
        )
        st.write("")
        
        if st.button("Inizia il Test", type="primary", use_container_width=True):
            st.session_state.current_page = 1
            st.rerun()

    # FASE B: Quiz a blocchi (Pagine da 1 a N)
    elif st.session_state.current_page <= total_pagine:
        st.title("Scopri il tuo Profilo Psicologico")
        quiz_page = st.session_state.current_page - 1
        
        start_idx = quiz_page * DOMANDE_PER_PAGINA
        end_idx = min(start_idx + DOMANDE_PER_PAGINA, total_domande)
        domande_pagina = domande[start_idx:end_idx]
        
        st.progress(quiz_page / total_pagine)
        st.write(f"**Pagina {quiz_page + 1} di {total_pagine}** (Domande {start_idx + 1} - {end_idx})")
        
        for i, domanda in enumerate(domande_pagina):
            global_idx = start_idx + i + 1
            
            st.markdown(f"""
                <div class="question-box">
                    <div class="question-text">{global_idx}. {domanda['text']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            risposta_precedente = st.session_state.risposte_utente.get(domanda['id'], None)
            default_idx = opzioni.index(risposta_precedente) if risposta_precedente in opzioni else 2
            
            st.session_state.risposte_utente[domanda['id']] = st.radio(
                f"Scelta per {domanda['id']}",
                options=opzioni,
                index=default_idx,
                key=f"radio_{domanda['id']}",
                horizontal=True,
                label_visibility="collapsed"
            )
            st.write("") 
            
        st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Indietro", use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
                    
        with col2:
            is_last_page = (quiz_page == total_pagine - 1)
            label_bottone = "Calcola Personalità" if is_last_page else "Avanti"
            tipo_bottone = "primary" if is_last_page else "secondary"
            
            if st.button(label_bottone, type=tipo_bottone, use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()

    # FASE C: Schermata dei Risultati Big Five (Pagina N + 1)
    elif st.session_state.current_page == total_pagine + 1:
        st.title("I Tuoi Risultati")
        
        # Calcolo dei punteggi
        risultati_ocean = calcola_punteggi(st.session_state.risposte_utente, domande)
        
        # Individuazione del tratto maggiore per l'evidenziazione grafica
        tratto_maggiore = max(risultati_ocean, key=risultati_ocean.get)
        
        st.subheader("Il tuo profilo psicologico completo:")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Apertura (O)", risultati_ocean['O'])
        col2.metric("Coscienz. (C)", risultati_ocean['C'])
        col3.metric("Estrovers. (E)", risultati_ocean['E'])
        col4.metric("Gradevol. (A)", risultati_ocean['A'])
        col5.metric("Nevrotic. (N)", risultati_ocean['N'])
        st.write("")

        # Convertiamo i dati in un DataFrame Pandas per Altair
        dati_grafico = pd.DataFrame([
            {"Tratto": NOMI_OCEAN[k], "Punteggio": v, "Sigla": k}
            for k, v in risultati_ocean.items()
        ])
        
        # Creazione del grafico con alt.condition (minuscolo!)
        istogramma_personalizzato = alt.Chart(dati_grafico).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("Tratto:N", axis=alt.Axis(labelAngle=0), title="Tratti di Personalità", sort=None),
            y=alt.Y("Punteggio:Q", title="Punteggio ottenuto"),
            color=alt.condition(  # <--- Corretto qui!
                alt.datum.Sigla == tratto_maggiore,
                alt.value("#10B981"),  # Verde Smeraldo per il tratto dominante
                alt.value("#4A90E2")   # Blu per tutti gli altri tratti
            ),
            tooltip=["Tratto", "Punteggio"]
        ).properties(height=350)
        
        st.altair_chart(istogramma_personalizzato, use_container_width=True)
        st.divider()

        # PULSANTI DI NAVIGAZIONE
        col_actions1, col_actions2 = st.columns([1, 1])
        with col_actions1:
            if st.button("Ripeti il Test", use_container_width=True):
                st.session_state.current_page = 0
                st.session_state.risposte_utente = {}
                st.session_state.scelta_genere = "Preferisco non specificare"
                st.session_state.dev_mode = False
                st.rerun()
                
        with col_actions2:
            if st.button("Scopri le tue Raccomandazioni", type="primary", use_container_width=True):
                st.session_state.current_page = total_pagine + 2
                st.rerun()

    # FASE D: Schermata Separata per le Raccomandazioni (Pagina N + 2)
    else:
        st.title("Le Tue Raccomandazioni")
        
        col_back1, col_back2 = st.columns([1, 1])
        with col_back1:
            if st.button("Torna ai tuoi Punteggi", use_container_width=True):
                st.session_state.current_page = total_pagine + 1
                st.rerun()
        with col_back2:
            if st.button("Ripeti il Test", key="btn_reset_final", use_container_width=True):
                st.session_state.current_page = 0
                st.session_state.risposte_utente = {}
                st.session_state.scelta_genere = "Preferisco non specificare"
                st.session_state.dev_mode = False
                st.rerun()
        
        st.divider()
        st.write("In base al tuo profilo psicologico calcolato, ecco i contenuti ideali suddivisi per genere affine:")
        
        mappa_genere = {"Preferisco non specificare": "all", "Uomo": "male", "Donna": "female"}
        genere_chiave = mappa_genere[st.session_state.scelta_genere]
        risultati_ocean = calcola_punteggi(st.session_state.risposte_utente, domande)
        
        motore_raccomandazione = genera_raccomandazioni(risultati_ocean, genere_chiave)
        
        if st.session_state.get("dev_mode", False):
            match = motore_raccomandazione["match_esatti"]
            if len(match) > 0:
                st.success("DEV MODE] Abbiamo trovato delle affinità assolute:")
                for item in match:
                    st.write(f"- **{item}**")
            st.write("")
            
        ranking = motore_raccomandazione["ranking_completo"]
        ranking_libri = [r for r in ranking if r["genere"].startswith("Libri:")]
        ranking_film = [r for r in ranking if r["genere"].startswith("Film:")]
        ranking_musica = [r for r in ranking if r["genere"].startswith("Musica:")]
        
        tab_libri, tab_film, tab_musica = st.tabs(["Libri", "Film", "Musica"])
        
        with tab_libri:
            cols_libri = st.columns(3)
            for i in range(min(3, len(ranking_libri))):
                with cols_libri[i]:
                    genere_completo = ranking_libri[i]["genere"]
                    nome_pulito = genere_completo.replace("Libri: ", "")
                    st.markdown(f"### {i+1}. {nome_pulito}")
                    
                    libri_consigliati = ottieni_item_per_genere("catalogo_libri", genere_completo, "rating")
                    if libri_consigliati:
                        for libro in libri_consigliati:
                            if "titolo" in libro:
                                rating = libro.get('rating', 'N/D')
                                st.info(f"**{libro['titolo']}**\n(Rating: {rating})")
                    else:
                        st.warning("Nessun libro trovato.")
                        
        with tab_film:
            cols_film = st.columns(3)
            for i in range(min(3, len(ranking_film))):
                with cols_film[i]:
                    genere_completo = ranking_film[i]["genere"]
                    nome_pulito = genere_completo.replace("Film: ", "")
                    st.markdown(f"### {i+1}. {nome_pulito}")
                    
                    film_consigliati = ottieni_item_per_genere("catalogo_film", genere_completo, "rating")
                    if film_consigliati:
                        for film in film_consigliati:
                            if "titolo" in film and "regista" in film:
                                st.info(f"**{film['titolo']}**\n(Regia: {film['regista']} - Voto: {film['rating']})")
                    else:
                        st.warning("Nessun film trovato.")
                        
        with tab_musica:
            cols_musica = st.columns(3)
            for i in range(min(3, len(ranking_musica))):
                with cols_musica[i]:
                    genere_completo = ranking_musica[i]["genere"]
                    nome_pulito = genere_completo.replace("Musica: ", "")
                    st.markdown(f"### {i+1}. {nome_pulito}")
                    
                    brani_consigliati = ottieni_item_per_genere("catalogo_musica", genere_completo, "popolarita")
                    if brani_consigliati:
                        for brano in brani_consigliati:
                            if "titolo" in brano and "artista" in brano:
                                st.info(f"**{brano['titolo']}**\n(Di: {brano['artista']})")
                    else:
                        st.warning("Nessun brano trovato.")

if __name__ == "__main__":
    main()