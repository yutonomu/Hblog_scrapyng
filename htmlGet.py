from bs4 import BeautifulSoup
import json
import os
import requests
import time as ti

def htmlget():
    directry = "日向坂ブログ"
    html_directry = "html"
    now_page = 0 #ここで途中から開始するページを指定する
    stop_page = 1000

    # ファイルを作成。メンバーの名前のリストを取得
    search_url = 'https://www.hinatazaka46.com/s/official/search/artist?ima=0000'
    
    responce = requests.get(search_url)
    
    responce.raise_for_status()
    
    bs4_blog = BeautifulSoup(responce.text, 'html.parser')
    
    all_member =  bs4_blog.select('.sort-default li')
    
    name_kanji = []
    save_dir = {kanji: {} for kanji in name_kanji}
    
    if not os.path.isdir(directry) :
        os.mkdir(directry)
    
    for i in range(len(all_member)):
        name_kanji.append(all_member[i].find('div', {'class': 'c-member__name'}).get_text().strip())
        path = os.path.join(directry, name_kanji[i])
        save_dir[name_kanji[i]] = path
        if not os.path.isdir(path):
            os.mkdir(path)

    name_kanji.append('ポカ')
    path = os.path.join(directry, name_kanji[-1])
    save_dir[name_kanji[-1]] = path
    if not os.path.isdir(path):
        os.mkdir(path)

    # 配列をファイルに書き込む
    with open('hinataNameList.txt', 'w', encoding='utf-8') as file:
        for name in name_kanji:
            file.write(name + '\n')

    # ファイルに保存する
    with open('save_dir.json', 'w', encoding='utf-8') as json_file:
        json.dump(save_dir, json_file, ensure_ascii=False, indent=4)

    html_dir = os.path.join(directry, html_directry)

    if not os.path.isdir(html_dir):
        os.mkdir(html_dir)


    # # ファイルから情報を読み込む
    # with open('initial_blog_info.txt', 'r') as f:
    #     lines = f.readlines()

    # # linesリストから必要な情報を取得
    # finish_title = lines[0].strip()
    # finish_time = lines[1].strip()
        
    next_exist = True
    initial_Flag = False
    soup = []
    # 日向坂の更新順に並んでいるサイトのURLを取得
    url = 'https://www.hinatazaka46.com/s/official/diary/member/list?ima=0000&page={}'

    #時間計測用
    start_time = ti.time()
    # 対象とするページの情報をsoupの配列に格納する
    while next_exist:
        if now_page == 0:
            initial_Flag = True
        # アクセスするためのURL。１ページ目等を指定するため
        target_url = url.format(now_page)

        r = requests.get(target_url)
        ti.sleep(1)
        
        soup.append(BeautifulSoup(r.text,features="html.parser"))

        soup_dir = os.path.join(html_dir, f"{now_page}.html")
        # soupをファイルに書き込む
        with open(soup_dir, 'w', encoding='utf-8') as file:
            file.write(str(soup[-1]))

        link = 0
        next_page = soup[-1].select('svg')

        for i in range(len(next_page)):
            next_page[i] = next_page[i].find_parent()
            next_page[i] = next_page[i].find_parent()
            if next_page[i].get('href') != None:
                    link += 1

        print(now_page, 'ページ目が終わりました')

        if stop_page == now_page:
            next_exist = False
        elif now_page == 0:
            now_page += 1
        elif now_page >= 1 and link >= 2:
            now_page += 1
        else:
            next_exist = False

    end_time = ti.time()
    excution_time = end_time - start_time
    print(f"{excution_time/60:.2f} 分かかりました。")

htmlget()