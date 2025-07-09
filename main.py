import asyncio
import aiohttp
from flask import Flask, jsonify, Response, json

app = Flask(__name__)

# 🌐 Danh sách URL chứa proxy
henry_proxy = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
]

# 🏷️ Danh sách tag thông tin thêm
TAGS = [
    "admin@zproject2",
    "group@zproject3",
    "group@zproject4",
    "bot@zprojectX_bot"
]

# 🧠 Xác định loại proxy từ URL
def detect_type(url):
    if "socks5" in url:
        return "socks5"
    elif "socks4" in url:
        return "socks4"
    else:
        return "http"

# ✅ Kiểm tra proxy sống
async def check_proxy(session, proxy, proxy_type):
    test_url = "http://httpbin.org/ip"
    proxy_url = f"{proxy_type}://{proxy}"
    try:
        async with session.get(test_url, proxy=proxy_url, timeout=5) as resp:
            if resp.status == 200:
                return {
                    "proxy": proxy,
                    "type": proxy_type.upper(),
                    "more_info": TAGS
                }
    except:
        return None

# 🔍 Lấy và lọc proxy sống
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

        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result:
                results.append(result)
            if len(results) >= min(limit, 100):
                break
        return results

# 📦 API JSON: Trả về proxy chi tiết, định dạng đẹp
@app.route('/getproxy=<int:count>', methods=['GET'])
def get_proxy(count):
    if count > 100:
        return jsonify({
            "thanhcong": False,
            "thongbao": "Số lượng yêu cầu vượt quá giới hạn (tối đa 100 proxy)"
        })

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    proxies = loop.run_until_complete(fetch_and_validate_proxies(count))

    if len(proxies) < count:
        return jsonify({
            "thanhcong": False,
            "thongbao": f"Không đủ proxy sống. Chỉ tìm được {len(proxies)} proxy."
        })

    data = {
        "thanhcong": True,
        "soproxyget": count,
        "sodem_proxy_song": len(proxies),
        "danh_sach_proxy": proxies
    }

    return app.response_class(
        response=json.dumps(data, indent=2, ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )

# 📄 API RAW: Trả về danh sách proxy dạng text thuần
@app.route('/getproxyraw=<int:count>', methods=['GET'])
def get_proxy_raw(count):
    if count > 100:
        return Response("Số lượng yêu cầu vượt quá giới hạn (tối đa 100 proxy)", status=400)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    proxies = loop.run_until_complete(fetch_and_validate_proxies(count))

    if len(proxies) < count:
        return Response(f"Không đủ proxy sống. Chỉ tìm được {len(proxies)} proxy.", status=503)

    raw_list = "\n".join([p["proxy"] for p in proxies])
    return Response(raw_list, mimetype='text/plain')

# 🚀 Chạy server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)