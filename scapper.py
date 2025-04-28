import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dataclasses import asdict, dataclass, field

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

@dataclass
class Serie:
    titulo: str = ""
    ano: int = 0
    episodios: int = 0
    nota: float = 0.0
    pagina: str = ""
    popularidade: int = 0
    elenco: list = field(default_factory=list)

    def cria_serie(self, imdb_li_tag):
        titulo = imdb_li_tag.find_element(By.CLASS_NAME, "ipc-title__text").text
        self.titulo = re.sub(r"^\d+\.\s*", "", titulo)
        dados = imdb_li_tag.find_elements(By.XPATH, './/span[contains(@class, "cli-title-metadata-item")]')
        
        if len(dados) >= 2:
            ano = dados[0].text
            ano = re.search(r"\d{4}", ano)
            self.ano = int(ano.group())
            
            episodios = dados[1].text
            episodios = re.findall(r'\d+', episodios)
            self.episodios = int(episodios[0])
        
        nota_text = imdb_li_tag.find_element(By.CLASS_NAME, "ipc-rating-star--rating").text
        self.nota = float(nota_text.replace(',', '.'))
        self.pagina = imdb_li_tag.find_element(By.TAG_NAME, "a").get_attribute("href")
        
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

    todas_series = []

    for serie_tag in lista_series:
        serie = Serie()
        serie.cria_serie(serie_tag)

        print(serie.titulo)
        print(serie.ano)
        print(serie.episodios)
        print(serie.nota)
        print(serie.pagina + '\n')
        
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(serie.pagina)


        time.sleep(2)

        try:
            wait = WebDriverWait(driver, 5)
            popularidade_element = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="hero-rating-bar__popularity__score"]')))
            popularidade_text = popularidade_element.text.strip()
            serie.popularidade = int(re.sub(r'\D', '', popularidade_text))
        except Exception as e:
            print(f"Popularidade não encontrada para {serie.titulo}: {e}")
            serie.popularidade = 0
            
        try:
            elenco_divs = driver.find_elements(By.XPATH, '//div[@data-testid="title-cast-item"]')
            for elenco_div in elenco_divs:
                try:
                    nome_ator = elenco_div.find_element(By.XPATH, './/a[@data-testid="title-cast-item__actor"]').text
                except:
                    nome_ator = "Não encontrado"
                try:
                    nome_papel = elenco_div.find_element(By.XPATH, './/a[@data-testid="cast-item-characters-link"]/span').text
                except:
                    nome_papel = "Não encontrado"
                
                serie.elenco.append({
                    "nome": nome_ator,
                    "papel": nome_papel
                })
        except Exception as e:
            print(f"Erro ao buscar elenco para {serie.titulo}: {e}")

        driver.close() 
        driver.switch_to.window(driver.window_handles[0])
        
        todas_series.append(asdict(serie))

        print("-" * 50)
finally:
    with open('top_250_series.json', 'w', encoding='utf-8') as f:
        json.dump(todas_series, f, ensure_ascii=False, indent=4)
    
    time.sleep(10)
    driver.quit()