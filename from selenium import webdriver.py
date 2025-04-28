from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import time
import json
from dataclasses import dataclass, asdict

@dataclass
class AtorPersonagem:
    ator: str
    personagem: str

@dataclass
class Serie:
    titulo: str
    ano: str
    classificacao: float
    pagina: str
    popularidade: str
    elenco: list
    numero_episodios: str

def configurar_driver():
    options = webdriver.ChromeOptions()
    # Adiciona algumas opções para melhorar a performance
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Descomente a linha abaixo para executar em modo headless (sem abrir o navegador)
    # options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def extrair_ano_da_serie(driver, wait):
    # Tenta encontrar o ano usando o seletor exato da imagem
    try:
        # Seletor atualizado baseado na estrutura HTML fornecida
        ano_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//ul[contains(@class, "ipc-inline-list")]/li/a[contains(@class, "ipc-link--baseAlt") and contains(@href, "/releaseinfo")]')))
        return ano_elem.text
    except:
        try:
            # Tenta outro seletor para o ano
            ano_elem = driver.find_element(By.XPATH, '//a[contains(@href, "/releaseinfo") and contains(@class, "ipc-link")]')
            return ano_elem.text
        except:
            try:
                # Tenta um terceiro seletor
                ano_elem = driver.find_element(By.XPATH, '//a[contains(@href, "tt") and contains(@href, "releaseinfo")]')
                return ano_elem.text
            except:
                return "N/A"

def extrair_classificacao_da_serie(driver, wait):
    # Tenta encontrar a classificação usando o seletor exato da imagem
    try:
        # Seletor atualizado baseado na estrutura HTML fornecida
        classificacao_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/span[@class="sc-d54185f9-1 imUuxf"]')))
        return float(classificacao_elem.text.replace(',', '.'))
    except:
        try:
            # Tenta outro seletor para classificação
            classificacao_elem = driver.find_element(By.XPATH, '//span[contains(@class, "sc-d54185f9-1")]')
            return float(classificacao_elem.text.replace(',', '.'))
        except:
            try:
                # Tenta um terceiro seletor
                classificacao_elem = driver.find_element(By.XPATH, '//div[contains(@data-testid, "hero-rating-bar__aggregate-rating__score")]/span')
                return float(classificacao_elem.text.replace(',', '.'))
            except:
                return 0.0

def extrair_elenco_da_serie(driver, wait):
    # Lista para armazenar os atores e personagens
    elenco = []
    
    try:
        # Aguarda a seção de elenco carregar
        wait.until(EC.presence_of_element_located((By.XPATH, '//section[contains(@data-testid, "title-cast")]')))
        
        # Encontra todos os itens de elenco usando o seletor exato da imagem
        elenco_tags = driver.find_elements(By.XPATH, '//div[contains(@class, "sc-cd7dc4b7-7") or contains(@class, "vCane")]')
        
        # Se não encontrar com o seletor acima, tenta outro
        if not elenco_tags:
            elenco_tags = driver.find_elements(By.XPATH, '//div[contains(@data-testid, "title-cast-item")]')
        
        # Limita aos 6 primeiros atores
        for i, ator_tag in enumerate(elenco_tags[:6]):
            try:
                # Extrai o nome do ator usando o seletor exato
                nome_ator_elem = ator_tag.find_element(By.XPATH, './/a[@data-testid="title-cast-item__actor"]')
                nome_ator = nome_ator_elem.text
                
                # Extrai o nome do personagem usando o seletor exato
                try:
                    personagem_elem = ator_tag.find_element(By.XPATH, './/span[contains(@class, "sc-cd7dc4b7-4") or contains(@class, "zVTic")]')
                    personagem = personagem_elem.text
                except NoSuchElementException:
                    # Tenta outro seletor para o personagem
                    try:
                        personagem_elem = ator_tag.find_element(By.XPATH, './/a[contains(@data-testid, "cast-item-characters-link")]/span')
                        personagem = personagem_elem.text
                    except:
                        personagem = "Personagem não encontrado"
                
                elenco.append(AtorPersonagem(nome_ator, personagem))
                
                # Se já temos 6 atores, paramos
                if i >= 5:
                    break
                    
            except Exception as e:
                print(f"Erro ao capturar informações do ator: {e}")
        
    except Exception as e:
        print(f"Erro ao capturar elenco: {e}")
    
    return elenco

