import aiohttp
import asyncio
import json
import logging
from bs4 import BeautifulSoup
import re

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Список ключевых слов для поиска
KEYWORDS = ['дизайн', 'фото', 'web', 'python']


async def fetch_articles(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            response_text = await response.text()
            return BeautifulSoup(response_text, features='lxml')
        else:
            logger.error(f"Failed to fetch {url}: {response.status}")
            return None


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


async def process_article(session, article, parsed_data):
    link = 'https://habr.com' + article.select_one('a.tm-title__link')['href']
    article_soup = await fetch_articles(session, link)

    if article_soup:
        article_data = parse_article(article_soup)
        for word in KEYWORDS:
            if re.search(f'{word}', article_data['text'], re.IGNORECASE):
                parsed_data.append({
                    'found keyword': word,
                    'link': link,
                    'title': article_data['title'],
                    'author': article_data['author'],
                    'time': article_data['time'],
                })
                logger.info(
                    f'{len(parsed_data)} article:\n'
                    f'found keyword "{word}" in article\n'
                    f'link: {link}\n'
                    f'title: {article_data["title"]}\n'
                    f'author: {article_data["author"]}\n'
                    f'time: {article_data["time"]}\n\n'
                )
                break
    else:
        logger.error(f"Failed to process article: {link}")


async def main():
    async with aiohttp.ClientSession() as session:
        # Получаем список статей с главной страницы
        soup = await fetch_articles(session, 'https://habr.com/ru/articles')
        if soup:
            articles_list = soup.select_one('div.tm-articles-list')
            articles = articles_list.select('article.tm-articles-list__item')

            parsed_data = []
            tasks = [process_article(session, article, parsed_data) for article in articles]
            await asyncio.gather(*tasks)

            logger.info(f'A total of {len(parsed_data)} articles were found with these keywords')

            # Сохраняем результаты в JSON-файл
            with open('articles_with_aiohttp.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(parsed_data, ensure_ascii=False, indent=4))
        else:
            logger.error('Failed to fetch main page')


# Запуск асинхронной функции
asyncio.run(main())
