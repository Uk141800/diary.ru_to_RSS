import requests
from bs4 import BeautifulSoup
from rfeed import *
import datetime

def handler(a, b):
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    cookies = {
        '_ym_d':'',
        '_csrf':'',
        '_identity_':'',
        '_ym_isad':'',
        'PHPSESSID':'',
        '_ym_uid':''
# Так как на дайриках есть защита от ботов (которая не мешает обилию спама)
# самый простой способ авторизации - пройти её в браузере и скопировать куки сюда.
# Я почти уверен, что не все эти куки нужны.
    }


    try:
        user = a['queryStringParameters']['login'] # не совсем правильно называть это логином. Это адрес дневника
    except:
        user = '' #сюда можно вставить свой адрес, чтобы на него перенаправляло по умолчанию
    page = requests.get(f"https://{user}.diary.ru/?favorite", cookies=cookies, headers=headers)
    page = BeautifulSoup(page.text, 'lxml')
    posts = page.findAll("div",  {"class": ['singlePost countSecond', 'singlePost countFirst']})

    months = {
        "января":1,
        'февраля':2,
        'марта':3,
        'апреля':4,
        'мая':5,
        'июня':6,
        'июля':7,
        'августа':8,
        'сентября':9,
        'октября':10,
        'ноября':11,
        'декабря':12
    }

    items = []

    for post in posts:
        id = post['id'][4:]
        post_date = post.find("div",  {"class": 'countSecondDate postDate uline'})
        post_date = post_date.text.strip()
        post_date = post_date[post_date.find(',')+2:]

        post_time_title = post.find("div",  {"class": 'postTitle header'})
        post_time_title = post_time_title.text.strip().replace('\n','').replace('  ','')
        post_time_title = post_time_title.replace('ПодтверждениеЭтот пост будет безвозвратно удален:Вы уверены в том, что действительно хотите это сделать?ДаНет','')
        if len(post_time_title) == 5:
            post_time = post_time_title
            post_title = ""
        else:
            post_time = post_time_title[0:5]
            post_title = post_time_title[5:].strip()

        #print(f"{post_date} {post_time}")
        #print(post_title)

        post_author = str(post.find("div",  {"class": 'authorName'}).text).strip()
        #print(post_author.text.strip())

        post_text = post.find("div",  {"class": 'postInner'}).find("div",  {"class": 'paragraph'}).find('div')

        for img in post_text.findAll('img'):
            try:
                img['src'] = 'https://diary.ru' + img['src'] if img['src'].startswith('/') else img['src']
            except:
                pass

        post_text['style'] = ""
        try:
            item = Item(
                title=post_author + " " + post_title,
                link=f"http://diary.ru/p{id}.html",
                description=post_text,
                author=post_author,
                guid=Guid(f"http://diary.ru/p{id}.html"),
                pubDate=datetime.datetime(
                    int(post_date[-4:]),
                    months[post_date[3:-5]],
                    int(post_date[:2]),
                    int(post_time[:2]),
                    int(post_time[3:])))
            items.append(item)
        except Exception as e:
            return {
                'statusCode': 200,
                'body': 'Ошибка выполнения ' + e,
            }

    feed = Feed(
            title = "Избранновое",
            link = "https://diary.ru/",
            description = "Избранновое с сайта diary.ru, потому что пограммист только ломает, но не может сделать хотябы как было",
            language = "ru-ru",
            lastBuildDate = datetime.datetime.now(),
            items = items)


    return {
        'statusCode': 200,
        'body': feed.rss(),
    }
