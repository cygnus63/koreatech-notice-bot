import requests
from bs4 import BeautifulSoup
import telegram
import time
import threading

# 텔레그램 관련
term = int(input("검색 주기 설정 (초 단위) >> "))

def sendTG(type, link, title, views):
    button = [[telegram.InlineKeyboardButton('자세히 보기', url = link)]]
    reply_markup = telegram.InlineKeyboardMarkup(button)

    bot.sendMessage(chat_id='YOUR_CHAT_ID', 
                    text = f'[{type}] {title}\n\n(조회수:{views})', 
                    reply_markup = reply_markup)

bot = telegram.Bot(token='YOUR_TELEGRAM_BOT_TOKEN')

KUT = 'http://www.koreatech.ac.kr'

noticeURL = [
    'https://www.koreatech.ac.kr/kor/CMS/NoticeMgr/list.do?mCode=MN230',
    'https://www.koreatech.ac.kr/kor/CMS/NoticeMgr/scholarList.do?mCode=MN231',
    'https://www.koreatech.ac.kr/kor/CMS/NoticeMgr/bachelorList.do?mCode=MN233'
    ]

postNumDir = [
    '/python-docker/koreatech_notice/postNum_ilban.txt',
    '/python-docker/koreatech_notice/postNum_scholar.txt',
    '/python-docker/koreatech_notice/postNum_barchelor.txt'
]

# postNumDir = [
#     './postNum_ilban.txt',
#     './postNum_scholar.txt',
#     './postNum_barchelor.txt'
# ]

noticeType = ['일반공지', '장학공지', '학사공지']

def notice(a):
    type = noticeType[a]
    url = noticeURL[a]
    path = postNumDir[a]
    
    while True:
        with open(postNumDir[a], 'r') as f:
            postNums = f.read().splitlines()

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        postArea = soup.find('tbody')
        posts = postArea.find_all('tr')

        for i in posts:

            # 게시글 번호로 판단
            postInfo = i.find_all('td', {'class' : 'num'})
            postNum = postInfo[0].text
            
            if postNum not in postNums: # 파일에 번호가 없을 시

                # 게시글 번호 저장
                with open(path, "a") as f:
                    f.write(postNum + '\n')

                # 게시글 정보 GET
                postLink, postName, postWriter, postDate, postViews = getInfo(i)
                
                sendTG(type, postLink, postName, postViews)
                now = time.localtime()
                printInfo(type, postNum, postName, postWriter, postDate, postViews, postLink)

                print("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec), "\n")

                print('\n')

            else:   # 파일에 번호가 있을 때
                print("이미 존재 합니다")
                continue
            
        time.sleep(term)

def getInfo(i):
    postLink = KUT + i.find('a')['href']

    postName = i.find('span')['title']
    postWriter = i.find('td', {'class' : 'writer'}).text
    postDate = i.find('td', {'class' : 'date'}).text
    postViews = i.find('td', {'class' : 'cnt'}).text

    return postLink, postName, postWriter, postDate, postViews
                
def printInfo(type, postNum, postName, postWriter, postDate, postViews, postLink):
    print("-- 새 게시글 --\n")
    print(f"공지 분류 : {type}\n")
    print(f"게시글 번호 : {postNum}\n")
    print(f"게시글 이름 : {postName}")
    print(f"작성자 : {postWriter}")
    print(f"작성일자 : {postDate}")
    print(f"조회수 : {postViews}")
    print(f"링크 : {postLink}\n")

threads = []

for i in range(len(noticeType)):
    threads.append(threading.Thread(target=notice, args=(i,)))

for thread in threads:
    thread.start()

# # Wait for all threads to finish
# for thread in threads:
#     thread.join()
