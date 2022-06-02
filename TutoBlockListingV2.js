const selenium = require("selenium-webdriver")
const [bld, par, sdK, clef, until] = [new selenium.Builder(), selenium.By, selenium.sendKeys , selenium.Key, selenium.until]
const fs= require('fs');


async function creerDriver(){
    
    return bld.forBrowser("MicrosoftEdge").build()
}

function ouvrirPageHtml(){
    url = process.argv.slice(2)[0]
    //driver.get('https://opensea.io/collection/metroverse-genesis?search[sortAscending]=true&search[sortBy]=PRICE&search[toggles][0]=BUY_NOW')
    //driver.get('https://opensea.io/collection/metroverse-blackout?search[sortAscending]=true&search[sortBy]=PRICE&search[toggles][0]=BUY_NOW')
    driver.get(process.argv.slice(2)[0])
    //console.log('url', url)
    //console.log(process.argv.slice(2)[1])
}

async function etendreAffichageBlock()
{ 
    //cacherFiltre = driver.findElement(par.xpath('//*[@id="main"]/div/div/div[3]/div/div/div/div[2]/div/div/header/button/div[2]'))
    cacherFiltre = driver.findElement(par.xpath('//*[@id="main"]/div/div/div[5]/div/div[3]/div[1]/div/div/div/div/div[1]/div/button/span'))
    await cacherFiltre.click()
    //display = driver.findElement(par.xpath('//*[@id="main"]/div/div/div[3]/div/div/div/div[3]/div[1]/div[2]/div[4]/div/button[2]/div'))
    display = driver.findElement(par.xpath('//*[@id="main"]/div/div/div[5]/div/div[3]/div[1]/div/div/div/div/div[4]/div/div/button[2]/div'))
    await display.click()
    //console.log("après click")
}

async function selectionnerBlock(){
    //return await driver.findElements(par.className('Blockreact__Block-sc-1xf18x6-0 Assetreact__StyledContainer-sc-bnjqwy-0 elqhCm bwCDxg Asset--loaded'))
    return await driver.findElements(par.className('sc-1xf18x6-0 sc-bnjqwy-0 hDbqle floEcI Asset--loaded'))
}


async function scrollDown()
{
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

async function isBuyNow(block)
{
    try {
            await driver.sleep(10);
            //await block.findElements(par.className('Blockreact__Block-sc-1xf18x6-0 Textreact__Text-sc-1w94ul3-0 cKQpdV dsumKY'))
            await block.findElements(par.className('sc-1xf18x6-0 sc-1w94ul3-0 bRplOh crRCcg'))

            return true
    }
    catch (err) {
            //num = await numeroBlock(block)
            //console.log(num)
            return false
    }
    
}

async function numeroBlock(block)
{
    await driver.sleep(10);
    await block.findElement(par.className('AssetCardFooter--name')).getText().then(function (num) 
        {
            id = num.slice(7)
        });
    

    return id
}

async function prixBlock(block, idBlock)
{
    var prixBlk = -1
    await driver.sleep(10);
    //prix = block.findElement(par.className('Overflowreact__OverflowContainer-sc-7qr9y8-0 jPSCbX Price--amount'))
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
}

async function enregistrerInfosBlock()
{
    continuer = true
    //await scrollDown()
    while (continuer)
    {
        await scrollDown()
        await scrollDown()
        blocks = await selectionnerBlock()
        continuer = false
        //console.log(blocks.length)
        for (i = 0; i < blocks.length; i++)
        {
            if (await isBuyNow(blocks[i]))
            {
                //console.log("appel de num block")
                idBlock = await numeroBlock(blocks[i])
                //console.log("appel de prix block")
                if (await prixBlock(blocks[i], idBlock) > 0)
                {
                    continuer = true
                }
            }
        }
       // console.log("bloc suivant")
    }
}

//const driver = creerDriver()
let driver = bld.forBrowser("MicrosoftEdge").build();

compteur = 1
blockListed = {};

(async () => {
    try {
            // driver.manage().window().setSize(200,200);
            //await driver.manage().window().setRect({x:0, y:0, width:30000, height:100000})
            
            await driver.manage().window().maximize()

            //console.log("creerDriver")
            ouvrirPageHtml()
            //console.log("ouvrirPageHtml")
            await etendreAffichageBlock();
            //console.log("etendreAffichageBlock")
            //const blocks = selectionnerBlock()
            //console.log("après selectionnerBlock")
            //blocks.then(console.log)
            await enregistrerInfosBlock()
            //console.log(blockListed)
            //console.log(Object.keys(blockListed).length )
            if (blockListed.hasOwnProperty(''))
            {
                delete blockListed[""]
            }
            //console.log(blockListed)
            //console.log(Object.keys(blockListed).length)
            const data = JSON.stringify(blockListed);
            //fs.writeFile(process.argv.slice(2)[1], data, (err) => 
            fs.writeFile(process.argv.slice(2)[1], data, (err) => 
            {
                    if (err) 
                            console.log('erreur dans le writefile', err);
                    else    console.log("JSON data is saved.");
                });
        } finally {
             //await driver.quit();
        }
})()