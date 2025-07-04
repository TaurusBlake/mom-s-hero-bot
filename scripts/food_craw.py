from bs4 import BeautifulSoup
import requests
import os

url = 'https://www.ytower.com.tw/recipe/iframe-recipe.asp?seq=D01-0431'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
response = requests.get(url, headers=headers)
response.encoding = 'big5'  # 有些可能是 'big5-hkscs'，但先試 big5

soup = BeautifulSoup(response.text, 'html.parser')

title = soup.find('div', id='recipe_name')
if title:
    print(f'食譜名稱: {title.get_text(strip=True)}')

# --- 定位圖片和標題 ---
main_pic = soup.find('div', id='recipe_mainpic')

if main_pic:
    img_tag = main_pic.find('img')
    if img_tag and 'src' in img_tag.attrs:
        image_url = img_tag['src']
        print(f"成功解析到圖片網址: {image_url}")

# --- 下載圖片 ---
if image_url:
    # 從原始圖片 URL 中取得副檔名 (例如 .jpg)
    #    os.path.splitext 會將路徑切成 (主檔名, 副檔名)
    file_extension = os.path.splitext(image_url)[1]

    # 組合出最終的、乾淨的檔案名稱
    final_file_name = f"{title.get_text(strip=True)}{file_extension}"
    
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        with open(final_file_name, 'wb') as f:
            f.write(response.content)
        
        print(f"圖片成功儲存至: {os.path.abspath(final_file_name)}")

    except requests.exceptions.RequestException as e:
        print(f"下載圖片時發生錯誤: {e}")
    except IOError as e:
        print(f"儲存檔案時發生錯誤: {e}")

recipe = soup.find_all('span', class_='ingredient_name')
for item in recipe:
    # 食材名稱
    name_tag = item.find('a')
    name = name_tag.get_text(strip=True) if name_tag else''

    # 食材數量
    amount_tag = item.find('span', class_='ingredient_amount')
    amount = amount_tag.get_text(strip=True) if amount_tag else ''
    
    if name:
        print(f'食材名稱: {name}, 數量: {amount}')

# 使用 find_all 尋找所有 class="step" 的 <li> 標籤
# 這會回傳一個包含所有符合條件標籤的列表
step_tags = soup.find_all('li', class_='step') # 

# 建立一個空列表，用來存放每個步驟的文字內容
steps_list = []

# 遍歷所有找到的 <li> 標籤
for step in step_tags:
    # 提取標籤內的文字，使用 .strip() 去除前後多餘的空白
    # 使用 get_text(separator='\\n') 可以將 <br> 轉換為換行符，保持格式
    text = step.get_text(separator='\n', strip=True)
    
    # 將處理好的文字加入到我們的列表中
    steps_list.append(text)

print(steps_list)