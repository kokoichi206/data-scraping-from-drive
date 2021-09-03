from notion_api import NotionAPI
from drive import FetchPdfNames


DATE_FILE_PATH = './updated_date'

def main(is_debug):
    if not is_debug:
        import config
        api_key = config.API_SECRET
        database_id = config.DATABASE_ID
        driver_path = config.DRIVER_PATH
    elif is_debug:
        import config_debug
        api_key = config_debug.API_SECRET
        database_id = config_debug.DATABASE_ID
        driver_path = config_debug.DRIVER_PATH

    fetcher = FetchPdfNames(driver_path=driver_path)
    notion_user = NotionAPI(api_key=api_key, database_id=database_id)

    # main function
    if not is_debug:
        release_mode(fetcher, notion_user)
    else:
        # Do Something
        debug_mode()

def debug_mode():
    pass

def release_mode(fetcher, notion_user):
    last_updated_at = get_last_updated_date()
    pdf_infos = fetcher.get_new_pdf_infos_since(last_updated_at)
    for pdf_info in pdf_infos:
        print(pdf_info)
        notion_user.post_pdf(pdf_info)
    # 更新日をファイルに追記
    update_date_file()

# 最終更新日だけ返す
def get_last_updated_date():
    with open(DATE_FILE_PATH) as f:
        # 全行読む
        lines = f.readlines()

    # 後ろから1行だけ返す
    return lines[-1]

def update_date_file():
    with open(DATE_FILE_PATH, mode='a') as f:
        f.write(f'\n{get_today()}')

# 2021/08/05 の形で ~今日の~ 日付を取得する
def get_today():
    import datetime

    dt_now = datetime.datetime.now()
    return dt_now.strftime('%Y/%m/%d')


if __name__ == "__main__":
    is_debug = False    # 本番用のデータ使うかどうか
    main(is_debug)
    # print(get_last_updated_date())
    # update_date_file()
