# 判例を収集します
# 裁判例検索 (https://www.courts.go.jp/app/hanrei_jp/search1?reload=1) よりスクレイピングをする
# 実行時に、サイトへの負荷軽減のsleep(N)の設定を忘れない!!!

import os
import re
import time
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup

division = 1 # 民事:1, 刑事:2
list_dict = {1:"総合", 2:"最高裁判所", 3:"高等裁判所", 4:"下級裁判所", 5:"行政事件", 6:"労働事件", 7:"知的財産"}
search_list = [3] # list_dictに対応 [int]
search_gengo = ["令和", "平成", "昭和"]
output_dir = './pdf_files/'
precedent_set = set() # 判例が重複しないようにする

def download_pdf(url, save_dir):
    """
    URLで指定されたpdfファイルをダウンロードする

    Args:
        url (str): pdfファイルのURL
        save_dir (str): 保存先のパス
    """

    # ファイル名の取得
    file_name = url.split('/')[-1].replace('.pdf','')

    # 重複がないか確認
    if file_name in precedent_set:
        return
    precedent_set.add(file_name)

    # ダウンロードしたファイルの保存先の指定
    os.makedirs(save_dir, exist_ok = True)

    # ダウンロードし、ファイルを保存
    link = 'https://www.courts.go.jp' + url
    r = requests.get(link)
    if r.status_code == 200:
        with open(os.path.join(save_dir, file_name+'.pdf'), "wb") as f:
                f.write(r.content)
    else:
        print("Download Failed")
        return

# 正規表現
# pdfのURLパターン
pdf_url_ptn = re.compile('<a href="(.*?)" target="_blank">全文</a>')
page_ptn = re.compile('(\d+?)件中\d*?～\d*?件を表示')

max_page = 1000 # ページ最大値(多めに設定している)
cnt = 0 # ダウンロードした判例数

# 元号ごとに検索
for gengo in search_gengo:

    if gengo == "令和":
        year_from = 1
        year_to = 5
    elif gengo == "平成":
        year_from = 1
        year_to = 31
    elif gengo == "昭和":
        year_from = 22
        year_to = 64
    else:
        print("There is no precedent for the specified era name")
        continue

    # 年ごとに検索
    for year in tqdm(range(year_from, year_to+1), desc=gengo):
        # (元号)XX-YY年の1ページ目から、最大ページ数の取得
        # URLの設定
        url_page1 = "https://www.courts.go.jp/app/hanrei_jp/list2?page={}&sort=1&filter[judgeDateMode]=1&filter[judgeGengoFrom]={}&filter[judgeYearFrom]={}&filter[division1]={}".format(1, gengo, year, division)

        # Responseオブジェクト生成
        response_page1 = requests.get(url_page1)

        # 文字化け防止
        response_page1.encoding = response_page1.apparent_encoding

        # BeautifulSoupオブジェクト生成
        soup_page1 = BeautifulSoup(response_page1.text, "html.parser")
        match = re.search(page_ptn, str(soup_page1.find(name='p',string=page_ptn)))
        # 最大ページ数 = 全件数 // 10 + 1 (各ページ最大10件のため)
        max_page = int(match.group(1)) // 10 + 1
        
        # ページごとに検索
        for page_num in tqdm(range(1,max_page+1), desc=str(year)+'年',leave=False):
            # URLの設定
            URL = "https://www.courts.go.jp/app/hanrei_jp/list2?page={}&sort=1&filter[judgeDateMode]=1&filter[judgeGengoFrom]={}&filter[judgeYearFrom]={}&filter[division1]={}".format(page_num, gengo, year, division)

            # Responseオブジェクト生成
            response = requests.get(URL)

            # 文字化け防止
            response.encoding = response.apparent_encoding

            # BeautifulSoupオブジェクト生成
            soup = BeautifulSoup(response.text, "html.parser")

            # 判例全文のpdfにつながるリンクを取得
            elems = soup.select('a[href]')
            pdf_list = []
            for e in elems:
                a_tag_str = str(e)
                if re.match(pdf_url_ptn, a_tag_str):
                    # pdfのパスを取得
                    pdf_path = re.match(pdf_url_ptn, a_tag_str).group(1)

                    # ダウンロードするディレクトリの指定
                    output_dir2 = output_dir + gengo + '/' + str(year) + '/'     
                    # ダウンロード       
                    download_pdf(pdf_path, output_dir2)

                    cnt += 1
                    time.sleep(5) # ダウンロード負荷軽減

            time.sleep(5) # ページ読み込み負荷軽減

print("判例数:",cnt)