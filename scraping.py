import os
import datetime
import time
import pandas as pd

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# Selenium4対応済

# 日付設定
now = datetime.datetime.now()
ymdhms = now.strftime("%Y%m%d%h%m%s")

# パス
OUTPUT_PATH = "./OUTPUT"
EXP_CSV_PATH = f"{OUTPUT_PATH}/会社情報{ymdhms}.csv"
LOG_DIR = "./LOG"
log_file_path = f"{LOG_DIR}/{ymdhms}.log"

def log(txt):
    make_dir(LOG_DIR)
    with open(log_file_path, mode="a") as f:
        f.write(f"{txt}\n")

def make_dir(path):
    os.makedirs(path, exist_ok=True)

def set_driver(hidden_chrome: bool=False):
    '''
    Chromeを自動操作するためのChromeDriverを起動してobjectを取得する
    '''
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if hidden_chrome:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(f'--user-agent={USER_AGENT}') # ブラウザの種類を特定するための文字列
    options.add_argument('log-level=3') # 不要なログを非表示にする
    options.add_argument('--ignore-certificate-errors') # 不要なログを非表示にする
    options.add_argument('--ignore-ssl-errors') # 不要なログを非表示にする
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # 不要なログを非表示にする
    options.add_argument('--incognito') # シークレットモードの設定を付与
    
    # ChromeのWebDriverオブジェクトを作成する。
    service=Service(ChromeDriverManager().install())
    return Chrome(service=service, options=options)


def main():
    '''
    main処理
    '''
    search_keyword = input("検索キーワードを入力してください >>")
    # driverを起動
    driver = set_driver()
    # 検索キーワードをログとして残す
    log(f"[検索キーワード:{search_keyword}]")
    
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)
    
    '''
    ポップアップを閉じる
    ※余計なポップアップが操作の邪魔になる場合がある
      モーダルのようなポップアップ画面は、通常のclick操作では処理できない場合があるため
      excute_scriptで直接Javascriptを実行することで対処する
    '''
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    
    '''
    find_elementでHTML要素(WebElement)を取得する
    byで、要素を特定する属性を指定するBy.CLASS_NAMEの他、By.NAME、By.ID、By.CSS_SELECTORなどがある
    特定した要素に対して、send_keysで入力、clickでクリック、textでデータ取得が可能
    '''
    # 検索窓に入力
    driver.find_element(by=By.CLASS_NAME, value="topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element(by=By.CLASS_NAME, value="topSearch__button").click()
    
    '''
    find_elements(※複数形)を使用すると複数のデータがListで取得できる
    一覧から同一条件で複数のデータを取得する場合は、こちらを使用する
    '''
    
    # 空のDataFrame作成
    df = pd.DataFrame()
    # ログ用回数のカウント
    success = 0
    error = 0

    '''
    name_elmsには１ページ分の情報が格納されているのでforでループさせて１つづつ取り出して、Dataframeに格納する
    '''
    while True:
        name_elms = driver.find_elements(by=By.CSS_SELECTOR, value=".cassetteRecruit__heading.cassetteUseFloat")
        log(f"{len(name_elms)}件のデータ取得を開始します。")
        try:
            for name_elm in name_elms:
                company_name = name_elm.find_element(by=By.CSS_SELECTOR, value=".cassetteRecruit__name")
                copy = name_elm.find_element(by=By.CSS_SELECTOR, value=".cassetteRecruit__copy.boxAdjust").find_element(by=By.TAG_NAME, value="a")
                label = name_elm.find_element(by=By.CSS_SELECTOR, value=".labelEmploymentStatus")
                # DataFrameに対して辞書形式でデータを追加する
                df = df.append(
                    {"会社名": company_name.text, 
                    "コピー": copy.text,
                    "ラベル": label.text
                    }, ignore_index=True)
                success += 1
                log(f"[LOG:成功]{company_name.text}")
        except:
            log(f"[LOG:失敗]{company_name.text}")
            error += 1
            
        try:    
            driver.find_element(by=By.CSS_SELECTOR, value=".iconFont--arrowLeft").click()
            log("次のページに遷移しました。")
        except:
            print("最終ページまで到達しました。")
            log(f"[LOG:成功:{success}件、失敗:{error}件]最終ページまで到達しました。")
            break
    make_dir(OUTPUT_PATH)
    df.to_csv(EXP_CSV_PATH, encoding="utf-8_sig")

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()