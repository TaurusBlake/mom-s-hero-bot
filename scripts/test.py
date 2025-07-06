import requests
from bs4 import BeautifulSoup
import json
import re

def parse_ytower_recipe(url: str):
    """
    接收一個楊桃美食網的食譜 URL，爬取並解析其內容，
    返回一個包含結構化食譜資料的字典。
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.encoding = 'big5'
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- 1. 建立一個字典，用來存放所有解析出來的資料 ---
        recipe_data = {
            "name": None,
            "image_url": None,
            "core_ingredients": [],
            "full_ingredient_list": {},
            "steps": [],
            # 其他欄位給定預設空值
            "total_time": None,
            "difficulty": None,
            "cuisine_style": None,
            "servings": None,
            "key_equipment": None,
            "tips": None,
            "nutrition_info": None,
        }

        # --- 2. 解析基本資料：名稱與圖片 ---
        # [cite: 1] 根據 crawl.txt 的邏輯
        title_tag = soup.find('div', id='recipe_name')
        if title_tag:
            recipe_data['name'] = title_tag.get_text(strip=True)

        #  根據 html.txt 的結構，從 meta tag 獲取高品質圖片
        image_meta_tag = soup.find('meta', property='og:image')
        if image_meta_tag:
            recipe_data['image_url'] = image_meta_tag['content']
        
        # --- 3. 實施方案一：結構化地解析食材 ---
        
        # 首先，找到所有 class 為 'ingredient' 的 <ul> 區塊
        ingredient_uls = soup.find_all('ul', class_='ingredient')

        for ul in ingredient_uls:
            # 找到每個 <ul> 中的第一個 <li>，這就是我們的分組標題
            group_title_tag = ul.find('li')
            if not group_title_tag:
                continue # 如果沒有標題，跳過這個區塊
            
            group_title = group_title_tag.get_text(strip=True)

            # 找到這個 <ul> 中所有 class 為 'ingredient_name' 的 <span>
            items = ul.find_all('span', class_='ingredient_name')
            
            group_ingredients = {}
            for item in items:
                name_tag = item.find('a')
                amount_tag = item.find('span', class_='ingredient_amount')
                
                name = name_tag.get_text(strip=True) if name_tag else ''
                amount = amount_tag.get_text(strip=True) if amount_tag else ''

                if name: # 確保有抓到食材名稱
                    group_ingredients[name] = amount
            
            # 將解析出的群組食材存入「完整食材清單」
            recipe_data['full_ingredient_list'][group_title] = group_ingredients

            # 關鍵判斷：如果群組標題是【材　料】，就提取為「核心食材」
            if '【材　料】' in group_title:
                recipe_data['core_ingredients'].extend(group_ingredients.keys())

        # --- 4. 解析烹飪步驟 ---
        # [cite: 4] 根據 crawl.txt 的邏輯
        step_tags = soup.find_all('li', class_='step')
        recipe_data['steps'] = [step.get_text(separator='\n', strip=True) for step in step_tags]

        print(f"✅ 成功解析: {recipe_data['name']}")
        return recipe_data

    except requests.RequestException as e:
        print(f"❌ 請求失敗: {url}, 錯誤: {e}")
        return None
    except Exception as e:
        print(f"❌ 解析時發生未知錯誤: {url}, 錯誤: {e}")
        return None


if __name__ == "__main__":
    target_urls = [
        'https://www.ytower.com.tw/recipe/iframe-recipe.asp?seq=D01-0431', # 紅燒豆腐
        'https://www.ytower.com.tw/recipe/iframe-recipe.asp?seq=A01-0512', 
    ]

    all_recipes = []
    for url in target_urls:
        data = parse_ytower_recipe(url)
        if data:
            all_recipes.append(data)
    
    # 將爬取到的所有食譜資料寫入一個 JSON 檔案中
    output_filename = 'recipes_data.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_recipes, f, ensure_ascii=False, indent=4)

    print(f"\n爬取完成！共 {len(all_recipes)} 筆食譜已儲存至 {output_filename}")