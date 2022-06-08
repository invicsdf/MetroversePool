import json
import sys
import copy
import itertools
import requests
from operator import itemgetter
from libMetroverse import lireBlocAVendre
from itertools import combinations

def scrappingPrixETHMET():
    url = "https://coinmarketcap.com/currencies/ethereum/"
    url2 = "https://coinmarketcap.com/fr/currencies/metroverse/"

    respMetro = requests.get(url)
    #print(respMetro.status_code)
    elementHtml = "<div class=\"priceValue \"><span>"
    deb = respMetro.text.find(elementHtml)
    portionHtmlETH = respMetro.text[deb : deb + 100]
    finMET = portionHtmlETH.find("</span>")
    debutMET = len(elementHtml) + 1
    prixETHStr = portionHtmlETH[debutMET : finMET]
    prixETHStr = prixETHStr.replace(",", "")
    prixETH = float(prixETHStr)

    respMetro = requests.get(url2)
    #print(respMetro.status_code)
    elementHtml = "<div class=\"priceValue \"><span>"
    deb = respMetro.text.find(elementHtml)
    portionHtmlMET = respMetro.text[deb : deb + 100]
    finETH = portionHtmlMET.find("</span></div>")
    debutETH = len(elementHtml) + 1
    prixMETStr = portionHtmlMET[debutETH : finETH]
    prixMET = float(prixMETStr)

    prixETHMET = prixMET / prixETH

    return prixETHMET

def lireCollection(nomJson):
    with open(nomJson) as json_data:
        donneeCollection = json.load(json_data)

    return donneeCollection

def lirePortefeuille(nomJson):
    return lireBlocAVendre(nomJson)

def lireBoost(nomJson):
    with open(nomJson) as json_data:
        donneeBoost = json.load(json_data)

    return donneeBoost


def completerBloc(donneeBloc):
    for k, v in donneeBloc.items():
        infoBloc = copy.copy(donneeCollection[k])
        infoBloc['prix'] = v
        donneeBloc[k] = infoBloc


def remplirNeiborhoodEtCalculScorePrix(donneePtf):
    score = 0
    prix = 0
    for info in donneePtf.values():
        buildingPtf = []
        flatListBoost = []
        ######### boucle lisant chaque bloc du portefeuille complété avec un boost de ceux qui sont listés. 
        # Le score d'un bloc du ptf est rajouté au score global de même pour le prix afin de connaître le score total et le prix total 
        # du ptf incluant un bloc listé test.
        score = score + int(info['score'])
        prix = prix + float(info['prix'])
        buildingPtf.append(info['commercial'])
        buildingPtf.append(info['industrial'])
        buildingPtf.append(info['public'])
        buildingPtf.append(info['residential'])
        #buildingPtf.append(info['ways'])
        flatListBoost = itertools.chain(*buildingPtf)
        for build in flatListBoost:
            k = listeBoost['index'][build]
            listeBoost['boost'][k][build] += 1

    return score, prix


def calculTaux(n, t):
    match n:
        case 0:
            return 0
        case 1:
            return 1 * t
        case 2:
            return 1.5 * t
        case 3:
            return 1.75 * t 
        case _:
            return 0       


