import asyncio
import time

import aiohttp
import zgzqb_art
from redis import StrictRedis
from hashlib import md5
from lxml import etree

news_list = []


def input_redis(url_id):
    redis = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    if redis.sismember('urllist', url_id):
        return True
    else:
        redis.sadd('urllist', url_id)
        return False


async def get_requests(url):
    async with aiohttp.ClientSession() as sess:
        async with await sess.get(url=url) as resp:
            page_text = await resp.text()
            if (resp.status != 200):
                print("Erro:  ",resp.status,url)
            return page_text


def news_list_get(t):
    page_text = t.result()
    tree = etree.HTML(page_text)
    #===============================================头条中间板块
    news = tree.xpath('//div[@class="box410 ch_focus space_l1"]/ul/li/a/@href')
    secret = md5()
    for new in news:
        secret.update(new.encode())
        newid = secret.hexdigest()
        # news_list.append(new)
        if not input_redis(newid):
            if ("weixin" not in new):
                news_list.append("https://www.cs.com.cn" + str(new).strip('.'))
            else:
                news_list.append(new)
    # ===============================================热点新闻
    news = tree.xpath('//div[@class="ch_typewd space_t3"]//a/@href')
    for new in news:
        secret.update(new.encode())
        newid = secret.hexdigest()
        # news_list.append(new)
        if not input_redis(newid):
            if ("weixin" not in new):
                news_list.append("https://www.cs.com.cn" + str(new).strip('.'))
            else:
                news_list.append(new)




def page_index_get(urls):
    tasks = []
    for url in urls:
        c = get_requests(url)  # c是特殊函数返回的协程对象
        task = asyncio.ensure_future(c)  # 任务对象
        task.add_done_callback(news_list_get)
        tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))

def main():
    urls_index = [
        'https://www.cs.com.cn/'
    ]
    page_index_get(urls_index)
    print(news_list)
    news_url = []

    for i in range(len(news_list)):
        news_url.append(news_list[i])
        if (len(news_url)==10):
            zgzqb_art.page_news_get(news_url)
            news_url=[]
            time.sleep(1)
    if (len(news_url)>0):
        zgzqb_art.page_news_get(news_url)
    print("中国证券报：更新 ",len(news_list),"条数据")