# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import csv
import urllib.request

#### Listes de mots utilisées dans le script ###

articles_indefinis = ["un", "une"]
articles_definis = ["le", "la", "l'"]
conjonction_subordination = ["à", "dans", "en", "durant", "sur", "lors"]

### Fonctions utilisées ###

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
        
def extract_year(text):
    liste_citation = content_text.find_all('a', href=re.compile("#cite_ref"))
    # correspond au stockage des références (ces items ne nous intéressent pas)
    
    liste1 = content_text.find_all('li')
    liste2 = []
    liste3 = []
    for i in liste1:
        if i.a not in liste_citation:
            if i.a['href'][0] != '#': #correspond au sommaire (ces items ne nous intéressent pas)
                liste2.append(i)
    for i in liste2:
        if is_number(i.a['href'][6:]): #Années (ces items nous intéressent, nous les récupérons ainsi que les items associés)
            liste3.append(i)
    return liste3
    
def year_event(liste):
    annee = liste.a['href'][6:]
    liste_event_int = list(liste.ul.children) #Items correspondants aux différentes morts de l'année, et à leur description
    liste_event = [i for i in liste_event_int if i != '\n']
    noms_mort = []
    for j in liste_event:
        if extract_name(j) != None:
            noms_mort.append(extract_name(j)) 
    if len(noms_mort) > 0:
        return annee, noms_mort
    
def extract_name(element):
    """ Le but de cette fonction est d'extraire le nom de la personne du paragraphe décrivant sa mort. Pour cela, la fonction 
    va repérer le premier nom cité dans le paragraphe (suite de mots commençant par une majuscule). Si le paragraphe commence
    par un article indéfini, il concerne un anonyme (et ne nous intéresse pas). Si le paragraphe commence par un article défini,
    cet article est retiré en amont (il commence bien par une majuscule, mais n'est pas le nom de la personne)"""
    contenu = element.text
    premier_mot = re.findall('^\w+', contenu)
    while premier_mot[0].lower() in conjonction_subordination: 
    #Si le paragraphe commence par une proposition subordonnée, on l'enlève pour ne s'intéresser qu'à la proposition principale
        if contenu.find(',') > 0:
            contenu = contenu[(contenu.find(',')+2):]
            premier_mot = re.findall('^\w+', contenu)
        else: 
        # Il y a une proposition subordonnée dans la phrase mais pas de virgule : la phrase n'est pas correcte et aucune
        # valeur n'est renvoyée
            return
            
    if premier_mot[0].lower() in articles_indefinis: 
    # Si la proposition principale commence par un article indéfini, le mort n'est pas identifié, et ne nous intéresse donc pas  
        return
    if premier_mot[0].lower() in articles_definis: 
    #Si la proposition principale commence par un article défini, on retire cet article     
        contenu = contenu[2:] 
        
    mot = re.findall('([A-Z]\w+)', contenu) # Recherche du premier mot contenant une majuscule
    if len(mot) == 0:
        return # Si il n'y a pas de non avec une majuscule, la fonction ne renvoie rien
    else:
        nom = mot[0]
        while len(mot) > 0: 
            if len(mot) == 1:
            # Si il n'y a qu'un nom en majuscule dans la proposition principale (hors articles), c'est le nom qui nous
            # intéresse    
                return nom
            else:
                index_mot0 = contenu.find(mot[0])
                contenu = contenu[index_mot0 + len(mot[0]):]
                index_mot1 = contenu.find(mot[1])
                if index_mot1 > 4:
                # Si les différents noms propres sont espacés de plus de 4 caractères, il s'agit de choses différentes :
                # le prenier nom nous intéresse
                    return nom
                else:
                # Si les nons propres sont espacés de moins de 4 caractères, il s'agit d'un nom composé : la totalité du 
                # nom du mort est récupérée
                    nom +=contenu[:index_mot1 + len(mot[1])]
                    mot = mot[1:]

def save_tableau(liste_sauvegarde, fichier_final):
    """ Le but de cette fonction est de sauvegarder les informations extraites de la page internet sous la fonme d'un tableau 
    'Année du décès' 'Personne décedée'"""
    fichier_final.writerow(["Année", "Personne décédée"])  
    for i in liste_sauvegarde:
        if i != None:
            for j in i[1]:
                fichier_final.writerow([i[0], j])

### Main ###

with urllib.request.urlopen("https://fr.wikipedia.org/wiki/Liste_de_morts_insolites") as page:
    page_a_scrapper = page.read()

soup = BeautifulSoup(page_a_scrapper,"lxml")

#Selection du contenu de la page wikipedia
content_text = soup.find(id="mw-content-text")

#Selection des listes contenant les informations qui nous intéressent : les années, et les morts associés.
liste_interet = extract_year(content_text)
liste_mort = []
for i in liste_interet:
    liste_mort.append(year_event(i))

#Sauvegarde de la liste sous format csv

with open("Liste_morts_insolites.csv", 'w') as csvFile:
    fichier_final = csv.writer(csvFile)
    save_tableau(liste_mort, fichier_final)
csvFile.close()