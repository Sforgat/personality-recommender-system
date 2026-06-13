import json
import random

def crea_mini_questionario():
    # 1. Carica il dataset completo
    with open("data/domande.json", "r", encoding="utf-8") as f:
        tutte_le_domande = json.load(f)

    domande_20 = []
    tratti_ocean = ['O', 'C', 'E', 'A', 'N']

    # 2. Estrai 4 domande bilanciate per ogni tratto
    for tratto in tratti_ocean:
        # Separa le positive dalle negative per questo specifico tratto
        domande_plus = [d for d in tutte_le_domande if d['domain'] == tratto and d['keyed'] == 'plus']
        domande_minus = [d for d in tutte_le_domande if d['domain'] == tratto and d['keyed'] == 'minus']
        
        # Prendi 2 positive e 2 negative (selezionate casualmente tra quelle disponibili)
        selezionate = random.sample(domande_plus, 2) + random.sample(domande_minus, 2)
        
        domande_20.extend(selezionate)

    # 3. Mescola l'ordine finale 
    random.shuffle(domande_20)

   
    with open("data/domande_20.json", "w", encoding="utf-8") as f:
        json.dump(domande_20, f, indent=4, ensure_ascii=False)

    print(f"Creato domande_20.json con {len(domande_20)} item perfettamente bilanciati.")

if __name__ == "__main__":
    crea_mini_questionario()