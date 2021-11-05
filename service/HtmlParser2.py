# HTML Web Scrabbing Forecast helper file


import logging
import os
import asyncio
import sys

import async_timeout
import time
import aiohttp

from domain import FundInfo
from datetime import datetime

from bs4 import BeautifulSoup
from aiohttp import ClientSession, ClientConnectorError, TCPConnector

hdfc_bond_url = 'https://www.moneycontrol.com/mutual-funds/nav/quant-liquid-plan/MES016'

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
LOGGER = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
headers = {"user-agent": USER_AGENT}


async def fetch(session, url):
    try:
        async with async_timeout.timeout(30):
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f'Response Status {response.status} is not OK')
    except asyncio.TimeoutError as ex:
        LOGGER.error(f'Unable to connect remote API : {url} - {repr(ex)}')
        raise ex


async def get_fund_info(future, location):
    start = time.time()
    info = None

    try:
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, location)
            LOGGER.info(f'fund content fetch in {time.time() - start} secs.')
            parse_start = time.time()
            info = await parse_fund_info(html)
            LOGGER.info(f'fund parsing took {time.time() - parse_start} secs.')
    except ClientConnectorError as ex:
        LOGGER.error(f'Unable to connect fund API : {repr(ex)}')
        info = FundInfo.FundInfo("", '0', '0', "", "")
        info.set_error(ex)
    except BaseException as ex:
        LOGGER.error(f'Unable to connect fund API : {repr(ex)}')
        info = FundInfo.FundInfo("", '0', '0', "", "")
        info.set_error(ex)

    LOGGER.info(f'FundAPI Time Taken {time.time() - start}')
    future.set_result(info)


async def parse_fund_info(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')

    seg_temp = soup.find_all('div', class_='personal_financePg')[0]
    # print(seg_temp)

    print ('-------------------------------')

    scheme = seg_temp.find_all('h1', class_='page_heading navdetails_heading')[0]
    scheme = scheme.text
    print(scheme)

    seg_temp = seg_temp.find_all('div', class_='leftblok')[0]
    #print (seg_temp)

    nav = seg_temp.find('span', class_='amt').text
    if len(nav) > 0:
        nav = nav[2:len(nav)]
    print(nav)

    purchase_value = '33.1363'

    last_updated = seg_temp.find('div', class_='grayvalue').text
    print(last_updated)

    diff = float(nav) - float(purchase_value)
    diff = "{:.4f}".format(diff)
    print (diff)

    last_updated = last_updated.replace("(as on ", "")
    last_updated = last_updated.replace("th", "")
    last_updated = last_updated.replace("st", "")
    last_updated = last_updated.replace("nd", "")
    last_updated = last_updated.replace("rd", "")
    last_updated = last_updated.replace(",", "")
    last_updated = last_updated.replace(")", "")
    # last_updated = last_updated[len('(as on ') : len(last_updated)-1]
    print(last_updated)

    # datetime_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
    datetime_object = datetime.strptime(last_updated, '%d %B %Y')
    #print(datetime_object)
    last_updated = datetime_object.strftime("%d-%b-%Y")
    print(last_updated)

    fuel_info = FundInfo.FundInfo("", "", scheme, last_updated, nav, last_updated)
    fuel_info.set_error(None)

    LOGGER.info(str(fuel_info))

    return fuel_info


# Testing Methods
def callback(future):
    print (future.result())


def call_fund_api(location):
    LOGGER.info("call_fund_api")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    f1 = asyncio.Future()

    f1.add_done_callback(callback)

    tasks = [get_fund_info(f1, location)]
    loop.run_until_complete(asyncio.wait(tasks))

    loop.close()

    return f1.result()



if __name__ == '__main__':
    LOGGER.info (f"Parser starts ... args: {len(sys.argv)}")

    #call_weather_accu('4ef51d4289943c7792cbe77dee741bff9216f591eed796d7a5d598c38828957d') # thalambur
    # call_weather_forecast('thalambur')
    #call_weather_api('4ef51d4289943c7792cbe77dee741bff9216f591eed796d7a5d598c38828957d')
    # call_fuel_api()
    # call_gold_api()
    call_fund_api()

