import requests
from pprint import pprint
import json




class NotionAPI():
    def __init__(self, api_key, database_id):
        # config.py のなかに、"API_SECRET", "DATABASE_ID"の２つの変数を用意しておく
        self.notion_api_key = api_key
        self.database_id = database_id
        self.headers = {"Authorization": f"Bearer {self.notion_api_key}",
                "Content-Type": "application/json",
                "Notion-Version": "2021-05-13"}

        # インスタンス時に渡してもいいけど、めんどくさそう
        # 自分のDBの設定に応じて変更させる
        self.KEY_INFOS = [
            {
                "name": "title",    # Notionで定義した名前
                "property": "title",    # DBの形にあわさる
                "type": "text"
            },
            {
                "name": "url",
                "property": "url",    # DBの形にあわさる
                "type": None,
            },
            {
                "name": "tag",
                "property": "rich_text",
                "type": "text",
            },
        ]

    def get_request_url(self, end_point):
        return f'https://api.notion.com/v1/{end_point}'

    def get_db_check(self):
        response = requests.request('GET', 
            url=self.get_request_url(f'databases/{self.database_id}'),
            headers=self.headers)

        pprint(response.json())


    def make_query_body(self, pdf_info):
        # 一番重要なproperties(中身)を作る
        properties = {}
        for i in range(len(self.KEY_INFOS)):
            key_info = self.KEY_INFOS[i]
            key_name = key_info["name"]
            try:
                if (key_info["type"]):
                    this_type = [{key_info["type"]: {
                            # 名前を合わせる必要がある
                            "content": pdf_info[key_name],
                        }}]
                else:
                    this_type = pdf_info[key_name]
                properties[key_name] = {
                    key_info["property"]: this_type,
                }
            except KeyError:
                # pdf_infoがその情報を持ってない場合スキップ
                continue
        print(properties)

        # 生成したpropertiesを元に、リクエストボディを作る
        body = {
            "parent": {
                "database_id": self.database_id
            },
            "properties": properties
        }
        return body

    # bodyは他で作る必要がある
    def post_field(self, body):
        response = requests.request('POST', url=self.get_request_url('pages'), headers=self.headers, data=json.dumps(body))
        pprint(response.json())

    def post_pdf(self, pdf_info):
       body = self.make_query_body(pdf_info)
       self.post_field(body)
       # 上手くいったかどうかのチェックを行いたい？


if __name__ == "__main__":
    import config
    apiUser = NotionAPI(api_key=config.API_SECRET, database_id=config.DATABASE_ID)
    apiUser.get_db_check()

    # テスト用データ
    MOCK_PDF_INFOS = [
        {
            "title": "いたずら.pdf",
            "url": "https://nogizaka.com/itazura.saiko",
            "updated_at": "01/03",
            "tag": "かわいいの天才",
        },
        {
            "title": "乃木撮.pdf",
            "url": "https://nogizaka.com/nogisatsu.hogehoge",
            "updated_at": "01/03",
            "tag": "",
        },
        {
            "title": "日向撮.pdf",
            "url": "https://hinatazaka.com/hinatazaka.hogehoge",
            "updated_at": "01/03",
        },
        {
            "title": "さくら撮(仮).pdf",
            "url": "https://sakurazaka.com/sakurazaka.hogehoge",
            "updated_at": "01/03",
        },
        {
            "title": "光の角度.pdf",
            "url": "https://nogizaka.com/hikari",
            "updated_at": "01/03",
        },
    ]
    
    for pdf_info in MOCK_PDF_INFOS:
        apiUser.post_pdf(pdf_info)
