const express = require('express');
const app = express();
const port = 3000;
//const cors = require('cors')
const fs= require('fs');

/* corsOptions = {
    //origin : "*"
    //optionsSuccessStatus : 200
} */
function scrappingBlockListedGenesis(){
    url = "https://opensea.io/collection/metroverse-genesis?search[sortAscending]=true&search[sortBy]=PRICE&search[toggles][0]=BUY_NOW"
    nomFichier = "blockListed_genesis_vf.json"
    var spawn = require("child_process").spawn;
	var process = spawn('node',["./TutoBlockListingV2.js", url, nomFichier]);
	p1 = new Promise((resolve, reject) => 
        {
            process.stdout.on('data', function(data) 
            {
		        console.log(data.toString())
                resolve(data.toString())
            })
	    })
}

function scrappingBlockListedBlackout(){
    url = "https://opensea.io/collection/metroverse-blackout?search[sortAscending]=true&search[sortBy]=PRICE&search[toggles][0]=BUY_NOW"
    nomFichier = "blockListed_blackout_vf.json"
    var spawn = require("child_process").spawn;
	var process = spawn('node',["./TutoBlockListingV2.js", url, nomFichier]);
	p2 = new Promise((resolve, reject) => 
        {
            process.stdout.on('data', function(data) 
            {
		        console.log(data.toString())
                resolve(data.toString())
            })
	    })
}

function fusionBlockListed()
{
    scrappingBlockListedGenesis()
    scrappingBlockListedBlackout()

    console.log('Promesse1', p1) 
    console.log('Promesse2', p2) 

    Promise.all([p1, p2]).then((results) => {
        console.log('Résultat', results)
        if (results[0] == "JSON data is saved.\n" && results[1] == "JSON data is saved.\n")
        {
            console.log('bien sauvegardés')
            const BlockListedGenesis = require('./blockListed_genesis_vf.json') 
            const BlockListedBlackout = require('./blockListed_blackout_vf.json') 
            fusionBlockListed= Object.assign({}, BlockListedGenesis, BlockListedBlackout);
            const data = JSON.stringify(fusionBlockListed);
            fs.writeFile('fusionBlockListed.json', data, (err) => 
            {
                if (err) 
                        console.log('erreur dans le writefile', err);
                else    console.log("JSON fusion data is saved.");
            });
        }
    }).catch((err) => console.log(err))
}

fusionBlockListed()

setInterval(function () 
{
    fusionBlockListed()
}, 300000)


app.get('/accueil', function(req,res)
{   
    fs.readFile('MetroversePool.html', 'utf8', (_err, data) => {
        res.send(data);
    });
})

//http://localhost:3000/resultat?ptf=0 ou 1&genesis=0 ou 1&blackout=0 ou 1&nbBlock=nbre
//http://localhost:3000/resultat?ptf=1&genesis=1&blackout=1&nbBlock=5

app.get('/resultat', function(req,res)
{   
    contenuPtf = req.query.ptf
    actifGenesis = req.query.genesis
    actifBlackout = req.query.blackout
    nbBlock = req.query.nbBlock
    methode = req.query.methode
    console.log(contenuPtf, actifGenesis, actifBlackout, nbBlock, methode)
    var spawn = require("child_process").spawn;
	var process = spawn('python3',["./calculs_blocks_metroverse_web.py",	contenuPtf, actifGenesis, actifBlackout, nbBlock, methode]);
	process.stdout.on('data', function(data) {
        console.log(data.toString())
		res.send(data.toString());
	})
})


app.use( (_req, res) => {
    res.send('Page introuvable')
  })
  
app.listen(port, () => 
  {
    console.log('Exemple de serveur en écoute a http://127.0.0.1:%d',port);
  })