def calculTauxGlobal():
    tauxGlobal = 0
    for k, v in listeBoost['boost'].items():
        pourcentage = v['baseBoost']
        if (k == "Railway" or k == "River"):
            nbreMinBoost = list(v.values())[0]
            tauxGlobal = tauxGlobal + calculTaux(nbreMinBoost//3, pourcentage)
            #print("railway")
        else:
            nbreMinBoost = min(min(list(v.values())[:3]), 3)
            tauxGlobal = tauxGlobal + calculTaux(nbreMinBoost, pourcentage)
            
    return tauxGlobal


def calculerGain(donneePtfCopie):
    (scoreInitial, prix) = remplirNeiborhoodEtCalculScorePrix(donneePtfCopie)
    tauxGlobal = calculTauxGlobal()
    gainGlobal = round((1 + tauxGlobal/100) * scoreInitial)

    return scoreInitial, tauxGlobal, gainGlobal, prix

def intervalleRechercheMeilleurBlock():
    actifGenesis = int(sys.argv[2])
    actifBlackout = int(sys.argv[3])
    """ actifGenesis = 1
    actifBlackout = 0 """
    if actifGenesis == 0 and actifBlackout == 1:
        borneInf = 10001
        borneSup = 20000
    else:
        borneInf = (actifGenesis * 10000 + actifBlackout * 10000) - (actifGenesis + actifBlackout) * 10000 + 1
        borneSup = (actifGenesis * 10000 + actifBlackout * 10000)

    return borneInf, borneSup

def meilleurPortefeuille():
    global listeBoost
    PrixETHMET = scrappingPrixETHMET()
    (borneInf, borneSup) = intervalleRechercheMeilleurBlock()
    #print(borneInf ,borneSup)
    nbBlock = int(sys.argv[4])
    #nbBlock = 5
    donneePtfMeilleurBlock = copy.copy(donneePortefeuille)
    meilleurKey = ()
    prixTotal = 0
    scoreTotal = 0
    gainTotal = []

    for i in range(1, nbBlock + 1):
        gain = []
        for k, v in donneeBlocAVendre.items():
            if borneInf <= int(k) <= borneSup:  
                donneePtfCopie = copy.copy(donneePtfMeilleurBlock)
                listeBoost  = copy.deepcopy(donneeBoost)
                donneePtfCopie[k] = v
                (scoreInitial, tauxGlobal, gainGlobal, prix) = calculerGain(donneePtfCopie)
                #####calcul de RoI
                #Le gainGlobal est le score total prenant en compte le tauxGlobal que donnent les boosts
                #La variable prix est calculée dans la fonction remplirNeiborhoodEtCalculScorePrix()
                RoI = prix/(PrixETHMET * 30.5 * gainGlobal)
                gain.append((k, v['prix'], v['score'], scoreInitial,  tauxGlobal, gainGlobal, round(RoI, 3)))
        gainSorted = sorted(gain, key = itemgetter(6))
        #print(gainSorted)
        meilleurKey = meilleurKey + (gainSorted[0][0],)
        prixTotal = prixTotal + float(gainSorted[0][1])
        scoreTotal = scoreTotal + float(gainSorted[0][2])
        scoreInitialFinal = gainSorted[0][3]
        tauxGlobalFinal = gainSorted[0][4]
        gainGlobalFinal = gainSorted[0][5]
        RoIFinal = gainSorted[0][6]

        donneePtfMeilleurBlock[meilleurKey[i - 1]] = donneeBlocAVendre[meilleurKey[i - 1]] 
        #print(donneePtfMeilleurBlock)

        del donneeBlocAVendre[meilleurKey[i - 1]]
    meilleurResultat = meilleurKey + (prixTotal, scoreTotal, scoreInitialFinal, tauxGlobalFinal, gainGlobalFinal, round(RoIFinal, 3))
    gainTotal.append(meilleurResultat)

    return gainTotal

def remplirHtml():
    nbBlock = 1
    html = "<table>\n"
    html += "<tr>\n"
    for i in range(1, int(sys.argv[4]) + 1):
    #for i in range(1, int(nbBlock) + 1):
        html += "<th>" + 'Bloc ' + str(i)  + "</th>\n"
    
    html += "<th>" + 'Prix total boosts' + "</th>\n"
    html += "<th>" + 'Score total boosts' + "</th>\n"
    html += "<th>" + 'Score initial total ptf' + "</th>\n"
    html += "<th>" + 'Taux total ptf' + "</th>\n"
    html += "<th>" + 'Score global ptf' + "</th>\n"
    html += "<th>" + 'RoI' + "</th>\n"
    html += "</tr>\n" 

    if int(sys.argv[5]) == 0:
        result = meilleurPortefeuille()
    else:
        result = resultatOptimisationComb()
    
    html += "<tr>\n"

    for i in range(0, int(sys.argv[4])):
    #for i in range(0, int(nbBlock)):
        html += "<td>" + result[0][i] + "</td>\n"

    
    html += "<td>" + str(result[0][int(sys.argv[4])]) + "</td>\n"
    html += "<td>" + str(result[0][int(sys.argv[4]) + 1]) + "</td>\n"
    html += "<td>" + str(result[0][int(sys.argv[4]) + 2]) + "</td>\n"
    html += "<td>" + str(result[0][int(sys.argv[4]) + 3]) + "</td>\n"
    html += "<td>" + str(result[0][int(sys.argv[4]) + 4]) + "</td>\n"
    html += "<td>" + str(result[0][int(sys.argv[4]) + 5]) + "</td>\n"
    html += "</tr>\n";   
    html += "</table>\n"

    return html
    
    """ html += "<td>" + str(result[0][int(nbBlock)]) + "</td>\n"
    html += "<td>" + str(result[0][int(nbBlock) + 1]) + "</td>\n"
    html += "<td>" + str(result[0][int(nbBlock) + 2]) + "</td>\n"
    html += "<td>" + str(result[0][int(nbBlock) + 3]) + "</td>\n"
    html += "<td>" + str(result[0][int(nbBlock) + 4]) + "</td>\n"
    html += "<td>" + str(result[0][int(nbBlock) + 5]) + "</td>\n" """
   
################################################   Calculs combinaisons plus justes     ########################################################
            
def listeCombinaison():
    nbBlock = int(sys.argv[4])
    listeTrie = []
    #nbBlock = 1
    (borneInf, borneSup) = intervalleRechercheMeilleurBlock()
    listeKey = list(donneeBlocAVendre.keys())
    for i in listeKey:
        if borneInf <= int(i) <= borneSup:   
            listeTrie.append(i)
    combinaison = list(combinations(listeTrie, nbBlock))

    return combinaison


def meilleurPtfCombinaison():
    PrixETHMET = scrappingPrixETHMET()
    global listeBoost
    combinaison = listeCombinaison()
    RoIMaxPrecedent = 100
    global iActuel
    iActuel = 0
    #print(len(combinaison))
    for i in range(0, len(combinaison)):
        """ if i % 100000 == 0:
            print(i) """
        donneePtfCopie = copy.copy(donneePortefeuille)
        listeBoost  = copy.deepcopy(donneeBoost)
        for j in combinaison[i]:
            donneePtfCopie[j] = donneeBlocAVendre[j]
        (scoreInitial, tauxGlobal, gainGlobal, prix) = calculerGain(donneePtfCopie)
        RoIActuel = prix/(PrixETHMET * 30.5 * gainGlobal)
        if RoIActuel < RoIMaxPrecedent:
            RoIMaxPrecedent = RoIActuel
            iActuel = i

    return RoIMaxPrecedent, combinaison[iActuel]


def resultatOptimisationComb():
    (RoIMaxPrecedent, tupleKey) = meilleurPtfCombinaison()
    gainTotalComb = []
    PrixETHMET = scrappingPrixETHMET()
    donneePtfCopie = copy.copy(donneePortefeuille)
    global listeBoost
    listeBoost  = copy.deepcopy(donneeBoost)
    prixTotalAchatBoost = 0
    scoreTotalAchatBoost = 0
    for i in tupleKey: 
        donneePtfCopie[i] = donneeBlocAVendre[i]
        prixTotalAchatBoost = prixTotalAchatBoost + float(donneeBlocAVendre[i]['prix'])
        scoreTotalAchatBoost = scoreTotalAchatBoost + float(donneeBlocAVendre[i]['score'])
    (scoreInitialTotal, tauxGlobalTotal, gainGlobalTotal, prixTotalPtf) = calculerGain(donneePtfCopie)  
    RoIFinal = prixTotalPtf/(PrixETHMET * 30.5 * gainGlobalTotal)
    #print(RoIActuel == RoIFinal)
    #print(RoIActuel)
    #print(RoIFinal)
    meilleurResultat = tupleKey + (prixTotalAchatBoost, scoreTotalAchatBoost, scoreInitialTotal,  tauxGlobalTotal, gainGlobalTotal, round(RoIFinal, 3))
    gainTotalComb.append(meilleurResultat)

    return gainTotalComb

##############################################################


####### Fichiers important pour le programme de calculs:
listeBoost          = {}
listeBoostComb      = {}
#donneeBlocAVendre   = lireBlocAVendre('blockListed.json')
donneeBlocAVendre   = lireBlocAVendre('fusionBlockListed.json')
## Fichier json incomplet ne contenant pas de ways pour les blackout:
donneeCollection    = lireCollection('fusionBoostCollection.json')
## Fichier json complet contenant tous les ways pour les blackout une fois le fichier correctionBuildingBD.js exécuté:
#donneeCollection    = lireCollection('boost_complet_genesis_blackout.json')
donneeBoost         = lireBoost('neighborhoodBoost.json')

contenuPtf = int(sys.argv[1])
if  contenuPtf == 0:
    donneePortefeuille  = {}
else:
    donneePortefeuille  = lirePortefeuille('ptfBlocMetroverse.json')

#donneePortefeuille  = {}
#donneePortefeuille  = lirePortefeuille('ptfBlocMetroverse.json')

completerBloc(donneeBlocAVendre)
completerBloc(donneePortefeuille)

print(remplirHtml())
##Avec PrixETHMET = 3.5378393381089585e-06
##Avec nombre total de blocs = 358


#print(resultatOptimisation())
#print(resultatOptimisationComb())
#Avec donneePortefeuille  = lirePortefeuille('ptfBlocMetroverse.json')
#Avec actifGenesis = 1, actifBlackout = 0
#nbreBlock = 1 
#nbreBlock = 2 
#nbreBlock = 3 
#nbreBlock = 4 
#nbreBlock = 5 

#Avec donneePortefeuille  = {}
#Avec actifGenesis = 1, actifBlackout = 0
#nbreBlock = 1 
#nbreBlock = 2 
#nbreBlock = 3 
#nbreBlock = 4 
#nbreBlock = 5 

#Avec donneePortefeuille  = lirePortefeuille('ptfBlocMetroverse.json')
#Avec actifGenesis = 0, actifBlackout = 1
#nbreBlock = 1 
#nbreBlock = 2 
#nbreBlock = 3 
#nbreBlock = 4 
#nbreBlock = 5 

#Avec donneePortefeuille  = {}
#Avec actifGenesis = 0, actifBlackout = 1
#nbreBlock = 1 
#nbreBlock = 2 
#nbreBlock = 3 
#nbreBlock = 4 
#nbreBlock = 5 

