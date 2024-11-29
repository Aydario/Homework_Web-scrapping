import requests
import json
from bs4 import BeautifulSoup

# Список ключевых слов для поиска
KEYWORDS = ['дизайн', 'фото', 'web', 'python']


def fetch_articles(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, features='lxml')


def parse_article(article_soup):
    header = article_soup.select_one('h1.tm-title').find('span').text.strip()
    author = article_soup.select_one('a.tm-user-info__username').text.strip()
    time = article_soup.select_one('time')['datetime']
    text = article_soup.select_one('div.article-formatted-body').get_text(separator='\n', strip=True).lower()
    return {
        'title': header,
        'author': author,
        'time': time,
        'text': text
    }


def main():
    # Получаем список статей с главной страницы
    soup = fetch_articles('https://habr.com/ru/articles')
    articles_list = soup.select_one('div.tm-articles-list')
    articles = articles_list.select('article.tm-articles-list__item')

    parsed_data = []
    for article in articles:
        link = 'https://habr.com' + article.select_one('a.tm-title__link')['href']
        article_soup = fetch_articles(link)

        article_data = parse_article(article_soup)
        for word in KEYWORDS:
            if word in article_data['text']:
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

    print(f'A total of {len(parsed_data)} articles were found with these keywords')

    # Сохраняем результаты в JSON-файл
    with open('articles.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(parsed_data, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    main()