def acessar_pagina_serie(driver, serie):
    driver.get(serie.pagina)
    wait = WebDriverWait(driver, 10)
    
    # Esperar até que a página da série carregue completamente
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    
    # Extrai o ano usando o seletor específico
    serie.ano = extrair_ano_da_serie(driver, wait)
    
    # Extrai a classificação usando o seletor específico
    serie.classificacao = extrair_classificacao_da_serie(driver, wait)
    
    try:
        # Popularidade
        popularidade_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[contains(@class, "sc-5f7fb5b4-1") and contains(@class, "TZoor")]')))
        serie.popularidade = popularidade_elem.text
    except (TimeoutException, NoSuchElementException) as e:
        try:
            # Tenta outro seletor para popularidade
            popularidade_elem = driver.find_element(
                By.XPATH, '//div[contains(@data-testid,"hero-rating-bar__popularity__score")]')
            serie.popularidade = popularidade_elem.text
        except:
            print(f"Erro ao capturar popularidade para {serie.titulo}")
            serie.popularidade = "N/A"
    
    try:
        # Número de episódios - usando o seletor exato da imagem
        episodios_elem = driver.find_element(
            By.XPATH, '//span[@data-testid="hero-subnav-bar-series-episode-count"]')
        serie.numero_episodios = episodios_elem.text
    except NoSuchElementException:
        try:
            # Tenta outro seletor para episódios
            episodios_elem = driver.find_element(
                By.XPATH, '//span[contains(@class, "sc-45a414e-1")]')
            serie.numero_episodios = episodios_elem.text
        except NoSuchElementException:
            print(f"Não foi possível encontrar o número de episódios para {serie.titulo}")
            serie.numero_episodios = "N/A"

    # Extrai o elenco usando a função específica
    serie.elenco = extrair_elenco_da_serie(driver, wait)

def coletar_dados_series():
    driver = configurar_driver()
    series = []
    
    try:
        # Restaurando a navegação original
        driver.get("https://imdb.com/")
        driver.maximize_window()

        wait = WebDriverWait(driver, 10)
        
        try:
            # Esperar até que o menu esteja visível e clicar
            menu_button = wait.until(EC.element_to_be_clickable((By.ID, "imdbHeader-navDrawerOpen")))
            menu_button.click()
            print("Menu aberto com sucesso")
        except Exception as e:
            print(f"Erro ao clicar no botão de menu: {e}")
            return []
        
        try:
            # Aguardar o link para as séries mais populares aparecer e clicá-lo
            link_populares = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "250 séries mais populares")))
            url = link_populares.get_attribute("href")
            driver.get(url)
            print("Navegou para a página de séries populares")
        except Exception as e:
            print(f"Erro ao capturar o link das séries populares: {e}")
            # Tenta um caminho alternativo
            try:
                link_populares = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '250 séries mais populares')]")))
                link_populares.click()
                print("Navegou para a página de séries populares (método alternativo)")
            except Exception as e2:
                print(f"Erro no método alternativo: {e2}")
                return []
        
        # Aguarda a página carregar
        time.sleep(3)
        
        # Verifica se precisa ordenar por classificação
        try:
            # Tenta encontrar e clicar no seletor de ordenação
            sort_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Sort') or contains(@class, 'sort')]")))
            sort_button.click()
            print("Botão de ordenação clicado")
            
            # Aguarda as opções de ordenação aparecerem
            time.sleep(1)
            
            # Seleciona ordenação por classificação (rating)
            rating_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'IMDb rating') or contains(text(), 'classificação') or contains(text(), 'Rating')]")))
            rating_option.click()
            print("Ordenado por classificação")
            
            # Aguarda a página recarregar com a nova ordenação
            time.sleep(3)
        except Exception as e:
            print(f"Erro ao tentar ordenar por classificação: {e}")
            print("Continuando com a ordenação padrão...")
        
        # CORREÇÃO: Vamos processar as séries em duas etapas para evitar o erro de stale element
        # Primeiro, vamos obter todas as URLs das séries
        urls_series = []
        
        try:
            # Esperar o carregamento completo da lista de séries
            tag_ul = wait.until(EC.presence_of_element_located((By.XPATH, '//ul[contains(@class, "ipc-metadata-list")]')))
            lista_series = tag_ul.find_elements(By.TAG_NAME, "li")
            print(f"Encontradas {len(lista_series)} séries na lista.")
            
            # Limita a 250 séries se houver mais
            lista_series = lista_series[:250]
            
            # Primeiro, vamos coletar todas as URLs e informações básicas
            for i, item in enumerate(lista_series):
                try:
                    # Extrai informações básicas
                    titulo_elem = item.find_element(By.XPATH, './/h3[contains(@class, "ipc-title__text")]')
                    titulo_completo = titulo_elem.text
                    
                    # Remove o número de ranking do início (ex: "1. Breaking Bad" -> "Breaking Bad")
                    titulo_sem_ranking = titulo_completo.split('. ', 1)[1] if '. ' in titulo_completo else titulo_completo
                    
                    # Extrai o título limpo (sem o ano)
                    titulo_limpo = titulo_sem_ranking
                    if "(" in titulo_sem_ranking:
                        titulo_limpo = titulo_sem_ranking[:titulo_sem_ranking.rfind("(")].strip()
                    
                    # Extrai o link para a página da série
                    link_elem = item.find_element(By.TAG_NAME, "a")
                    link = link_elem.get_attribute('href')
                    
                    # Cria o objeto da série com as informações básicas
                    # Nota: o ano e classificação serão extraídos na página da série
                    serie = Serie(titulo_limpo, "N/A", 0.0, link, "", [], "N/A")
                    urls_series.append(serie)
                    
                except Exception as e:
                    print(f"Erro ao processar informações básicas da série {i+1}: {e}")
            
            print(f"Coletadas informações básicas de {len(urls_series)} séries.")
            
            # Agora, vamos acessar cada URL individualmente para obter detalhes adicionais
            for i, serie in enumerate(urls_series):
                try:
                    print(f"\nProcessando série {i+1}/{len(urls_series)}: {serie.titulo}")
                    
                    # Acessa a página da série para obter detalhes adicionais
                    acessar_pagina_serie(driver, serie)
                    
                    # Adiciona a série à lista final
                    series.append(serie)
                    
                    # Exibe as informações da série
                    print(f"--- Informações da série ---")
                    print(f"Título: {serie.titulo}")
                    print(f"Ano: {serie.ano}")
                    print(f"Classificação: {serie.classificacao}")
                    print(f"Página: {serie.pagina}")
                    print(f"Popularidade: {serie.popularidade}")
                    print(f"Número de episódios: {serie.numero_episodios}")
                    print(f"Elenco principal: ")
                    for ator_personagem in serie.elenco:
                        print(f"  {ator_personagem.ator} como {ator_personagem.personagem}")
                    
                    # Pequena pausa para não sobrecarregar o servidor
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Erro ao processar detalhes da série {i+1}: {e}")
            
        except Exception as e:
            print(f"Erro ao encontrar a lista de séries: {e}")
            return []
        
        print(f"\nTotal de séries capturadas: {len(series)}")
        
    except Exception as e:
        print(f"Erro durante a coleta de dados: {e}")
    finally:
        driver.quit()
    
    # Retorna a lista de séries coletadas
    return series

