const selenium = require("selenium-webdriver")
const [bld, par, sdK, clef, until] = [new selenium.Builder(), selenium.By, selenium.sendKeys , selenium.Key, selenium.until]
const fs= require('fs');


/* async function creerDriver(){
    
    return bld.forBrowser("MicrosoftEdge").build()
} */

function ouvrirPageHtml(driver){
    try {
            url = process.argv.slice(2)[0]
            //driver.get('https://opensea.io/collection/metroverse-genesis?search[sortAscending]=true&search[sortBy]=PRICE&search[toggles][0]=BUY_NOW')
            //driver.get('https://opensea.io/collection/metroverse-blackout?search[sortAscending]=true&search[sortBy]=PRICE&search[toggles][0]=BUY_NOW')
            driver.get(process.argv.slice(2)[0])
    } catch(err) {
            //console.log("erreur dans l'ouverture du driver et de la page: ", err)
            error = "erreur dans l'ouverture du driver et de la page: \n" + err 
    }
    //console.log('url', url)
    //console.log(process.argv.slice(2)[1])
}

async function etendreAffichageBlock(driver)
{ 
    //cacherFiltre = driver.findElement(par.xpath('//*[@id="main"]/div/div/div[3]/div/div/div/div[2]/div/div/header/button/div[2]'))
    try {
            //cacherFiltre = driver.findElement(par.xpath('//*[@id="main"]/div/div/div[3]/div/div/div/div[2]/div/div/header/button/div[2]'))                  //mauvais
            cacherFiltre = driver.findElement(par.xpath('//*[@id="main"]/div/div/div[5]/div/div[3]/div[1]/div/div/div/div/div[1]/div/button/span'))
            await cacherFiltre.click()
    } catch(err) {
            //console.log("erreur etendue de l'affichage: ", err)
            error = "erreur etendue de l'affichage: \n" + err 
    }

    //console.log("après filtre cacher")
    //display = driver.findElement(par.xpath('//*[@id="main"]/div/div/div[3]/div/div/div/div[3]/div[1]/div[2]/div[4]/div/button[2]/div'))

    /* display = driver.findElement(par.xpath('//*[@id="main"]/div/div/div[5]/div/div[3]/div[1]/div/div/div/div/div[4]/div/div/button[2]/div'))
    await display.click()
    console.log("avant augmenter display") */
}

async function selectionnerBlock(driver){
    //return await driver.findElements(par.className('Blockreact__Block-sc-1xf18x6-0 Assetreact__StyledContainer-sc-bnjqwy-0 elqhCm bwCDxg Asset--loaded'))
    try {
            //return await driver.findElements(par.className('Blockreact__Block-sc-1xf18x6-0 Assetreact__StyledContainer-sc-bnjqwy-0 elqhCm bwCDxg Asset--loaded'))        //mauvais
            return await driver.findElements(par.className('sc-1xf18x6-0 sc-bnjqwy-0 haVRLx floEcI Asset--loaded'))
            //sc-1xf18x6-0 sc-bnjqwy-0 hDbqle floEcI Asset--loaded                                                
    } catch(err) {
            //console.log("erreur selection et recherche blocs listés: ", err)
            error = "erreur selection et recherche blocs listés: \n" + err
    }
}


async function scrollDown(driver)
{
    try {
            pageBlock = driver.findElement(par.css("body"));
            await pageBlock.sendKeys(clef.PAGE_DOWN);
            await driver.sleep(2500);
            //await driver.wait(until.elementLocated(par.className('AssetCardFooter--name')))
            //await driver.wait(selectionnerBlock())
            await driver.wait(async function() {
                const readyState = await driver.executeScript('return document.readyState')
                return readyState === 'complete'
            });
        }
    catch (err) {
                error = "erreur de scrolling: \n" + err
        }
    
}

async function isBuyNow(block, driver)
{
    try {
            await driver.sleep(10);
            //buyNow = await block.findElements(par.className('Blockreact__Block-sc-1xf18x6-0 Textreact__Text-sc-1w94ul3-0 cKQpdV dsumKY'))   //mauvais
            await block.findElements(par.className('sc-1xf18x6-0 sc-1w94ul3-0 bRplOh crRCcg'))

            return true    
    }
    catch (err) {
            //num = await numeroBlock(block)
            //console.log(num)
            error = "erreur scrapping isBuyNow: \n" + err
            return false
    }
    
}

