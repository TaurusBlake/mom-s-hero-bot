# 檔案位置: scripts/crawler.py

import requests
from bs4 import BeautifulSoup
import json

def get_recipe_data(url: str) -> dict:
    """
    接收一個食譜頁面的 URL，爬取並解析其內容，
    返回一個包含結構化食譜資料的字典。
    """
    print(f"正在爬取: {url}")
    try:
        # 1. 發送 GET 請求取得網頁 HTML 內容
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # 如果請求失敗 (e.g., 404 Not Found), 拋出異常

        # 2. 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 3. 根據網頁結構，萃取我們在 project_plan.md 中定義的「黃金資料欄位」
        #    注意：下方的 'h1', '.recipe-image', '.ingredient-list li' 等都是 CSS 選擇器，
        #    需要根據目標網站的實際 HTML 結構進行調整。
        
        recipe = {
            "name": soup.find('h1', class_='recipe-title').text.strip(),
            "image_url": soup.find('img', class_='recipe-image')['src'],
            "core_ingredients": [li.text.strip() for li in soup.select('.core-ingredients-list li')],
            "full_ingredient_list": {
                group.find('h3').text.strip(): [
                    li.text.strip() for li in group.select('.ingredient-list li')
                ]
                for group in soup.select('.ingredient-group')
            },
            "steps": [step.text.strip() for step in soup.select('.steps-section ol li')],
            "total_time": int(soup.find('span', class_='total-time').text.replace(' 分鐘', '').strip()),
            "difficulty": len(soup.select('.difficulty-stars .star-filled')), # 透過計算星星數量來量化
            "cuisine_style": soup.find('span', class_='cuisine-style').text.strip(),
            "servings": soup.find('span', class_='servings').text.strip(),
            "key_equipment": [equip.text.strip() for equip in soup.select('.key-equipment-list li')],
            "tips": [tip.text.strip() for tip in soup.select('.tips-section ul li')],
            # 營養成分是次要目標，如果不存在則設為 None
            "nutrition_info": {
                item.find(class_='nutrient-name').text.strip(): item.find(class_='nutrient-value').text.strip()
                for item in soup.select('.nutrition-table .nutrient-item')
            } if soup.select_one('.nutrition-table') else None,
        }
        
        print(f"成功解析: {recipe['name']}")
        return recipe

    except requests.RequestException as e:
        print(f"請求失敗: {url}, 錯誤: {e}")
    except Exception as e:
        print(f"解析失敗: {url}, 錯誤: {e}")
    
    return None

if __name__ == "__main__":
    # 假設我們有一個想要爬取的食譜 URL 列表
    target_urls = [
        "http://fake-recipe-website.com/recipe/1", # 範例 URL 1
        "http://fake-recipe-website.com/recipe/2", # 範例 URL 2
        "http://fake-recipe-website.com/recipe/3", # 範例 URL 3
    ]

    all_recipes = []
    for url in target_urls:
        data = get_recipe_data(url)
        if data:
            all_recipes.append(data)
    
    # 4. 將爬取到的所有食譜資料寫入一個 JSON 檔案中
    #    這便於我們進行下一步的資料清洗與匯入資料庫
    output_filename = 'recipes_data.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_recipes, f, ensure_ascii=False, indent=4)

    print(f"\n爬取完成！共 {len(all_recipes)} 筆食譜已儲存至 {output_filename}")