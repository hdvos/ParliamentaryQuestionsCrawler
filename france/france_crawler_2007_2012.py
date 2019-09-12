from selenium import webdriver
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.support.select import Select
import requests
import re
import pprint as pp
import logging


logging.basicConfig(filename = "logs_2007_2012.txt",level=logging.WARNING)

BASE_URL = "http://www2.assemblee-nationale.fr/recherche/questions"

LINKS_TABLE_FILE = "links_table_2007_2012.csv"
RESULTS_TABLE_FILE = "france_results_table_2007_2012.csv"
NTRIES = 10     # If connection fails. How many tries to reconnect before aborting.

def get_links(driver) -> pd.DataFrame:
    """Extract all links to questions from the data frame.
    
    :param driver: A driver object with a page containing a table with links.
    :type driver: webdriver.Firefox()
    :return: A pandas data frame containing the links.
    :rtype: pd.DataFrame
    """

    table = driver.find_element_by_css_selector("#resultats-questions > table:nth-child(3)")
    table_html = table.get_attribute('outerHTML')
    soup = BeautifulSoup(table_html, 'html.parser')
    table = soup.find('table')

    # code adapted from: https://stackoverflow.com/questions/56757261/extract-href-using-pandas-read-html
    df  = pd.read_html(table_html)[0]
    
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
    
    return df

def process_link(row:pd.Series) -> dict:
    """Gets the desired info from a page containing a question.
    
    :param row: A row from the links dataframe as created in get_links()
    :type row: pd.Series
    :return: A dictionary with all the extracted information.
    :rtype: dict
    """
    
    url = row.Link
    intitule = row.Intitulé     # Some kind of summary. I keep it just in case it might turn out relevant.
    print(url)
    data = {}

    data["intitule"] = intitule

    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="lxml")
    # print(soup)

    table = soup.findAll("table")
    # print(table[0].contents)
    # input()
    table = table[0].contents

    ministere_interroge = str(table[5].contents[1].contents[1].contents[0]).strip()
    data['ministere_interroge'] = ministere_interroge
    

    ministere_attributaire = str(table[6].contents[1].contents[1].contents[0]).strip()
    data["ministere_attributaire"] = ministere_attributaire
    
    rubrique = str(table[24].contents[1].contents[1].contents[1].contents[0]).strip()
    # rubrique = str(rubrique[0].contents[2]).strip()
    data["rubrique"] = rubrique


    titre = ''
    data['titre'] = titre

    tete_de_analyse = str(table[24].contents[2].contents[1].contents[1].contents[0]).strip()

    body_analyse =  str(table[24].contents[3].contents[1].contents[1].contents[0]).strip()

    analyse = f'{tete_de_analyse} - {body_analyse}'

    data['analyse'] = analyse


    question_no = str(table[1].contents[0].contents[1].contents[1].contents[0]).strip()
    question_no = int(question_no)
    data["question_no"] = question_no
    
    question_mode = ''
    data["question_mode"] = question_mode

    
    asker = str(table[1].contents[2].contents[1].contents[-2].contents[0]).strip()
    data["asker"] = asker

    question_publiee = str(table[8].contents[1].contents[1].contents[0].contents[0]).strip()
    data["question_publiee"] = question_publiee
    
    try:
        question_retire = str(table[3].contents[0].contents[3].contents[0]).strip()
        data["question_retire"] = question_retire
    except IndexError as e:     # Sometimes there is no response available.
        input(IndexError)
        data["question_retire"] = "NULL"

    if "fin de mandat" in str(r.text):      # Don't know what this is, but in case it might turn out relevant I keep it.
        data["fin_de_mandat"] = True
    else:
        data["fin_de_mandat"] = False
    
    data["url"] = url

    # text_de_la_question = soup.select(".question > p:nth-child(2)")
    # text_de_la_question = str(text_de_la_question[0].contents[0]).strip()
    # text_de_la_question = text_de_la_question.replace('\n', ' ')
    # text_de_la_question = text_de_la_question.replace('\t', ' ')
    # text_de_la_question = re.sub(r'\s+', ' ', text_de_la_question)
    # data["text_de_la_question"] = text_de_la_question

    # try:
    #     texte_de_la_response = soup.select(".reponse_contenu")
    #     texte_de_la_response = str(texte_de_la_response[0].contents[0]).strip()
    #     texte_de_la_response = texte_de_la_response.replace("\n", ' ')
    #     texte_de_la_response = texte_de_la_response.replace("\t", ' ')
    #     texte_de_la_response = re.sub(r'\s+', ' ', texte_de_la_response)

    #     data["text_de_la_response"] = texte_de_la_response
    # except Exception as e: # Sometimes there is not answer available.
    #     data["text_de_la_response"] = "NULL"
    
    # return data
    

