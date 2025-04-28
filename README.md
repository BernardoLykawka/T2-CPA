# Trabalho 2 - CPA

## Descrição
Este projeto faz parte do Trabalho 2 da disciplina de Coleta, Preparação e Análise de Dados. O objetivo é realizar web scraping para coletar dados relacionados às 250 séries com as maiores avaliações no IMDB. Inicialmente, será feito o scraping para obter as seguintes informações:
- Título
- Ano de estreia
- Número total de episódios
- Nota do IMDB 
- link para a página de cada série

Após coletar esses dados, o próximo passo é acessar as páginas específicas de cada uma das 250 séries e realizar um novo scraping para obter:
- popularidade da série
- listagem do elenco principal
  - nomes dos atores/atrizes
  - personagens que interpretam.

Os resultados obtidos serão armazenados no repositório do GitHub e organizados conforme a estrutura definida.

## Requisitos
- Python 3.18 com a lib Selenium

## Como Executar
1. Clone o repositório:
  ```bash
  git clone https://github.com/BernardoLykawka/T2-CPA.git
  ```
2. Navegue até o diretório do projeto:
  ```bash
  cd T2-CPA/
  ```
3. Use o comando:
  ```bash
  python3 scrapper.py
  ```

## Autores
- Bernardo Medeiros, Bernardo Kirsch, Iuri Queiroz e Luiza Flores
