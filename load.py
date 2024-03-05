def image_error(d, message=None, errorNumber=None, url_images=None):
    with open(f'ERROR_{str(errorNumber)}.txt', 'w', encoding='utf-8') as f:
        f.write(pformat(d) + '\n')
        if message is not None:
            f.write(message + '\n')
        if url_images is not None and message == "指定した拡張子以外の画像ファイルがあります":
            for url in url_images:
                f.write(f'{url}\n')

    if message is not None:
        print(message)


def count_files_in_folder(folder_path):
    try:
        # フォルダ内のファイルリストを取得
        files = os.listdir(folder_path)
        
        # ファイルの数を返す
        return len(files)
    except FileNotFoundError:
        print(f"指定されたフォルダ '{folder_path}' が見つかりませんでした。")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None
    
from bs4 import BeautifulSoup
import json
import os
import pandas as pd
import random
import requests
import time as ti
from pprint import pprint
from pprint import pformat

def load():
    skip_Flag = True
    skip_page = 423
    skip_name = "松田 好花"
    errorNumber = 103

    # 判別する拡張子のリスト
    extensions_to_check = ['.jpeg', '.jpg', '.png', '.JPG']
    soup = []
    # 指定したディレクトリ内にあるファイルの数を取得
    soup_len = count_files_in_folder("日向坂ブログ/html")

    directry = "日向坂ブログ"
    html_directry = "html"
    html_dir = os.path.join(directry, html_directry)

    print(skip_page)
    print(soup_len)
    
    for i in range(skip_page,soup_len):
        soup_dir = os.path.join(html_dir, f"{i}.html")
        print(f"{i}.html")
        # ファイルからHTMLを読み込む
        with open(soup_dir, 'r', encoding='utf-8') as file:
            html_content = file.read()
            soup.append(BeautifulSoup(html_content, 'html.parser'))

    # ファイルからデータを取得する
    with open('hinataNameList.txt', 'r', encoding='utf-8') as file:
        # ファイルから行ごとにデータを読み込み、リストに格納する
        name_kanji = [line.strip() for line in file]

    with open('save_dir.json', 'r', encoding='utf-8') as json_file:
        save_dir = json.load(json_file)
    
    for i in range(len(soup)):
        #時間計測用
        start_time = ti.time()

        p_article = soup[i].find_all('div',class_="p-blog-article")

        for j in range(len(p_article)):
            article__head = p_article[j].find('div', class_="p-blog-article__head")

            title = article__head.find('div',class_="c-blog-article__title")
            time = article__head.find('div',class_="c-blog-article__date")
            name = article__head.find('div',class_="c-blog-article__name")
            article__text = p_article[j].find('div',class_="c-blog-article__text")

            title = title.text.strip()
            time = time.text.strip()
            name = name.text.strip()
            text = article__text.text.strip()
            text = text.replace("\n","")

            d = {
                'title': title,
                'time' : time,
                'text' : text
            }

            images = article__text.find_all('img')
            split_time = time.split()
            image_folder_name = f'{split_time[0]}_{split_time[1].replace(":", "h")}'

            #ブログのページを0からスクレイピング始めたときは一番最新のタイトルと時間をファイルに書き込む
            # if initial_Flag and i == 0 and j == 0: 
            #     with open('initial_brog_info.txt','w') as f:
            #         f.write(str(title) + '\n')
            #         f.write(str(time) + '\n')

            if name in name_kanji and (name == skip_name or not skip_Flag):
                df = pd.DataFrame([d])
                file_path = os.path.join(save_dir[name], f'{name}_blog.csv')
                if not os.path.exists(file_path):
                    df.to_csv(file_path,index=None,encoding='utf-8-sig')
                    print(f'{name}のファイルを新規に作成しました')
                else:
                    df.to_csv(file_path,mode='a',header=False,index=None,encoding='utf-8-sig')
                    # print(f'{name}のファイルに追加で書き込みました')
                
                nil_image = 0

                # 画像の量が多すぎると元のHTMLの構造のバグの可能性が高いため、ブログは１投稿につき30枚以下だろうと思った。
                if len(images) < 31 :

                    # 取得してきた画像のURLに対して空かどうか判定
                    url_images = [image.get('src') for image in images if image.get('src') != ('' or None)]
                    for k in range(len(url_images)):
                        # いずれかの拡張子が含まれているかどうかを判定
                        contains_extension = any(ext in url_images[k] for ext in extensions_to_check)

                        # 取得したURLが画像ファイルかどうか
                        if contains_extension:
                            image = requests.get(url_images[k])
                            ti.sleep(1)

                            image_path = os.path.join(save_dir[name], image_folder_name)
                            if not os.path.isdir(image_path):
                                os.mkdir(image_path)

                            with open(os.path.join(image_path,f'{k}.jpg'),'wb') as f:
                                f.write(image.content)
                        else:
                            # エラーではない正常に振り分けられているし、しっかりとこれらを除去して画像が保存できている。
                            # image_error(d,"指定した拡張子以外の画像ファイルがあります",errorNumber,url_images)
                            # errorNumber += 1
                            print("指定した拡張子以外の画像ファイルを取り除きました")
                    print('\t'+ f'{name}において{len(images)-nil_image}枚の写真を保存しました')
                else :
                    image_error(d,"画像が20枚以上あります",errorNumber)
                    errorNumber += 1

                skip_Flag = False
            else:
                print(f"{name}は日向坂のメンバーではない、またはスキップされました。")
                
        print(i + skip_page, ' ページ目が終わりました')
        #1つのページがどのくらいで終わるか
        end_time = ti.time()
        excution_time = end_time - start_time
        print(f"{excution_time/60:.2f} 分かかりました。")

load()