def process_links_table(links_table:pd.DataFrame) -> pd.DataFrame:
    results_list = list(links_table.apply(process_link, axis=1))
    results_dict = {x["question_no"]: x for x in results_list}

    results_df = pd.DataFrame.from_dict(results_dict, orient = 'index')

    return results_df



if __name__ == "__main__":
    links_table_cols = ['N°', 'Intitulé', 'Date', 'Link']
    with open("links_table_header.csv", 'wt') as f:     # store the table header separately. In order to prevent difficult code when appending.
        f.write('\t'.join(links_table_cols))

    # links_table = pd.DataFrame(columns=['N°', 'Intitulé', 'Date', 'Link'])

    results_table_cols = ['intitule', 'ministere_interroge', 'ministere_attributaire', 'rubrique',
       'titre', 'analyse', 'question_no', 'question_mode', 'asker',
       'question_publiee', 'question_retire', 'fin_de_mandat', 'url',
       'text_de_la_question', 'text_de_la_response']
    with open("results_table_header.csv", 'wt') as f:   # store the table header separately. In order to prevent difficult code when appending.
        f.write('\t'.join(results_table_cols))


    # results_table = pd.DataFrame(columns=results_table_cols)    # The table in which the results will be stored. #TODO remove this.
        
    with webdriver.Firefox() as driver:     # Start the selenium driver
        driver.get(BASE_URL)                # Go to the page with the menu.

        ##legislature > option:nth-child(2)
        # Select(driver.find_element_by_css_selector("#legislature > option:nth-child(2)"))

        # Select the period of which the questions need to be downloaded.
        select = Select(driver.find_element_by_id('legislature'))   
        select.select_by_value("13")

        # Find the search button and click it.
        search_btn = driver.find_element_by_css_selector('div.pull-right:nth-child(1) > p:nth-child(1) > button:nth-child(2)')
        search_btn.click()

        # Keep going until no pages are left. Breaking the loop is done with a break statement later.
        page = 1
        while True:
            # Try <NTRIES> times
            for j in range(NTRIES):

                if j > 1:       # If not the first try
                    print(f"Try {j}")
                    driver.refresh()        # Refresh the driver.

                    time.sleep(1)

                    
                try:

                    try:
                        obj = driver.switch_to.alert
                        print(obj)
                    except Exception as e:
                        print("no alert object")
                        print(e)
                    links_subTable = get_links(driver)

                    results_df = process_links_table(links_subTable)
                    print(results_df)
                    # Append the results table
                    results_df.to_csv(RESULTS_TABLE_FILE, sep='\t', mode = 'a', header = False)     
                    # Append the links table
                    links_subTable.to_csv(LINKS_TABLE_FILE, sep='\t', mode = 'a', header = False)
                    break
                except Exception as exc2:
                    print(exc2)
                    if j == NTRIES - 1:     # If no more tries are left.
                        logging.warning(f"Could not parse {driver.current_url} after {NTRIES} tries")
                    continue

            # Try to find the button to proceed to the next page.
            try:
                nextbutton = driver.find_element_by_link_text("Suivant »")
                
                nextbutton.click()

                page +=1
                print(page, end = '\n----------------------------------------------------\n')
            # If the button to the next page does not work/exist, terminate the program.
            except Exception as e:
                print("Ending the loop because of exception")
                print(e)
                input()
                break
            

        # process_link(links_subTable.Link[1], links_subTable.Intitulé[1])