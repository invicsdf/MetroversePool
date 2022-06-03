fusionBlockListed.json
fusionBoostCollection.json
neighborhoodBoost.json
ptfBlocMetroverse.json

libMetroverse.py
requirements.txt
package npm

Le repository contient:

- Un fichier principal qui est le serveur:

	A) \accueil  donne une page avec que l'interface (bouttons) pour filtrer. Une fois le boutton optimisé cliqué, 
		     en ajax (\resultat) un tableau apparaîtra avec le meilleur résultat et ses caractéristiques 
		     (temporaire donc à améliorer)

		1. http://localhost:3000/accueil
		2. http://localhost:3000/resultat?ptf=1&genesis=1&blackout=1&nbBlock=5
	B) Au lancement du serveur une recherche des blocs listés se fait automatiquement au départ et toutes les x temps (5 min dans le fichier)
	   Le temps peut être modifié à la ligne 73

- Un fichier de calculs:
	Les json utiles au fonctionnement du py de calculs sont:
		fusionBlockListed.json
		fusionBoostCollection.json
		neighborhoodBoost.json
		ptfBlocMetroverse.json
		libMetroverse.py



Comment faire les installations??:

	faire les commandes suivantes afin d'installer les librairies/modules:
		npm install
		pip install -r requirements.txt


Faire fonctionner l'interface:
	
	- lancer le node serveur: node .\serveur_metroKhaldoche.js
	- attendre la fin du scrapping pour avoir le fichier fusionBlockListed.json nécessaire à calculs_blocks_metroverse_web.py
	  (à noter qu'un fichier fusionBlockListed.json vieux de quelques jours est dans le github si jamais)
	- taper l'url http://localhost:3000/accueil dans le browser
	- choisir les filtres
	- un tableau avec le meilleur choix en "empilant" les meilleurs blocs chaque fois