async function numeroBlock(block, driver)
{
    await driver.sleep(10);
    try {               
            //await block.findElement(par.className('AssetCardFooter')).getText().then(function (num)   //mauvais
            await block.findElement(par.className('AssetCardFooter--name')).getText().then(function (num) 
            {
                id = num.slice(7)
            });
        
            return id
    } catch(err) {
            //console.log("erreur scrapping numero bloc: ", err)
            error = "erreur scrapping numero bloc: \n" + err
    }
}

async function prixBlock(block, idBlock, driver)
{
    var prixBlk = -1
    await driver.sleep(10);
    //prix = block.findElement(par.className('Overflowreact__OverflowContainer-sc-7qr9y8-0 jPSCbX Price--amount'))
    try {
            //prix = block.findElement(par.className('Overflowreact__OverflowContainer-sc-7qr9y8-0 jPSCbX Price--amount'))   //mauvais
            prix = block.findElement(par.className('sc-7qr9y8-0 iUvoJs Price--amount'))
            if (blockListed[idBlock] == undefined)
            {
                await prix.getText().then(function (price) 
                {
                    //console.log(compteur++)
                    blockListed[idBlock] = price
                    prixBlk = price
                });
            }

            return prixBlk
    } catch(err) {
            error = "erreur scrapping prix bloc: \n" + err
            //console.log("erreur scrapping prix bloc: ", err)
    }
}

async function enregistrerInfosBlock(driver)
{
    continuer = true
    //await scrollDown()
    while (continuer)
    {
        await scrollDown(driver)
        await scrollDown(driver)
        blocks = await selectionnerBlock(driver)
        if (blocks.length == 0)
        {
            //console.log("Erreur scrapping: aucun bloc listé")
            error = "Erreur scrapping: aucun bloc listé scrappé"
            break
        }
        //console.log(blocks)
        continuer = false
        //console.log("Nombre de blocks listés: ", blocks.length)
        for (i = 0; i < blocks.length; i++)
        {
            if (await isBuyNow(blocks[i], driver))
            {
                //console.log("appel de num block")
                idBlock = await numeroBlock(blocks[i], driver)
                //console.log("appel de prix block")
                prixBloc = await prixBlock(blocks[i], idBlock, driver)
                if (prixBloc > 0)
                {
                    continuer = true
                }
                /* else if (prixBloc == -1) 
                {
                    break
                } */
            }
        }
       // console.log("bloc suivant")
    }
    if (error != 0)
    {
        console.log(error)
    }
}

//const driver = creerDriver()

compteur = 1
blockListed = {};
error = 0;

(async () => {
    let driver = await bld.forBrowser("firefox").build();
    try {
            // driver.manage().window().setSize(200,200);
            //await driver.manage().window().setRect({x:0, y:0, width:30000, height:100000})
            
            await driver.manage().window().maximize()

            //console.log("creerDriver")
            ouvrirPageHtml(driver)
            if (error != 0)
            {
                console.log(error)
            }

            //console.log("ouvrirPageHtml")
            await etendreAffichageBlock(driver);
            if (error != 0)
            {
                console.log(error)
            }            
            //console.log("etendreAffichageBlock")
            //const blocks = selectionnerBlock()
            //console.log("après selectionnerBlock")
            //blocks.then(console.log)
            await enregistrerInfosBlock(driver)
            //console.log(blockListed)
            //console.log(Object.keys(blockListed).length )

            if (blockListed.hasOwnProperty(''))
            {
                delete blockListed[""]
            }
            //console.log(blockListed)
            //console.log(Object.keys(blockListed).length)
            const data = JSON.stringify(blockListed);
            if (error == 0)
            {
                fs.writeFile(process.argv.slice(2)[1], data, (err) => 
                {
                        if (err) 
                                console.log('erreur dans le writefile', err);
                        else    console.log("JSON data is saved.");
                });
            }
        } finally {
             //await driver.quit();
        }
})()