import time
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime


class FetchPdfNames():
    def __init__(self, driver_path):
        self.DRIVER_PATH = driver_path
        # Webページを取得して解析する
        self.DEFAULT_URL = "https://drive.google.com/drive/folders/12CQH0j9-MHLMDUL-Ku-BV15lqy_SlVrn"

    def get_pdf_names(self, url=None, doesUseBrowser=False):

        if not url:
            url = self.DEFAULT_URL

        #ヘッドレスモードでブラウザを起動するかどうか
        options = webdriver.ChromeOptions()
        if not doesUseBrowser:
            options.add_argument('--headless')

        driver = webdriver.Chrome(self.DRIVER_PATH, options=options)

        driver.get(url)

        # リスト表示に切り替えるためのボタンをクリックする
        btn_to_list = driver.find_element_by_xpath('//div[@data-tooltip="リスト表示"]')
        print(btn_to_list)
        btn_to_list.click()

        #
        # FIXME
        # 待つ時間を、DOMレンダリング完了後、までに変更する
        time.sleep(15)
        print('get HTML start')
        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        BASE_URL = "https://drive.google.com/file/d/"
        SUFFIX = "/view?usp=sharing"

        # 
        # FIXME
        # もっといいやり方ありそう...
        # divだけにしておくと、その子要素のspanが取れない
        divspans = soup.findAll(["div", "span"])

        pfd_infos = []
        for i in range(len(divspans)):
            div = divspans[i]
            if div.has_attr("data-id"):
                pdf_info = {}
                id = div["data-id"]
                pdf_url = BASE_URL + id + SUFFIX
                pdf_info["url"] = pdf_url
                
                inner_divs = div.findChildren("div" , recursive=True)

                for k in range(len(inner_divs)):
                    inner_div = inner_divs[k]
                    if inner_div.text[-4:] == '.pdf':
                        pdf_info["title"] = inner_div.text
                        break

                TRY_NUM = 120
                for j in range(i, i+TRY_NUM):
                    inner_span = divspans[j]
                    if inner_span.has_attr("data-tooltip"):
                        span_text = inner_span["data-tooltip"]
                        if span_text[:4] == "最終更新":
                            split_date = span_text.split(":")
                            if len(split_date) == 2:
                                # "最終更新 : 07/03" みたいな場合
                                updated_at = split_date[1].strip()
                            elif len(split_date) == 3:
                                # "最終更新 : 20:03" みたいな場合
                                updated_at = ':'.join(split_date[1:])
                            else:
                                continue

                            pdf_info["updated_at"] = updated_at

                            pfd_infos.append(pdf_info)
                            break

        driver.close()
        return pfd_infos

    # 何を引数に渡すのがいいんだろう？
    def get_new_pdf_infos_since(self, date):
        # pdf_date => 2021/08/01 or 13:44
        # compare_date => 2021/07/07
        def _is_new_info_by_date(pdf_date, compare_date):
            if ":" in pdf_date:
                return True
            
            pdf_datetime = datetime(int(pdf_date.split("/")[0]), int(pdf_date.split("/")[1]), int(pdf_date.split("/")[2]))
            compare_datetime = datetime(int(pdf_date.split("/")[0]), int(compare_date.split("/")[1]), int(compare_date.split("/")[2]))
            #
            # TODO
            # = を含むかどうかとか、もう少しちゃんと考えたい
            return pdf_datetime > compare_datetime
            
        results = []
        # 必要なpdfの情報を取得
        pdf_infos = self.get_pdf_names()
        for pdf_info in pdf_infos:
            pdfdate = pdf_info["updated_at"]
            if _is_new_info_by_date(pdfdate, date):
                results.append(pdf_info)
        
        return results


if __name__ == "__main__":
    import config

    fetcher = FetchPdfNames(driver_path=config.DRIVER_PATH)
    # res = fetcher.get_pdf_names(url=fetcher.DEFAULT_URL, doesUseBrowser=False)
    res = fetcher.get_new_pdf_infos_since("2021/07/07")
    print(res)
