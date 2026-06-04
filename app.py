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
    # opzioni = ["1", "2", "3", "4", "5"]
    opzioni = ["5", "4", "3", "2", "1"] # cambiato ordine perchè in CSS si fa inversione

    # FASE 1: ONBOARDING
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

    # FASE 2: QUIZ A BLOCCHI
    elif st.session_state.current_page == "quiz":
        st.markdown("""
            <style>
            /* --- DOMANDA TRASPARENTE CON TESTO BIANCO --- */
            .question-box {
                background-color: transparent !important;
                padding: 10px 0px !important;
                border-radius: 0px !important;
                box-shadow: none !important;
                margin-top: 25px !important;
                margin-bottom: 5px !important;
                border-left: none !important;
            }
            .question-text {
                font-size: 17px !important;
                font-weight: 600 !important;
                color: #ffffff !important;
                line-height: 1.4;
            }
            
            /* --- CONTROLLO STRUTTURALE GRUPPO QUIZ A 5 BOTTONI --- */
            div[data-testid="stRadioHorizontal"]:has(label:nth-of-type(5)) {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                width: 100% !important;
            }
            div[data-testid="stRadioHorizontal"]:has(label:nth-of-type(5)) > label {
                display: none !important; 
            }
            
            /* --- CONTENITORE CENTRATO E SIMMETRICO --- */
            div[role="radiogroup"]:has(label:nth-of-type(5)) {
                display: flex !important;
                flex-wrap: nowrap !important;
                justify-content: center !important;
                align-items: center !important;
                gap: 24px !important;
                width: 100% !important;
                margin: 0 auto !important;
                height: 65px !important;
            }
            
            /* Iniezione dinamica del testo "In disaccordo" a sinistra (Inversione) */
            div[role="radiogroup"]:has(label:nth-of-type(5))::before {
                content: "In disaccordo" !important;
                color: #8B5CF6 !important;
                font-weight: 600 !important;
                font-size: 16px !important;
                white-space: nowrap !important;
                order: 0 !important;
            }
            
            /* Iniezione dinamica del testo "D'accordo" a destra (Inversione) */
            div[role="radiogroup"]:has(label:nth-of-type(5))::after {
                content: "D'accordo" !important;
                color: #10B981 !important;
                font-weight: 600 !important;
                font-size: 16px !important;
                white-space: nowrap !important;
                order: 6 !important;
            }
            
            /* ORDINAMENTO VISIVO INVERTITO: da Accordo (5) ad Disaccordo (1) */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(1) { order: 5 !important; } /* Verde Grande a destra */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(2) { order: 4 !important; } /* Verde Medio */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(3) { order: 3 !important; } /* Grigio Neutro al centro */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(4) { order: 2 !important; } /* Viola Medio */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(5) { order: 1 !important; } /* Viola Grande a sinistra */
            
            /* Box contenitori di ciascun cerchio */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label {
                margin: 0 !important;
                padding: 0 !important;
                width: 55px !important;
                height: 55px !important;
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                background-color: transparent !important;
                flex-shrink: 0 !important;
            }
            
            /* Reset etichette di testo native di Streamlit */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label [data-testid="stMarkdownContainer"] {
                display: none !important;
            }
            div[role="radiogroup"]:has(label:nth-of-type(5)) label > div:first-of-type div {
                display: none !important;
            }
            
            /* Stile base comune dei cerchi */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label > div:first-of-type {
                border-width: 3px !important;
                border-style: solid !important;
                background-color: transparent !important;
                margin: 0 !important;
                padding: 0 !important;
                box-sizing: border-box !important;
                transition: background-color 0.2s ease, border-color 0.2s ease !important;
            }
            
            /* --- DIMENSIONAMENTO DEI CERCHI --- */
            /* Opzione 1: Massimo Accordo (Verde Grande) */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(1) > div:first-of-type {
                width: 48px !important;
                height: 48px !important;
                border-color: #10B981 !important;
            }
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(1):has(input:checked) > div:first-of-type {
                background-color: #10B981 !important;
            }
            
            /* Opzione 2: Accordo Parziale (Verde Medio) */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(2) > div:first-of-type {
                width: 36px !important;
                height: 36px !important;
                border-color: #86EFAC !important;
            }
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(2):has(input:checked) > div:first-of-type {
                background-color: #86EFAC !important;
            }
            
            /* Opzione 3: Neutro (Grigio Piccolo) */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(3) > div:first-of-type {
                width: 24px !important;
                height: 24px !important;
                border-color: #94A3B8 !important;
            }
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(3):has(input:checked) > div:first-of-type {
                background-color: #94A3B8 !important;
            }
            
            /* Opzione 4: Disaccordo Parziale (Viola Medio) */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(4) > div:first-of-type {
                width: 36px !important;
                height: 36px !important;
                border-color: #C084FC !important;
            }
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(4):has(input:checked) > div:first-of-type {
                background-color: #C084FC !important;
            }
            
            /* Opzione 5: Massimo Disaccordo (Viola Grande) */
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(5) > div:first-of-type {
                width: 48px !important;
                height: 48px !important;
                border-color: #8B5CF6 !important;
            }
            div[role="radiogroup"]:has(label:nth-of-type(5)) label:nth-of-type(5):has(input:checked) > div:first-of-type {
                background-color: #8B5CF6 !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Contenitore centrale impostato a 3.0 per mantenere la griglia centrata
        _, col_central, _ = st.columns([0.5, 3.0, 0.5])
        with col_central:
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
                
                # I bottoni mantengono la logica nativa (1=Disaccordo, 5=Accordo), ma sono invertiti visivamente dal CSS
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

            st.divider()
            st.info("Modalità Sviluppatore attiva")
            if st.button("Compila tutto a caso", use_container_width=True):
                st.session_state.scelta_genere = random.choice(["Uomo", "Donna"])
                st.session_state.dev_mode = True
                for domanda in domande:
                    st.session_state.risposte_utente[domanda['id']] = random.choice(opzioni)
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
        
        # 2. Creiamo le schede (Tabs) interattive di Streamlit
        tab_libri, tab_film, tab_musica = st.tabs(["📚 Libri", "🎬 Film", "🎵 Musica"])
        
        # 3. Popoliamo la scheda Libri (DYNAMIC FILTERING + COLONNE)
        with tab_libri:
            cols_libri = st.columns(3) # Dichiariamo le 3 colonne orizzontali
            generi_mostrati = 0
            
            for item in ranking_libri:
                if generi_mostrati >= 3:
                    break 
                    
                genere_completo = item["genere"]
                nome_pulito = genere_completo.replace("Libri: ", "")
                distanza = item["distanza"]
                
                libri_consigliati = ottieni_item_per_genere("catalogo_libri", genere_completo, "rating")
                
                if libri_consigliati:
                    # Inseriamo il contenuto dinamicamente nella colonna corrispondente (0, 1, o 2)
                    with cols_libri[generi_mostrati]: 
                        st.markdown(f"### {generi_mostrati+1}. {nome_pulito}")
                        st.markdown(f"*(Distanza: {distanza:.2f})*")
                        for libro in libri_consigliati:
                            if "titolo" in libro:
                                prezzo = libro.get('prezzo', 'N/D')
                                rating = libro.get('rating', 'N/D')
                                st.info(f"**{libro['titolo']}**\n\n(Rating: {rating})")
                    generi_mostrati += 1 
                    
            if generi_mostrati == 0:
                st.warning("Nessun libro trovato per il tuo profilo.")
                
        # 4. Popoliamo la scheda Film (DYNAMIC FILTERING + COLONNE)
        with tab_film:
            cols_film = st.columns(3)
            generi_mostrati = 0 
            
            for item in ranking_film:
                if generi_mostrati >= 3:
                    break 
                    
                genere_completo = item["genere"]
                nome_pulito = genere_completo.replace("Film: ", "")
                distanza = item["distanza"]
                
                film_consigliati = ottieni_item_per_genere("catalogo_film", genere_completo, "rating")
                
                if film_consigliati:
                    with cols_film[generi_mostrati]:
                        st.markdown(f"### {generi_mostrati+1}. {nome_pulito}")
                        st.markdown(f"*(Distanza: {distanza:.2f})*")
                        for film in film_consigliati:
                            if "titolo" in film and "regista" in film:
                                st.info(f"**{film['titolo']}**\n\n(Regia: {film['regista']} - Voto: {film['rating']})")
                    generi_mostrati += 1 
                    
            if generi_mostrati == 0:
                st.warning("Nessun film trovato per il tuo profilo.")
                
        # 5. Popoliamo la scheda Musica (DYNAMIC FILTERING + COLONNE)
        with tab_musica:
            cols_musica = st.columns(3)
            generi_mostrati = 0
            
            for item in ranking_musica:
                if generi_mostrati >= 3:
                    break 
                    
                genere_completo = item["genere"]
                nome_pulito = genere_completo.replace("Musica: ", "")
                distanza = item["distanza"]
                
                brani_consigliati = ottieni_item_per_genere("catalogo_musica", genere_completo, "popolarita")
                
                if brani_consigliati:
                    with cols_musica[generi_mostrati]:
                        st.markdown(f"### {generi_mostrati+1}. {nome_pulito}")
                        st.markdown(f"*(Distanza: {distanza:.2f})*")
                        for brano in brani_consigliati:
                            if "titolo" in brano and "artista" in brano:
                                st.info(f"**{brano['titolo']}**\n\n(Di: {brano['artista']} - Popolarità: {brano['popolarita']})")
                    generi_mostrati += 1 
                    
            if generi_mostrati == 0:
                st.warning("Nessun brano trovato per il tuo profilo.")

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
            match = motore_raccomandazione.get("match_esatti", [])
            if len(match) > 0:
                st.success("Affinità assolute (100% Match) individuate dal sistema:")
                for item in match:
                    st.write(f"- **{item}**")
            else:
                st.info("Nessun match esatto generato con i dati attuali.")

if __name__ == "__main__":
    main()