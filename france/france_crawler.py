from selenium import webdriver
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.support.select import Select
import requests
import re
import pprint as pp
import logging


logging.basicConfig(filename = "logs.txt",level=logging.WARNING)

BASE_URL = "http://www2.assemblee-nationale.fr/recherche/questions"

LINKS_TABLE_FILE = "links_table.csv"
RESULTS_TABLE_FILE = "france_results_table.csv"
NTRIES = 10

def get_links(driver):
    table = driver.find_element_by_css_selector("#resultats-questions > table:nth-child(3)")
    table_html = table.get_attribute('outerHTML')
    soup = BeautifulSoup(table_html, 'html.parser')
    table = soup.find('table')

    # https://stackoverflow.com/questions/56757261/extract-href-using-pandas-read-html
    df  = pd.read_html(table_html)[0]
    # print(type(df))
    links = []
    for tr in table.findAll("tr"):
        trs = tr.findAll("td")
        for each in trs:
            try:
                link = each.find('a')['href']
                links.append(link)
            except:
                pass

    df['Link'] = links
    
    # print(df.columns)
    return df

def process_link(row):
    # print(row)
    
    url = row.Link
    intitule = row.Intitulé
    print(url)
    
    data = {}

    data["intitule"] = intitule

    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="lxml")

    ministere_interroge = soup.select("div.question_col50:nth-child(1)")
    ministere_interroge = str(ministere_interroge[0].contents[2]).strip()
    data['ministere_interroge'] = ministere_interroge

    ministere_attributaire = soup.select("div.question_col50:nth-child(2)")
    ministere_attributaire = str(ministere_attributaire[0].contents[2]).strip()
    data["ministere_attributaire"] = ministere_attributaire

    rubrique = soup.select("div.question_col33:nth-child(1) > p:nth-child(1)")
    rubrique = str(rubrique[0].contents[2]).strip()
    data["rubrique"] = rubrique

    titre = soup.select("div.question_col33:nth-child(2) > p:nth-child(1)")
    titre = str(titre[0].contents[1]).strip()
    data['titre'] = titre

    analyse = soup.select("div.question_col33:nth-child(3) > p:nth-child(1)")
    analyse = str(analyse[0].contents[2]).strip()
    data['analyse'] = analyse

    question_no = soup.select("div.question_big_content:nth-child(1)")
    question_no = str(question_no[0].contents[0]).strip()
    question_no = int(question_no.replace('Question N° ', ''))
    data["question_no"] = question_no
    
    question_mode = soup.select("div.question_big_content:nth-child(3)")
    question_mode = str(question_mode[0].contents[0]).strip()
    data["question_mode"] = question_mode

    asker = soup.select("#question_col80 > span:nth-child(1) > a:nth-child(1)")
    asker = str(asker[0].contents[0]).strip()
    data["asker"] = asker

    question_publiee = soup.select(".question_publish_date > div:nth-child(1) > span:nth-child(1)")
    question_publiee = str(question_publiee[0].contents[0]).strip()
    data["question_publiee"] = question_publiee
    
    try:
        question_retire = soup.select(".question_publish_date > div:nth-child(2) > span:nth-child(1)")
        question_retire = str(question_retire[0].contents[0]).strip()
        data["question_retire"] = question_retire
    except IndexError as e:
        data["question_retire"] = "NULL"

    if "fin de mandat" in str(r.text):
        data["fin_de_mandat"] = True
    else:
        data["fin_de_mandat"] = False
    
    data["url"] = url

    text_de_la_question = soup.select(".question > p:nth-child(2)")
    text_de_la_question = str(text_de_la_question[0].contents[0]).strip()
    text_de_la_question = text_de_la_question.replace('\n', ' ')
    text_de_la_question = text_de_la_question.replace('\t', ' ')
    text_de_la_question = re.sub(r'\s+', ' ', text_de_la_question)
    data["text_de_la_question"] = text_de_la_question

    try:
        texte_de_la_response = soup.select(".reponse_contenu")
        texte_de_la_response = str(texte_de_la_response[0].contents[0]).strip()
        texte_de_la_response = texte_de_la_response.replace("\n", ' ')
        texte_de_la_response = texte_de_la_response.replace("\t", ' ')
        texte_de_la_response = re.sub(r'\s+', ' ', texte_de_la_response)

        data["text_de_la_response"] = texte_de_la_response
    except Exception as e:
        data["text_de_la_response"] = "NULL"
    

    return data
    # print(rubrique)
    # print(url)

def process_links_table(links_table):
    results_list = list(links_table.apply(process_link, axis=1))
    results_dict = {x["question_no"]: x for x in results_list}
    
    # pp.pprint(results_dict)

    results_df = pd.DataFrame.from_dict(results_dict, orient = 'index')

    return results_df

# def make_list_of_allready_processed(filename = "france_results_table.csv") -> list:
#     results = pd.read_csv(filename, sep = '\t', header = False)
#     processed_question_nos = 


if __name__ == "__main__":
    links_table_cols = ['N°', 'Intitulé', 'Date', 'Link']
    with open("links_table_header.csv", 'wt') as f:
        f.write('\t'.join(links_table_cols))

    links_table = pd.DataFrame(columns=['N°', 'Intitulé', 'Date', 'Link'])

    results_table_cols = ['intitule', 'ministere_interroge', 'ministere_attributaire', 'rubrique',
       'titre', 'analyse', 'question_no', 'question_mode', 'asker',
       'question_publiee', 'question_retire', 'fin_de_mandat', 'url',
       'text_de_la_question', 'text_de_la_response']
    with open("results_table_header.csv", 'wt') as f:
        f.write('\t'.join(results_table_cols))


    results_table = pd.DataFrame(columns=results_table_cols)
        
    with webdriver.Firefox() as driver:
        driver.get(BASE_URL)

        ##legislature > option:nth-child(2)
        # Select(driver.find_element_by_css_selector("#legislature > option:nth-child(2)"))

        select = Select(driver.find_element_by_id('legislature'))
        select.select_by_value("14")

        search_btn = driver.find_element_by_css_selector('div.pull-right:nth-child(1) > p:nth-child(1) > button:nth-child(2)')
        search_btn.click()
        page = 1
        while True:
            for j in range(NTRIES):
                if j > 1:
                    print(f"Try {j}")
                    driver.refresh()
                    time.sleep(10)
                try:
                    links_subTable = get_links(driver)

                    results_df = process_links_table(links_subTable)
                    results_df.to_csv(RESULTS_TABLE_FILE, sep='\t', mode = 'a', header = False)
                    # print(results_df.columns)
                    # links_table = pd.concat([links_table, links_subTable])
                    links_subTable.to_csv(LINKS_TABLE_FILE, sep='\t', mode = 'a', header = False)
                    break
                except:
                    if j == NTRIES - 1:
                        logging.warning(f"Could not parse {driver.current_url} after {NTRIES} tries")
                    continue


            try:
                nextbutton = driver.find_element_by_link_text("Suivant »")
                
                nextbutton.click()

                page +=1
                print(page, end = '\n----------------------------------------------------\n')
            except Exception as e:
                print("Ending the loop because of exception")
                print(e)
                input()
                break
            

        # process_link(links_subTable.Link[1], links_subTable.Intitulé[1])