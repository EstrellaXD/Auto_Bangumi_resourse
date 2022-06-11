#! /usr/bin/python
import re
import time
import json
import requests
from bs4 import BeautifulSoup

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ApplewebKit/537.36 (KHtml, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
}


def get_html(url):
    requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    html = s.get(url=url, headers=header).text
    print("get html success")
    return html


def get_list(year, season):
    season = ["spring", "summer", "autumn", "winter"][season - 1]
    url = "https://anidb.net/anime/season/%s/%s/" % (year, season)
    html = get_html(url)
    ids = re.findall("<a href=\"/anime/(\d+)\"><picture>", html)
    return ids


def get_title(id):
    url = f"http://api.anidb.net:9001/httpapi?request=anime&client=autobangumi&clientver=1&protover=1&aid={id}"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "xml")
    titles = soup.titles.find_all("title")
    all_title_info = {
        "id": id,
        "main": None,
        "en": None,
        "zh-Hans": None,
        "zh-Hant": None,
        "ja": None,
        "other": []
    }
    for title in titles:
        if title["type"] == "main":
            all_title_info["main"] = title.string
        elif title["type"] == "official":
            if title["xml:lang"] in ["en", "zh-Hant", "zh-Hans", "ja"]:
                all_title_info[title["xml:lang"]] = title.string
            else:
                break
        elif title["type"] == "synonym":
            all_title_info["other"].append(title.string)
        else:
            break
    return all_title_info

def save(filename, obj):
    with open(filename, "w", encoding="utf8") as f:
        json.dump(obj, f, indent=4, separators=(",", ": "), ensure_ascii=False)
    pass


if __name__ == "__main__":
    localtime = time.localtime(time.time())
    month = localtime.tm_mon
    year = localtime.tm_year
    season = (month-1)//3
    season_list = [0, 1, 2, 3].remove(season)
    full_data = []
    ids = []
    for i in [0,1,2]:
        id = get_list(year, i)
        ids += id
        time.sleep(2)
    for id in ids:
        try:
            data = get_title(id)
            print(data)
            full_data.append(data)
        except Exception as e:
            print(e)
            continue
        time.sleep(2.5)
    save("resource/season_data.json", full_data)
