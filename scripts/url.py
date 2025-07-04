import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def collect_recipe_urls(base_api_url: str, output_file: str):
    """
    從一個基礎的分類 API URL 開始，自動翻頁並收集所有食譜的獨立連結。

    :param base_api_url: 不包含 page 參數的基礎 API URL。
    :param output_file: 用來儲存結果的 txt 檔案名稱。
    """
    all_urls = set()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    
    page = 1
    while True: # 使用一個無限循環
        # 組合出當前要請求的頁面 URL
        current_url = f"{base_api_url}&page={page}"
        
        print(f"正在掃描 API 頁面: {current_url}")
        try:
            response = requests.get(current_url, headers=headers)
            # 注意：楊桃網的 pager.asp 回傳的可能是 Big5 編碼的 HTML 片段
            response.encoding = 'big5'
            response.raise_for_status()

            # 檢查回傳的內容是否為空或非常短，這可能代表沒有內容了
            if len(response.text.strip()) < 50: # 用一個很小的長度作為閾值
                print("偵測到頁面內容為空，應已到達最後一頁。")
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            recipe_links = soup.find_all('a', href=lambda href: href and 'iframe-recipe.asp' in href)

            # 如果這一頁找不到任何食譜連結，也代表結束了
            if not recipe_links:
                print("此頁面已無食譜連結，判定為最後一頁。")
                break

            found_new = False
            for link in recipe_links:
                absolute_url = urljoin(base_api_url, link['href'])
                if absolute_url not in all_urls:
                    all_urls.add(absolute_url)
                    found_new = True
            
            # 如果這一頁沒有找到任何「新」的連結，也可能代表結束了（以防伺服器重複回傳最後一頁）
            if not found_new:
                print("此頁面未發現新的連結，可能已到達終點。")
                break

            # 準備下一輪
            page += 1
            # 加上一個短暫的延遲，做一個有禮貌的爬蟲
            time.sleep(0.5)

        except requests.RequestException as e:
            print(f"請求 API 時出錯: {e}")
            break

    # 將收集到的所有連結寫入檔案
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in sorted(list(all_urls)):
            f.write(url + '\n')
            
    print(f"\n連結收集完成！共找到 {len(all_urls)} 個不重複的食譜連結。")
    print(f"結果已儲存至: {output_file}")


if __name__ == "__main__":
    # 我們將 URL 拆成不含 page 參數的基礎部分
    BASE_API_URL = 'https://www.ytower.com.tw/recipe/pager.asp?KIND=%A5D%B5%E6&IsMobile=0'
    OUTPUT_FILENAME = 'ytower_recipe_urls.txt'
    collect_recipe_urls(base_api_url=BASE_API_URL, output_file=OUTPUT_FILENAME)