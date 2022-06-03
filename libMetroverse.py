import json


import json

def lireBlocAVendre(nomJson):
    with open(nomJson) as json_data:
        donneeBlocAVendre = json.load(json_data)

    return donneeBlocAVendre