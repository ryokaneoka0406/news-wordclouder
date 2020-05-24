import urllib
import ssl
from collections import defaultdict

import feedparser
from janome.tokenizer import Tokenizer
from wordcloud import WordCloud
import pandas as pd
import matplotlib.pyplot as plt


def news_title_generator(keyword):
    """
    get google news feed

    args:
        str
    return:
        list of str
    """
    keyword_quote = urllib.parse.quote(keyword)
    url = ("https://news.google.com/news/rss/search/section/q/" +
           keyword_quote + "/" + keyword_quote + "?ned=jp&amp;hl=ja&amp;gl=JP")
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context
    news_dict = feedparser.parse(url)
    articles = list()
    for i, article in enumerate(news_dict.entries):
        tmp = {
            "no": i,
            "title": article.title,
            "link": article.link,
            "published": article.published
        }
        articles.append(tmp)
    title_list = [article['title'] for article in articles]
    return title_list


def strip_media_title(news_list):
    """
    strip media title from news title

    args:
        list of str
    return:
        list of str
    """
    raw_title_df = pd.DataFrame(news_list)
    intermediate_df = raw_title_df[0].str.split(' - ', expand=True)
    title_list = intermediate_df[0]
    return title_list


def _counter(title_list):
    """
    count words in media news title

    args:
        list of str
    return:
        dict, list of str
    """
    t = Tokenizer()
    words_count = defaultdict(int)
    words = []
    for title in title_list:
        tokens = t.tokenize(title)
        for token in tokens:
            pos = token.part_of_speech.split(',')[0]
            if pos == '名詞':
                words_count[token.base_form] += 1
                words.append(token.base_form)
    return words_count, words


def word_clouder(title_list, keyword):
    """
    generate word cloud

    args:
        list of str, str
    return:
        none
    """
    words_count, words = _counter(title_list)
    text = ' '.join(words)
    stop_words = [keyword, ]
    wordcloud = WordCloud(
        font_path='/System/Library/Fonts/ヒラギノ明朝 ProN.ttc',
        width=900, height=600,
        background_color="white",
        stopwords=set(stop_words),
        max_words=500,
        min_font_size=4,
        collocations=False
    ).generate(text)

    plt.figure(figsize=(15, 12))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig("word_cloud.png")
    plt.show()


def start():
    """
    start input flow
    """
    while True:
        keyword = input(
            '任意のキーワードをどうぞ。\n' +
            '最新100件のニュースタイトルでこのキーワードと一緒に出てくる単語をワードクラウドにします。\n')
        title_list_and_medianame = news_title_generator(keyword)
        title_list = strip_media_title(title_list_and_medianame)
        word_clouder(title_list, keyword)
        break
