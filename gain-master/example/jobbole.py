import aiofiles
from gain import Css, Item, Parser, Regex, Spider


class Post(Item):
    title = Css('.entry-header h1::text')

    async def save(self):
        print(str(self.results))


class MySpider(Spider):
    start_url = 'http://blog.jobbole.com/'
    concurrency = 5
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'}
    parsers = [Parser('http://blog.jobbole.com/114503/', Post),]


MySpider.run()
