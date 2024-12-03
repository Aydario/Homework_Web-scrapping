import requests
import json
from bs4 import BeautifulSoup
import re

# Список ключевых слов для поиска
KEYWORDS = ['дизайн', 'фото', 'web', 'python']


def fetch_articles(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, features='lxml')
    return response.status_code


def parse_article(article_soup):
    header = article_soup.select_one('h1.tm-title').find('span')
    author = article_soup.select_one('a.tm-user-info__username')
    time = article_soup.select_one('time')['datetime']
    text = article_soup.select_one('div.article-formatted-body').get_text(separator='\n', strip=True)
    return {
        'title': header.text.strip() if header else 'Заголовок отсутствует',
        'author': author.text.strip() if author else 'Неизвестный автор',
        'time': time,
        'text': text
    }


def main():
    # Получаем список статей с главной страницы
    soup = fetch_articles('https://habr.com/ru/articles')
    if isinstance(soup, BeautifulSoup):
        articles_list = soup.select_one('div.tm-articles-list')
        articles = articles_list.select('article.tm-articles-list__item')

        parsed_data = []
        for article in articles:
            link = 'https://habr.com' + article.select_one('a.tm-title__link')['href']
            article_soup = fetch_articles(link)
            if isinstance(article_soup, BeautifulSoup):
                article_data = parse_article(article_soup)
                for word in KEYWORDS:
                    if re.search(f'{word}', article_data['text'], re.IGNORECASE):
                        parsed_data.append({
                            'link': link,
                            'title': article_data['title'],
                            'author': article_data['author'],
                            'time': article_data['time'],
                        })
                        print(
                            f'{len(parsed_data)} article:\n'
                            f'link: {link}\n'
                            f'title: {article_data["title"]}\n'
                            f'author: {article_data["author"]}\n'
                            f'time: {article_data["time"]}\n\n'
                        )
                        break
            else:
                print(f'Error! Response status code: {article_soup}')

        print(f'A total of {len(parsed_data)} articles were found with these keywords')

        # Сохраняем результаты в JSON-файл
        with open('articles.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(parsed_data, ensure_ascii=False, indent=4))
    else:
        print(f'Error! Response status code: {soup}')


if __name__ == '__main__':
    main()