def salvar_para_json(series, nome_arquivo="series_imdb.json"):
    """
    Salva a lista de séries em um arquivo JSON
    """
    try:
        # Converte os objetos Serie para dicionários
        series_dict = []
        for serie in series:
            # Converte o objeto Serie para um dicionário
            serie_dict = {
                "titulo": serie.titulo,
                "ano": serie.ano,
                "classificacao": serie.classificacao,
                "pagina": serie.pagina,
                "popularidade": serie.popularidade,
                "numero_episodios": serie.numero_episodios,
                "elenco": []
            }
            
            # Converte cada objeto AtorPersonagem para um dicionário
            for ator_personagem in serie.elenco:
                serie_dict["elenco"].append({
                    "ator": ator_personagem.ator,
                    "personagem": ator_personagem.personagem
                })
            
            series_dict.append(serie_dict)
        
        # Salva no arquivo JSON
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(series_dict, f, ensure_ascii=False, indent=4)
        
        print(f"Dados salvos com sucesso no arquivo '{nome_arquivo}'")
        return True
    except Exception as e:
        print(f"Erro ao salvar dados para JSON: {e}")
        return False

if __name__ == "__main__":
    # Coleta os dados
    series_coletadas = coletar_dados_series()
    
    # Exibe um resumo dos dados coletados
    print("\n\n=== RESUMO DOS DADOS COLETADOS ===")
    print(f"Total de séries coletadas: {len(series_coletadas)}")
    
    # Exibe os dados de todas as séries coletadas
    print("\n=== DADOS DE TODAS AS SÉRIES ===")
    for i, serie in enumerate(series_coletadas):
        print(f"\n{i+1}. {serie.titulo} ({serie.ano}) - Nota: {serie.classificacao}")
        print(f"   Número de episódios: {serie.numero_episodios}")
        print(f"   Popularidade: {serie.popularidade}")
        print(f"   Link: {serie.pagina}")
        print(f"   Elenco principal:")
        for ator in serie.elenco:
            print(f"     - {ator.ator} como {ator.personagem}")
    
    # Salva os dados em um arquivo JSON
    salvar_para_json(series_coletadas)