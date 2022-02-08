import asyncio
import sys
import re
import json
from aiohttp_client_cache import CachedSession, SQLiteBackend

INPUT_FILE = sys.argv[1]
REQUEST_TIMEOUT = 5
IP_PATTERN = re.compile("(?:(?:1\d\d|2[0-5][0-5]|2[0-4]\d|0?[1-9]\d|0?0?\d)\.){3}(?:1\d\d|2[0-5][0-5]|2[0-4]\d|0?[1-9]\d|0?0?\d)")
RDAP_URL = 'https://rdap.arin.net/registry/ip/'
GEOIP_URL = 'http://ipwhois.app/json/'


def parse_ips_from_file(filename) -> set:
    '''Return all unique ips found inside a file.'''
    unique_ips = set()
    for line in open(filename, "r+").readlines():
        for match in re.findall(IP_PATTERN, line):
            unique_ips.add(match)
    print('Found %s unique ips' % len(unique_ips))
    return unique_ips


def save_as_json(dict) -> None:
    '''Create a json file with the contents of dict '''
    with open('output.json', 'w') as file:
        file.write(json.dumps(dict))


async def fetch_ip_data(session, url, ip) -> dict:
    '''Asynchronously fetch data from url for a given ip address'''
    try:
        async with session.get(url+ip, timeout=REQUEST_TIMEOUT) as response:
            return json.loads(await response.text())
    except asyncio.exceptions.TimeoutError:
        return {'error': 'Request timed out'}
    except Exception as e:
        return {'error': repr(e)}


async def get_rdap_data(session, ip) -> dict:
    '''Request RDAP data from configured URL.'''
    return await fetch_ip_data(session, RDAP_URL, ip)


async def get_geoip_data(session, ip) -> dict:
    '''Request GEOIP data from configured URL.'''
    return await fetch_ip_data(session, GEOIP_URL, ip)


async def get_ip_info(session, ip) -> dict:
    '''Return the aggregated results of both methods of obtaining ip data.'''
    geo = await get_geoip_data(session, ip)
    rdap = await get_rdap_data(session, ip)
    return {'geoIp': geo, 'rdap': rdap}


async def main():
    async with CachedSession(cache=SQLiteBackend('http_cache')) as session:
        tasks = []
        ips = parse_ips_from_file(INPUT_FILE)
        for ip in ips:
            tasks.append(get_ip_info(session, ip))
        results = await asyncio.gather(*tasks)
        save_as_json(dict(zip(ips, results)))


if __name__ == "__main__":
    asyncio.run(main())
