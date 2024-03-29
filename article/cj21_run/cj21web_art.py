import asyncio
import re
import time
import aiohttp
import pymysql
import os.path
import urllib.request
from lxml import etree


def input_mysql(params):
    con = pymysql.Connect(host='47.96.18.55', user='crawler', password='123456', database='cnstock_db', port=3306)
    cur = con.cursor()
    sql = 'insert ignore into f_article (f_uid,f_title,f_context,f_source,f_sourceTime,f_sourceAddress,f_inputTime,f_media,f_sourceSite) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(sql, params)
    con.commit()
    con.close()


async def get_requests(url):
    if (len(url)<5):
        page = {"url": url, "page": "NUll", "status": 500}
        return page
    async with aiohttp.ClientSession() as sess:
        try:
            async with await sess.get(url=url) as resp:
                page_text = await resp.text()
                if (resp.status != 200):
                    print("Erro:  ", resp.status, url)
                    page = {"url": url, "page": page_text, "status": resp.status}
                    return page
                page = {"url": url, "page": page_text, "status": 200}
                return page
        except:
            print("Erro_link")


def article_get(t):
    try:
        page = t.result()
        if (page["status"] != 200):
            print("url_Erro")
            return
        page_text = page["page"]
        url = page["url"]
        tree = etree.HTML(page_text)
        f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        uid = str(url).split('/')[-1].split('.')[0]
        content = tree.xpath("/html/body/div[@class='layout']/div[@class='col-l']/div[@class='main']/div[@class='content']")
        title = tree.xpath("/html/body/div[@class='layout']/div[@class='col-l']/div[@class='main']/h1/text()")
        if len(title) == 0 :
            print("版面预警 ",url)
            return
        title = str(title[0]).strip()
        info = tree.xpath("/html/body/div[@class='layout']/div[@class='col-l']/div[@class='main']/h6/text()")

        info = str(info[0]).strip().split('                  ')
        if len(info)>=2 :
            source = str(info[1])
            f_source = source.split(' ')[0]
            if ("21财经APP" in source):
                f_source = f_source + ' ' + source.split(' ')[1]
            sourTime = str(info[0])
        art = ""
        for i in range(len(content)):
            art = art+etree.tostring(content[i],encoding='utf-8').decode()

        img_url = tree.xpath("/html/body/div[@class='layout']/div[@class='col-l']/div[@class='main']/div[@class='content']//img/@src")



        img_list = ""
        img_path = "/home/NRGLXT/source/media/img/"
        # img_path = "D:\pythonProject\Pic\\"
        if not os.path.exists(img_path):  # 创建路径
            os.mkdir(img_path)
        for i in range(0, len(img_url)):
            imgfname = f_inputTime[0:10] + uid + "_" + str(i) + os.path.splitext(img_url[i])[1]
            urllib.request.urlretrieve(img_url[i], filename=img_path + imgfname)  # 下载图片
            art = art.replace(img_url[i], "http://hzlaiqian.com/media/img/" + imgfname)
            img_list = img_list + "http://hzlaiqian.com/media/img/" + imgfname + ","

        params = (uid, title, art, f_source, sourTime, url, f_inputTime, img_list, "21世纪经济报道")

        input_mysql(params)
    except:
        print('Erro ',url)


def page_index_get(urls):
    tasks = []
    for url in urls:
        c = get_requests(url)  # c是特殊函数返回的协程对象
        task = asyncio.ensure_future(c)  # 任务对象
        task.add_done_callback(article_get)
        tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))



# url = ['https://m.21jingji.com/article/20220630/herald/053a7206ed73e18b51c37ac692043495.html']
# page_index_get(url)
