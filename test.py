import pandas as pd

# Sostituisci con il percorso del tuo file pulito
#df_musica = pd.read_csv("data/spotify-tracks-dataset.csv") 
df_musica = pd.read_csv("data/bookstoscrape.csv", encoding="latin1") 
# Stampa tutti i generi unici in ordine alfabetico
print(sorted(df_musica['Genre'].unique()))