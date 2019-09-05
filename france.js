const puppeteer = require('puppeteer');
// var cheerio = require('cheerio');
// var csv_obj = require("csv")
const Json2csvParser = require('json2csv').Parser;
const fs = require("fs")

var fields= ['question_no', 'questioner', 'Ministère interrogé', 'attributair', 'rubrique', 'titre', 'analyse', 'question_publiee', 'question_retiree', 'texte_question'];

var output_data= []
// output_data.push(header)

// var source_page =  "http://www2.assemblee-nationale.fr/recherche/questions"
async function clickandwait(page, selector){
    await Promise.all([
        page.click(selector),
        page.waitForNavigation({ waitUntil: 'networkidle0' }),
    ]);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

//https://stackoverflow.com/questions/47966510/how-to-fill-an-input-field-using-puppeteer 
(async () => {
    const browser = await puppeteer.launch({ headless: true });
    var page = await browser.newPage();

    console.log('load page')
    await page.goto("http://www2.assemblee-nationale.fr/recherche/questions", {waitUntil: 'networkidle2'});
    // await page.click('#legislature');
    // await page.click('#legislature > option:nth-child(2)');
    await page.select('#legislature', '14');
    // await page.click("div.pull-right:nth-child(1) > p:nth-child(1) > button:nth-child(2)", {waitUntil: 'networkidle2'});

    console.log("Search!")
    await clickandwait(page, "div.pull-right:nth-child(1) > p:nth-child(1) > button:nth-child(2)")
    // await sleep(500)
    console.log("first page loaded")

    first = true

    for (var j = 0; j < 4422; j++){

        var xpath_expr_str = "/html/body/div[3]/div/div/section/div/article/div/div/table/tbody/tr[*]/td[1]/a/@href"
        var url_elements = await page.$x(xpath_expr_str);
        console.log(url_elements);

        var url_list = [];
        for(var i = 0; i < url_elements.length; i++)
        {
            url_list.push(await page.evaluate(el => el.textContent, url_elements[i]));
        }

        for(var i = 0; i < url_list.length; i++){
            console.log(i + " : " + url)
            try {
                var url = url_list[i];
                const questionpage = await browser.newPage();
                await questionpage.goto(url)
                // await sleep(500)

                try{
                var question_no_element = await questionpage.$x('//*[@id="question_col10"]');
                // var question_no = await questionpage.evaluate(element => element.textContent, question_no_element);
                var question_no = await questionpage.evaluate(() => document.querySelector('#question_col10').textContent);
                var question_no = question_no.replace('Question N° ','');
                var question_no = question_no.trim();
                var question_no = parseInt(question_no)
                console.log(question_no);
                }
                catch(question_no_err){
                    var question_no = "unknown"
                    console.log(question_no_err)
                }

                try{
                var questioner = await questionpage.evaluate(() => document.querySelector('#question_col80 > span.question_big_content > a').textContent);
                }
                catch(questioner_err){
                    var questioner = "unknown"
                    console.log(questioner_err)
                }

                try{
                var questioned_minister = await questionpage.evaluate(() => document.querySelector("#contenu-page > div.contenu-principal.pleine-largeur.clearfix > div > section.question_info > div.ministere > div:nth-child(1)").textContent);
                var questioned_minister = questioned_minister.replace('Ministère interrogé >', '').trim()
                console.log(questioned_minister);
                }
                catch(questioned_minister_err){
                    var questioned_minister = "unknown"
                    console.log(questioned_minister_err)
                }

                try{
                var attributair = await questionpage.evaluate(() => document.querySelector('#contenu-page > div.contenu-principal.pleine-largeur.clearfix > div > section.question_info > div.ministere > div.question_col50.no-left-border').textContent);
                var attributair = attributair.replace('Ministère attributaire > ', '').trim()
                console.log(attributair)
                }
                catch(attributair_err){
                    var attributair = "unknown"
                    console.log(attributair_err)
                }
                
                try{
                var rubrique = await questionpage.evaluate(() => document.querySelector('#contenu-page > div.contenu-principal.pleine-largeur.clearfix > div > section.question_info > div.analyse_header > div:nth-child(1) > p').textContent);
                var rubrique = rubrique.replace('Rubrique >', '').trim()
                '#contenu-page > div.contenu-principal.pleine-largeur.clearfix > div > section.question_info > div.analyse_header > div:nth-child(1) > p'
                console.log(rubrique)
                }
                catch (rubrique_err){
                    var rubrique  = "unknown"
                    console.log(rubrique_err)
                }

                try{
                var titre = await questionpage.evaluate(() => document.querySelector('#contenu-page > div.contenu-principal.pleine-largeur.clearfix > div > section.question_info > div.analyse_header > div.question_col33.middle33 > p').textContent);
                var titre = titre.replace('Titre > ','').trim()
                console.log(titre)
                }
                catch (titre_err){
                    var titre = "unknown"
                    console.log(titre_err)
                }

                try{
                var analyse = await questionpage.evaluate(() => document.querySelector("#contenu-page > div.contenu-principal.pleine-largeur.clearfix > div > section.question_info > div.analyse_header > div.question_col33.last33 > p").textContent);
                var analyse = analyse.replace('Analyse >','').trim()
                console.log(analyse)
                }
                catch(analyse_err){
                    var analyse = "unknown"
                    console.log(analyse_err)
                }
                
                try{
                var question_publiee = await questionpage.evaluate(() => document.querySelector("#contenu-page > div.contenu-principal.pleine-largeur.clearfix > div > div > div:nth-child(1) > span").textContent);
                var question_publiee = question_publiee.trim()
                }
                catch(question_publiee_err){
                    var question_publiee = "unknown"
                    console.log(question_publiee_err)
                }
                
                try{
                var question_retiree = await questionpage.evaluate(() => document.querySelector("#contenu-page > div.contenu-principal.pleine-largeur.clearfix > div > div > div:nth-child(2) > span:nth-child(1)").textContent);
                var question_retiree = question_retiree.trim()
                console.log(question_retiree)
                }
                catch(question_retiree_err){
                    var question_retiree = "unknown"
                    console.log(question_retiree_err)
                }

                try{
                    var texte_question = await questionpage.evaluate(() => document.querySelector("#contenu-page > div.contenu-principal.pleine-largeur.clearfix > div > section.question_answer > div.question > p").textContent);
                    var texte_question = texte_question.replace(/(\n|\r)+$/, '').trim()                    
                }
                catch(texte_question_err){
                    var texte_question = "unknown"
                    console.log(texte_question_err)
                }


                "#contenu-page > div.contenu-principal.pleine-largeur.clearfix > div > div > div:nth-child(1) > span"
                data_element = {'question_no' : question_no, 
                                'questioner' : questioner, 
                                'Ministère interrogé' : questioned_minister, 
                                'attributair' : attributair, 
                                'rubrique' : rubrique, 
                                'titre' : titre, 
                                'analyse' : analyse, 
                                'question_publiee': question_publiee, 
                                'question_retiree' : question_retiree, 
                                'texte_question': texte_question};
                datalist = [question_no, questioner, questioned_minister, attributair, rubrique, titre, analyse, question_publiee, question_retiree, texte_question]
                output_data.push(data_element)

                // console.log(questioner)
                questionpage.close();
            }
            catch(err){
                console.log("sth went wrong:" + i + '-' + j)
            }

        }
    outfile = 'csv_files/' + j + '.csv'
    const json2csvParser = await new Json2csvParser({ fields, delimiter: '\t'  });
    const result = await json2csvParser.parse(output_data);

    console.log(result);
    await fs.writeFile(outfile, [result], "utf8", function (err) {
        if (err) {
            console.log('Some error occured - file either not saved or corrupted file saved.');
            sleep(5000)
        } else{
            console.log('It\'s saved!');
        }
    });

    output_data = []


    li_elements = await page.$x('//*[@id="resultats-questions"]/div[1]/ul/li[*]/a/@href'); /// a/@href    /a/@href
    suivant = await li_elements[li_elements.length - 1]
    next_url = await page.evaluate(el => el.textContent, suivant);
    next_url = await 'http://www2.assemblee-nationale.fr/' + next_url
    console.log(next_url);
    await page.close();
    page = await browser.newPage();
    await page.goto(next_url, {waitUntil: 'networkidle2'});

    // await sleep(1000)
    }
    "#resultats-questions > div:nth-child(2) > ul > li:nth-child(9) > a"


    console.log("close");
    await browser.close();

    const json2csvParser = new Json2csvParser({ fields, delimiter: '\t'  });
    const result = json2csvParser.parse(output_data);

    console.log(result);
    fs.writeFile("test.csv", [result], "utf8", function (err) {
        if (err) {
            console.log('Some error occured - file either not saved or corrupted file saved.');
        } else{
            console.log('It\'s saved!');
        }
    });
})();