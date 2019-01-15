import asyncio
import re
import aiohttp
import aiomysql
import uvloop
from pyquery import PyQuery #解析HTML的库

stopping=False
start_url="http://www.jobbole.com/"
waitting_urls=asyncio.Queue()
seen_urls=set()         #已经爬取到的url

sem=asyncio.Semaphore(3)        #设置并发数为3

async def fetch(url,session):
    '''发送http请求'''
    async with sem:
        try:
            async with session.get(url) as resp:      #完成一次get请求
                print("status:{}".format(resp.status))
                if resp.status in [200,201]:
                    data=await resp.text()
                    return data
        except Exception as e:
            print("!!!!Exception:",e)


def extract_urls(html):             #提取url是cpu操作，无需改成协程
    '''文章解析出url放入seen_urls队列'''
    pq=PyQuery(html)
    for link in pq.items("a"):
        url=link.attr("href")       #去掉已经爬取过的url，放入到等待爬取的列表
        if url and url.startswith("http") and url not in seen_urls:
            waitting_urls.put_nowait(url)


async def article_handler(url,session,pool):
    '''获取文章详情并解析入库'''
    html=await fetch(url,session)
    seen_urls.add(url)
    extract_urls(html)
    pq=PyQuery(html)
    title=pq("title").text()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            insert_sql="insert into jobbole_article(title) values('{}')".format(title)
            await cur.execute(insert_sql)

async def consumer(pool):
    '''控制爬虫，从队列中获取url交给文章解析函数'''
    async with aiohttp.ClientSession() as session:  #全局唯一一次创建session
        while not stopping:
            url=await waitting_urls.get()       #获取一个url,如果获取不到会一直等待
            print("start get url:{}".format(url))
            if re.match('http://.*?jobbole.com/\d+/',url):
                if url not in seen_urls:
                    asyncio.ensure_future(article_handler(url,session,pool))
                    await asyncio.sleep(0.5)
            waitting_urls.task_done()           #指名获取url任务已完成

async def main(loop):
    # 全局唯一一次创建pool
    pool=await aiomysql.create_pool(host='127.0.0.1',port=3306,user='root',password='123456',db='article_spider',loop=loop,charset='utf8',autocommit=True)

    async with aiohttp.ClientSession() as session:
        html = await fetch(start_url, session)
        seen_urls.add(start_url)
        extract_urls(html)
    asyncio.ensure_future(consumer(pool))   #传递连接池

if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop=asyncio.get_event_loop()
    asyncio.ensure_future(main(loop))
    loop.run_forever()
