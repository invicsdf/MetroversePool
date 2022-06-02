import json
from os import remove
import sys
import copy
import itertools
from tkinter import N
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
    actifBlackout = 1 """
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
        
        donneePtfMeilleurBlock[meilleurKey[i - 1]] = donneeBlocAVendre[meilleurKey[i - 1]] 
        #print(donneePtfMeilleurBlock)

        del donneeBlocAVendre[meilleurKey[i - 1]]

    return donneePtfMeilleurBlock, meilleurKey, prixTotal, scoreTotal

def resultatOptimisation():
    gainTotal = []
    PrixETHMET = scrappingPrixETHMET()
    (donneePtfMeilleurBlock, meilleurKey, prixTotalAchatBoost, scoreTotalAchatBoost) = meilleurPortefeuille()
    (scoreInitialTotal, tauxGlobalTotal, gainGlobalTotal, prixTotalPtf) = calculerGain(donneePtfMeilleurBlock)
    RoIFinal = prixTotalPtf/(PrixETHMET * 30.5 * gainGlobalTotal)
    meilleurResultat = meilleurKey + (prixTotalAchatBoost, scoreTotalAchatBoost, scoreInitialTotal,  tauxGlobalTotal, gainGlobalTotal, round(RoIFinal, 3))
    gainTotal.append(meilleurResultat)

    return gainTotal

def remplirHtml():
    html = "<table>\n"
    html += "<tr>\n"
    for i in range(1, int(sys.argv[4]) + 1):
        html += "<th>" + 'Bloc ' + str(i)  + "</th>\n"
    
    html += "<th>" + 'Prix total boosts' + "</th>\n"
    html += "<th>" + 'Score total boosts' + "</th>\n"
    html += "<th>" + 'Score initial total ptf' + "</th>\n"
    html += "<th>" + 'Taux total ptf' + "</th>\n"
    html += "<th>" + 'Score global ptf' + "</th>\n"
    html += "<th>" + 'RoI' + "</th>\n"
    html += "</tr>\n" 

    result = resultatOptimisation()
    
    html += "<tr>\n"

    for i in range(0, int(sys.argv[4])):
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
################################################   Calculs combinaisons plus justes     ########################################################
            
def listeCombinaison():
    #nbreBlock = sys.argv[4]
    nbreBlock = 3
    (borneInf, borneSup) = intervalleRechercheMeilleurBlock()
    listeKey = list(donneeBlocAVendre.keys())
    for i in listeKey:
        if not borneInf <= int(i) <= borneSup:   
            listeKey.remove(i)
    combinaison = list(combinations(listeKey, nbreBlock))

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
        if i % 100000 == 0:
            print(i)
        donneePtfCopie = copy.copy(donneePortefeuille)
        listeBoost  = copy.deepcopy(donneeBoost)
        for j in combinaison[i]:
            donneePtfCopie[j] = donneeBlocAVendre[j]
        (scoreInitial, tauxGlobal, gainGlobal, prix) = calculerGain(donneePtfCopie)
        RoIActuel = prix/(PrixETHMET * 30.5 * gainGlobal)
        if RoIActuel < RoIMaxPrecedent:
            RoIMaxPrecedent = RoIActuel
            iActuel = i

    return RoIActuel, combinaison[iActuel]


def resultatOptimisationComb():
    (RoIActuel, tupleKey) = meilleurPtfCombinaison()
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


#print(resultatOptimisation())
#Avec donneePortefeuille  = lirePortefeuille('ptfBlocMetroverse.json')
#nbreBlock = 1 [('18527', 0.6213, 330.0, 2529, 26.25, 3193, 48.775)]
#nbreBlock = 2 [('18527', '16469', 0.9102999999999999, 627.0, 2826, 26.25, 3568, 44.545)]
#nbreBlock = 3 [('18527', '16469', '15661', 1.2092999999999998, 915.0, 3114, 26.25, 3931, 41.33)]
#nbreBlock = 4 [('18527', '16469', '15661', '16300', 1.4583, 1184.0, 3383, 26.25, 4271, 38.493)]
#nbreBlock = 5 [('18527', '16469', '15661', '16300', '19737', 1.7583, 1482.0, 3681, 26.25, 4647, 36.136)]

#Avec donneePortefeuille  = {}
#nbreBlock = 1 [('14817', 0.245, 282.0, 282, 0, 282, 10.28)]
#nbreBlock = 2 [('14817', '16300', 0.494, 551.0, 551, 0, 551, 10.634)]
#nbreBlock = 3 [('14817', '16300', '19907', 0.739, 814.0, 814, 5, 855, 10.252)]
#nbreBlock = 4 [('14817', '16300', '19907', '15304', 0.988, 1082.0, 1082, 7.5, 1163, 10.046)]
#nbreBlock = 5 [('14817', '16300', '19907', '15304', '15661', 1.287, 1370.0, 1370, 12.5, 1541, 9.876)]



#print(resultatOptimisationComb())
#Avec donneePortefeuille  = lirePortefeuille('ptfBlocMetroverse.json')
#nbreBlock = 1 [('18527', 0.6213, 330.0, 2529, 22.5, 3098, 50.271)]
#nbreBlock = 2 [('1946', '10194', 1.0, 647.0, 2846, 28.0, 3643, 43.625)]
#nbreBlock = 3 [('1946', '10194', '16469', 1.289, 944.0, 3143, 30.5, 4102, 39.57)]

#Avec donneePortefeuille  = {}
#nbreBlock = 1 [('14817', 0.245, 282.0, 282, 0, 282, 10.234)]
#nbreBlock = 2 [('16300', '19907', 0.494, 532.0, 532, 5, 559, 10.443)]
#nbreBlock = 3 [('14817', '16300', '19907', 0.739, 814.0, 814, 5, 855, 10.212)]



