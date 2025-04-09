from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dataclasses import dataclass

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://imdb.com/")
    driver.maximize_window()

    wait = WebDriverWait(driver, 1)
    menu_button = wait.until(EC.element_to_be_clickable((By.ID, "imdbHeader-navDrawerOpen")))

    menu_button.click()
    
    link_populares = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "250 séries mais populares")) )
     
    url = link_populares.get_attribute("href")
    driver.get(url)

    tag_ul = driver.find_element(By.XPATH, r'//*[@id="__next"]/main/div/div[3]/section/div/div[2]/div/ul')
    lista_series = tag_ul.find_elements(By.TAG_NAME, "li")

    for serie in lista_series:
        print((By.XPATH, r'./div/div/div/div/div[2]/div[2]/span[1]').text)

    @dataclass
    class Serie:
        titulo: str
        ano: str
        episodios: str
        classificacao: float
        pagina: str

        def cria_serie(imdb_li_tag):
            titulo = imdb_li_tag.find_element(By.CLASS_NAME, "ipc-title__text").text
            ano = imdb_li_tag.find_element(By.XPATH, r'./div/div/div/div/div[2]/div[2]/span[1]').text 
            
        

    time.sleep(10)
finally:
    driver.quit()
    