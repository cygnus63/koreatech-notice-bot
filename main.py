import os
import requests
from bs4 import BeautifulSoup
import telegram
import time
import threading
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise ValueError("TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID 환경 변수가 설정되지 않았습니다. .env 파일을 확인해 주세요.")

interval = 1800  # 30분 = 1800초
bot = telegram.Bot(token=TOKEN)

BASE_URL = "https://www.koreatech.ac.kr"

URLS = [
    ('일반공지', 'https://www.koreatech.ac.kr/notice/list.es?mid=a10604010000&board_id=14'),
    ('장학공지', 'https://www.koreatech.ac.kr/notice/list.es?mid=a10604020000&board_id=15'),
    ('학사공지', 'https://www.koreatech.ac.kr/notice/list.es?mid=a10604030000&board_id=16')
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

postNumDir = {
    '일반공지': os.path.join(BASE_DIR, 'postNum_ilban.txt'),
    '장학공지': os.path.join(BASE_DIR, 'postNum_scholar.txt'),
    '학사공지': os.path.join(BASE_DIR, 'postNum_barchelor.txt')
}


def sendTG(type, link, title, views):
    buttons = [
        [telegram.InlineKeyboardButton('자세히 보기', url=link)],
        [telegram.InlineKeyboardButton(f'조회수: {views}', callback_data='noop')]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(buttons)

    bot.sendMessage(chat_id=CHAT_ID, 
                    text=f'[{type}]\n{title}', 
                    reply_markup=reply_markup)

def notice(noticeType, url):
    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        board = soup.find('table')
        board = board.find('tbody')
        posts = board.find_all('tr')

        for post in posts:
            category, title, author, views, num, post_url = getInfo(post)
            if saveInfo(noticeType, num):
                printInfo(noticeType, category, title, author, views, num, post_url)
                sendTG(noticeType, post_url, title, views)
        
        time.sleep(interval)

def saveInfo(noticeType, num):
    file_path = postNumDir[noticeType]
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    with open(file_path, 'r+') as file:
        lines = file.readlines()
        if any(num in line for line in lines):
            return False
        else:
            file.write(f"{num} - {current_time}\n")
            return True
        
def printInfo(noticeType, category, title, author, views, num, post_url):
    print(f"유형: {noticeType}")
    print(f"번호: {num}")
    print(f"분류: {category}")
    print(f"제목: {title}")
    print(f"작성자: {author}")
    print(f"조회수: {views}")
    print(f"URL: {post_url}")
    print("\n")

def getInfo(post):
    category_td = post.find('td', {'aria-label': '분류'}) or ""  # 학사는 카테고리 분류가 없다.
    title_td = post.find('td', {'aria-label': '제목'}) 
    author_td = post.find('td', {'aria-label': '작성자'})
    views_td = post.find('td', {'aria-label': '조회수'})
    num_td = post.find('td', {'aria-label': '번호'})
        
    category = category_td.get_text(strip=True) if category_td else "카테고리 없음"
    title = title_td.get_text(strip=True)
    author = author_td.get_text(strip=True)
    views = views_td.get_text(strip=True)
    num = num_td.get_text(strip=True)

    title_link = title_td.find('a')
    post_url = BASE_URL + title_link.get('href')

    return category, title, author, views, num, post_url

threads = []

for noticeType, url in URLS:
    threads.append(threading.Thread(target=notice, args=(noticeType, url)))

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()