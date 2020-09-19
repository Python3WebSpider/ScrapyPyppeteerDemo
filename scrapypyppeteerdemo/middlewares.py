from pyppeteer import launch
from scrapy.http import HtmlResponse
import asyncio
import logging

from twisted.internet.defer import Deferred

logging.getLogger('websockets').setLevel('INFO')
logging.getLogger('pyppeteer').setLevel('INFO')


def as_deferred(f):
    return Deferred.fromFuture(asyncio.ensure_future(f))


class PyppeteerMiddleware(object):
    
    async def _process_request(self, request, spider):
        browser = await launch(headless=False)
        page = await browser.newPage()
        pyppeteer_response = await page.goto(request.url)
        await asyncio.sleep(5)
        html = await page.content()
        pyppeteer_response.headers.pop('content-encoding', None)
        pyppeteer_response.headers.pop('Content-Encoding', None)
        response = HtmlResponse(
            page.url,
            status=pyppeteer_response.status,
            headers=pyppeteer_response.headers,
            body=str.encode(html),
            encoding='utf-8',
            request=request
        )
        await page.close()
        await browser.close()
        return response
    
    def process_request(self, request, spider):
        return as_deferred(self._process_request(request, spider))
