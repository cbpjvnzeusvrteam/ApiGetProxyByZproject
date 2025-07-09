import asyncio
import aiohttp
from flask import Flask, jsonify
import random

app = Flask(__name__)

# Danh sách URL chứa proxy
henry_proxy = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
]

# Danh sách tag thông tin thêm
TAGS = [
    "admin@zproject2",
    "group@zproject3",
    "group@zproject4",
    "bot@zprojectX_bot"
]

# Kiểm tra proxy sống
async def check_proxy(session, proxy, proxy_type):
    test_url = "http://httpbin.org/ip"
    proxy_url = f"{proxy_type}://{proxy}"
    try:
        async with session.get(test_url, proxy=proxy_url, timeout=5) as resp:
            if resp.status == 200:
                return {
                    "proxy": proxy,
                    "type": proxy_type.upper(),
                    "more_info": TAGS  # Trả về toàn bộ danh sách tag
                }
    except:
        return None

# Tải và lọc proxy
async def fetch_and_validate_proxies(limit):
    proxies = set()
    async with aiohttp.ClientSession() as session:
        for url in henry_proxy:
            try:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.text()
                        for line in data.splitlines():
                            if ':' in line:
                                proxies.add((line.strip(), detect_type(url)))
            except:
                continue

        tasks = [
            check_proxy(session, proxy, ptype)
            for proxy, ptype in proxies
        ]
        results = await asyncio.gather(*tasks)
        live_proxies = [r for r in results if r]
        random.shuffle(live_proxies)
        return live_proxies[:limit]

# Xác định loại proxy từ URL
def detect_type(url):
    if "socks5" in url:
        return "socks5"
    elif "socks4" in url:
        return "socks4"
    else:
        return "http"

# API endpoint
@app.route('/getproxy=<int:count>', methods=['GET'])
def get_proxy(count):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    proxies = loop.run_until_complete(fetch_and_validate_proxies(count))
    return jsonify({
        "thanhcong": True,
        "soproxyget": count,
        "sodem_proxy_song": len(proxies),
        "danh_sach_proxy": proxies
    })

# Chạy server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)