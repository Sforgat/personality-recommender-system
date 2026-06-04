import streamlit as st
import json
import random
import math
import pandas as pd
import altair as alt
from logic.calcolo_ocean import calcola_punteggi
from logic.recommender import genera_raccomandazioni
from logic.database import ottieni_item_per_genere

# 1. Configurazione globale della pagina
st.set_page_config(page_title="Personality Recommender", page_icon="🧠", layout="wide")

NOMI_OCEAN = {
    'O': "Apertura all'Esperienza",
    'C': "Coscienziosità",
    'E': "Estroversione",
    'A': "Gradevolezza",
    'N': "Nevroticismo"
}

@st.cache_data
def carica_domande():
    try:
        with open("data/domande_20.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        with open("data/domande.json", "r", encoding="utf-8") as f:
            return json.load(f)

def main():
    # Inizializzazione degli stati della navigazione
    if "current_page" not in st.session_state:
        st.session_state.current_page = "onboarding"
    if "quiz_step" not in st.session_state:
        st.session_state.quiz_step = 1
    if "risposte_utente" not in st.session_state:
        st.session_state.risposte_utente = {}
    if "scelta_genere" not in st.session_state:
        st.session_state.scelta_genere = "Preferisco non specificare"
    if "dev_mode" not in st.session_state:
        st.session_state.dev_mode = False
        
    domande = carica_domande()
    total_domande = len(domande)
    
    DOMANDE_PER_PAGINA = 3
    total_pagine = math.ceil(total_domande / DOMANDE_PER_PAGINA)
    opzioni = ["1", "2", "3", "4", "5"]

    # FASE 1: ONBOARDING (Protetto dal CSS del Quiz)
    if st.session_state.current_page == "onboarding":
        _, col_central, _ = st.columns([1, 2, 1])
        with col_central:
            st.title("Scopri il tuo Profilo Psicologico")
            st.write("Compila il seguente test per permetterci di raccomandarti i migliori contenuti basati sulla tua personalità.")
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
                st.session_state.current_page = "quiz"
                st.session_state.quiz_step = 1
                st.rerun()

    # FASE 2: QUIZ A BLOCCHI (Il CSS si attiva solo ed esclusivamente qui)
    elif st.session_state.current_page == "quiz":
        # Iniettiamo il CSS solo in questa schermata per preservare l'Onboarding
        st.markdown("""
            <style>
            /* Card protetta per le domande */
            .question-box {
                background-color: #ffffff;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
                margin-top: 25px;
                margin-bottom: 15px;
                border-left: 5px solid #4A90E2;
            }
            .question-text {
                font-size: 18px;
                font-weight: 600;
                color: #1E293B;
                line-height: 1.4;
            }
            
            /* --- AZZERAMENTO E CENTRATURA DEL GRUPPO RADIO --- */
            div[data-testid="stRadioHorizontal"] {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                width: 100% !important;
            }
            div[role="radiogroup"] {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                gap: 35px !important;
                width: auto !important;
            }
            
            /* Nasconde completamente i numeri nativi 1, 2, 3, 4, 5 */
            div[role="radiogroup"] label [data-testid="stMarkdownContainer"] {
                display: none !important;
            }
            
            /* Disattiva il pallino rosso interno predefinito di Streamlit */
            div[role="radiogroup"] label > div:first-of-type div {
                display: none !important;
            }
            
            /* Proprietà comuni a tutti i cerchi personalizzati */
            div[role="radiogroup"] label > div:first-of-type {
                border-width: 2px !important;
                border-style: solid !important;
                background-color: transparent !important;
                transition: transform 0.2s ease, background-color 0.2s ease !important;
            }
            
            /* --- CONFIGURAZIONE SINGOLI BOTTONI (SCALA E COLORI) --- */
            
            /* BOTTONE 1: Massimo Accordo (Verde Acceso - Grande) */
            div[role="radiogroup"] label:nth-of-type(1) > div:first-of-type {
                transform: scale(2.2) !important;
                border-color: #10B981 !important;
            }
            div[role="radiogroup"] label:nth-of-type(1) input:checked + div {
                background-color: #10B981 !important;
            }
            
            /* BOTTONE 2: Accordo Parziale (Verde Pastello - Medio Grande) */
            div[role="radiogroup"] label:nth-of-type(2) > div:first-of-type {
                transform: scale(1.6) !important;
                border-color: #86EFAC !important;
            }
            div[role="radiogroup"] label:nth-of-type(2) input:checked + div {
                background-color: #86EFAC !important;
            }
            
            /* BOTTONE 3: Neutro (Grigio - Piccolo) */
            div[role="radiogroup"] label:nth-of-type(3) > div:first-of-type {
                transform: scale(1.1) !important;
                border-color: #94A3B8 !important;
            }
            div[role="radiogroup"] label:nth-of-type(3) input:checked + div {
                background-color: #94A3B8 !important;
            }
            
            /* BOTTONE 4: Disaccordo Parziale (Viola Pastello - Medio Grande) */
            div[role="radiogroup"] label:nth-of-type(4) > div:first-of-type {
                transform: scale(1.6) !important;
                border-color: #C084FC !important;
            }
            div[role="radiogroup"] label:nth-of-type(4) input:checked + div {
                background-color: #C084FC !important;
            }
            
            /* BOTTONE 5: Massimo Disaccordo (Viola Acceso - Grande) */
            div[role="radiogroup"] label:nth-of-type(5) > div:first-of-type {
                transform: scale(2.2) !important;
                border-color: #8B5CF6 !important;
            }
            div[role="radiogroup"] label:nth-of-type(5) input:checked + div {
                background-color: #8B5CF6 !important;
            }
            </style>
        """, unsafe_allow_html=True)

        _, col_central, _ = st.columns([1, 2, 1])
        with col_central:
            st.info("Modalità Sviluppatore attiva")
            if st.button("Compila tutto a caso", use_container_width=True):
                st.session_state.scelta_genere = random.choice(["Uomo", "Donna"])
                st.session_state.dev_mode = True
                for domanda in domande:
                    st.session_state.risposte_utente[domanda['id']] = random.choice(opzioni)
                st.session_state.current_page = "results"
                st.rerun()
            st.divider()

            st.title("Scopri il tuo Profilo Psicologico")
            quiz_page_idx = st.session_state.quiz_step - 1
            
            start_idx = quiz_page_idx * DOMANDE_PER_PAGINA
            end_idx = min(start_idx + DOMANDE_PER_PAGINA, total_domande)
            domande_pagina = domande[start_idx:end_idx]
            
            st.progress(quiz_page_idx / total_pagine)
            st.write(f"**Pagina {st.session_state.quiz_step} di {total_pagine}** (Domande {start_idx + 1} - {end_idx})")
            
            for i, domanda in enumerate(domande_pagina):
                global_idx = start_idx + i + 1
                
                st.markdown(f"""
                    <div class="question-box">
                        <div class="question-text">{global_idx}. {domanda['text']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                risposta_precedente = st.session_state.risposte_utente.get(domanda['id'], None)
                default_idx = opzioni.index(risposta_precedente) if risposta_precedente in opzioni else 2
                
                col_lbl1, col_radio, col_lbl2 = st.columns([2, 6, 2], vertical_alignment="center")
                with col_lbl1:
                    st.markdown("<p style='color:#10B981; font-weight:600; text-align:right; margin:0; font-size:16px; white-space:nowrap;'>D'accordo</p>", unsafe_allow_html=True)
                with col_radio:
                    st.session_state.risposte_utente[domanda['id']] = st.radio(
                        f"Scelta per {domanda['id']}",
                        options=opzioni,
                        index=default_idx,
                        key=f"radio_{domanda['id']}",
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                with col_lbl2:
                    st.markdown("<p style='color:#8B5CF6; font-weight:600; text-align:left; margin:0; font-size:16px; white-space:nowrap;'>In disaccordo</p>", unsafe_allow_html=True)
                st.write("") 
                
            st.markdown("---")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Indietro", use_container_width=True):
                    if st.session_state.quiz_step > 1:
                        st.session_state.quiz_step -= 1
                    else:
                        st.session_state.current_page = "onboarding"
                    st.rerun()
                        
            with col2:
                is_last_page = (st.session_state.quiz_step == total_pagine)
                label_bottone = "Calcola Personalità" if is_last_page else "Avanti"
                tipo_bottone = "primary" if is_last_page else "secondary"
                
                if st.button(label_bottone, type=tipo_bottone, use_container_width=True):
                    if not is_last_page:
                        st.session_state.quiz_step += 1
                    else:
                        st.session_state.current_page = "results"
                    st.rerun()

    # FASE 3: SCHERMATA RISULTATI
    elif st.session_state.current_page == "results":
        st.title("I Tuoi Risultati")
        
        risultati_ocean = calcola_punteggi(st.session_state.risposte_utente, domande)
        tratto_maggiore = max(risultati_ocean, key=risultati_ocean.get)
        
        st.subheader("Il tuo profilo psicologico completo:")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Apertura (O)", risultati_ocean['O'])
        col2.metric("Coscienz. (C)", risultati_ocean['C'])
        col3.metric("Estrovers. (E)", risultati_ocean['E'])
        col4.metric("Gradevol. (A)", risultati_ocean['A'])
        col5.metric("Nevrotic. (N)", risultati_ocean['N'])
        st.write("")

        dati_grafico = pd.DataFrame([
            {"Tratto": NOMI_OCEAN[k], "Punteggio": v, "Sigla": k}
            for k, v in risultati_ocean.items()
        ])
        
        istogramma_personalizzato = alt.Chart(dati_grafico).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("Tratto:N", axis=alt.Axis(labelAngle=0), title="Tratti di Personalità", sort=None),
            y=alt.Y("Punteggio:Q", title="Punteggio ottenuto"),
            color=alt.condition(
                alt.datum.Sigla == tratto_maggiore,
                alt.value("#10B981"),  
                alt.value("#4A90E2")   
            ),
            tooltip=["Tratto", "Punteggio"]
        ).properties(height=400) 
        
        st.altair_chart(istogramma_personalizzato, use_container_width=True)
        st.divider()

        col_actions1, col_actions2 = st.columns([1, 1])
        with col_actions1:
            if st.button("Ripeti il Test", use_container_width=True):
                st.session_state.current_page = "onboarding"
                st.session_state.risposte_utente = {}
                st.session_state.scelta_genere = "Preferisco non specificare"
                st.session_state.dev_mode = False
                st.rerun()
                
        with col_actions2:
            if st.button("Scopri le tue Raccomandazioni", type="primary", use_container_width=True):
                st.session_state.current_page = "recommendations"
                st.rerun()

    # FASE 4: SCHERMATA RACCOMANDAZIONI
    elif st.session_state.current_page == "recommendations":
        st.title("Le Tue Raccomandazioni")
        st.write("In base al tuo profilo psicologico calcolato, ecco i contenuti ideali suddivisi per genere affine:")
        
        mappa_genere = {"Preferisco non specificare": "all", "Uomo": "male", "Donna": "female"}
        genere_chiave = mappa_genere[st.session_state.scelta_genere]
        risultati_ocean = calcola_punteggi(st.session_state.risposte_utente, domande)
        
        motore_raccomandazione = genera_raccomandazioni(risultati_ocean, genere_chiave)
        
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

        st.divider()
        
        col_back1, col_back2 = st.columns([1, 1])
        with col_back1:
            if st.button("Torna ai tuoi Punteggi", use_container_width=True):
                st.session_state.current_page = "results"
                st.rerun()
        with col_back2:
            if st.button("Ripeti il Test", key="btn_reset_final", use_container_width=True):
                st.session_state.current_page = "onboarding"
                st.session_state.risposte_utente = {}
                st.session_state.scelta_genere = "Preferisco non specificare"
                st.session_state.dev_mode = False
                st.rerun()
                
        if st.session_state.get("dev_mode", False):
            st.write("")
            st.markdown("### [DEV MODE] Diagnostica Motore Raccomandazioni")
            match = motore_raccomandazione.get("match_esatti", [])
            if len(match) > 0:
                st.success("Affinità assolute (100% Match) individuate dal sistema:")
                for item in match:
                    st.write(f"- **{item}**")
            else:
                st.info("Nessun match esatto al 100% generato con i dati attuali.")

if __name__ == "__main__":
    main()