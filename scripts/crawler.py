import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
import json
import time
import random

# ... parse_ytower_recipe_content 函式保持不變，它已經被驗證是正確的 ...
def parse_ytower_recipe_content(soup: BeautifulSoup, url: str) -> dict:
    # (此處省略，請沿用上一版的程式碼)
    recipe_data = {
        "name": None, "image_url": None, "core_ingredients": [],
        "full_ingredient_list": {}, "steps": [], "total_time": None,
        "difficulty": None, "cuisine_style": None, "servings": None,
        "key_equipment": None, "tips": None, "nutrition_info": None,
    }
    title_tag = soup.find('div', id='recipe_name')
    if title_tag:
        recipe_data['name'] = title_tag.get_text(strip=True)
    image_meta_tag = soup.find('meta', property='og:image')
    if image_meta_tag:
        recipe_data['image_url'] = image_meta_tag.get('content')
    ingredient_uls = soup.find_all('ul', class_='ingredient')
    for ul in ingredient_uls:
        group_title_tag = ul.find('li')
        if not group_title_tag: continue
        group_title = group_title_tag.get_text(strip=True)
        items = ul.find_all('span', class_='ingredient_name')
        group_ingredients = {}
        for item in items:
            name_tag = item.find('a')
            amount_tag = item.find('span', class_='ingredient_amount')
            name = name_tag.get_text(strip=True) if name_tag else ''
            amount = amount_tag.get_text(strip=True) if amount_tag else ''
            if name:
                group_ingredients[name] = amount
        recipe_data['full_ingredient_list'][group_title] = group_ingredients
        if '【材　料】' in group_title:
            recipe_data['core_ingredients'].extend(group_ingredients.keys())
    step_tags = soup.find_all('li', class_='step')
    recipe_data['steps'] = [step.get_text(separator='\n', strip=True) for step in step_tags]
    return recipe_data


async def fetch_and_parse(session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore, retries=2):
    async with semaphore:
        await asyncio.sleep(random.uniform(2.0, 5.0)) # 拉長並拉大隨機延遲範圍
        for attempt in range(retries):
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status >= 400: # 捕捉所有客戶端和伺服器錯誤
                        print(f"🟡 請求異常 (狀態碼: {response.status}) 於 {url}, 準備重試 (第 {attempt + 1}/{retries} 次)")
                        await asyncio.sleep(5 * (attempt + 1))
                        continue
                    
                    html_content = await response.text(encoding='big5-hkscs', errors='ignore')
                    soup = BeautifulSoup(html_content, 'html.parser')
                    data = await asyncio.to_thread(parse_ytower_recipe_content, soup, url)
                    
                    if not data or not data.get('name'):
                        # 即使狀態碼200，也可能回傳無效頁面，需增加判斷
                        print(f"⚠️ 內容解析為空: {url}")
                        return None

                    print('.', end='', flush=True)
                    return data
            except Exception as e:
                print(f"❌ 處理時發生錯誤: {url}, 錯誤: {e}")
                if attempt == retries - 1: return None
        return None

async def main():
    urls_file = 'unique_urls.txt'
    try:
        async with aiofiles.open(urls_file, mode='r', encoding='utf-8') as f:
            target_urls = [line.strip() for line in await f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"錯誤：找不到連結檔案 '{urls_file}'。")
        return

    print(f"從 {urls_file} 讀取到 {len(target_urls)} 個食譜連結...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    
    # --- 戰術參數調整 ---
    BATCH_SIZE = 50  # 每 50 個 URL 為一個批次
    CONCURRENT_REQUESTS = 5 # 非常保守的並發數
    
    all_recipes = []
    
    for i in range(0, len(target_urls), BATCH_SIZE):
        batch_urls = target_urls[i:i + BATCH_SIZE]
        print(f"\n--- 正在處理批次 {i // BATCH_SIZE + 1} (URL {i+1} - {i+len(batch_urls)}) ---")
        
        # 為每一個批次建立全新的 Session 和 Connector
        connector = aiohttp.TCPConnector(limit_per_host=5)
        semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
        
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            tasks = [asyncio.create_task(fetch_and_parse(session, url, semaphore)) for url in batch_urls]
            results = await asyncio.gather(*tasks)
            
            all_recipes.extend([res for res in results if res])
            
        # 一個批次結束後，隨機休息 8 到 15 秒
        sleep_duration = random.uniform(8, 15)
        print(f"\n批次完成，隨機休息 {sleep_duration:.2f} 秒...")
        await asyncio.sleep(sleep_duration)

    output_filename = 'recipes_data.json'
    async with aiofiles.open(output_filename, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(all_recipes, ensure_ascii=False, indent=4))

    print(f"\n全部爬取完成！共 {len(target_urls)} 個連結，成功解析 {len(all_recipes)} 筆食譜。")
    print(f"結果已儲存至 {output_filename}")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"總耗時: {end_time - start_time:.2f} 秒")