import os

# --- 設定區 ---
# 使用一個列表來存放所有要處理的檔案名稱
# 這樣未來若有增減，只需修改這個列表即可
INPUT_FILENAMES = [
    'ytower_recipe_urls.txt',
    'ytower_recipe_urls1.txt',
    'ytower_recipe_urls2.txt'
]
OUTPUT_FILENAME = 'unique_urls.txt'

# --- 核心邏輯 ---

def process_and_save_unique_urls():
    """
    讀取多個檔案，提取不重複的連結，並儲存到新檔案。
    """
    # 1. 初始化一個空的集合，用來存放不重複的連結
    unique_urls = set()
    files_processed_count = 0
    
    print(">>> 開始讀取檔案並提取連結...")

    # 2. 遍歷所有指定的輸入檔案
    for filename in INPUT_FILENAMES:
        try:
            # 使用 'with' 陳述式能確保檔案在使用後被正確關閉
            # 指定 encoding='utf-8' 來避免在不同系統上可能出現的亂碼問題
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    # .strip() 會移除每行前後的空白字元 (包含換行符 \n)
                    # 這是非常關鍵的一步，可以避免 'url' 和 'url\n' 被視為不同
                    url = line.strip()
                    
                    # 確保不是空行才加入集合
                    if url:
                        unique_urls.add(url)
                
                print(f"  [成功] 已處理檔案: {filename}")
                files_processed_count += 1

        except FileNotFoundError:
            print(f"  [警告] 找不到檔案 '{filename}'，已跳過。")
        except Exception as e:
            print(f"  [錯誤] 處理 '{filename}' 時發生錯誤: {e}")

    # 檢查是否有成功處理任何檔案
    if files_processed_count == 0:
        print("\n>>> 沒有成功處理任何檔案，程式結束。")
        return

    # 3. 將不重複的連結寫入新檔案
    print("\n>>> 提取完成！正在寫入不重複的連結...")

    # 為了讓輸出檔案的內容順序固定，可以先將 set 轉為 list 並排序
    # 如果不在意順序，可以直接遍歷 unique_urls 集合
    sorted_urls = sorted(list(unique_urls))

    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            for url in sorted_urls:
                # 加上換行符，讓每個連結佔一行
                f.write(url + '\n')
    except Exception as e:
        print(f"  [錯誤] 寫入檔案 '{OUTPUT_FILENAME}' 時發生錯誤: {e}")
        return

    # 4. 完成後給予使用者最終的回饋
    print("\n🎉 全部完成！")
    print(f"共處理了 {files_processed_count} 個輸入檔案。")
    print(f"總共整理出 {len(sorted_urls)} 個不重複的連結。")
    print(f"結果已儲存至檔案: {OUTPUT_FILENAME}")

# --- 執行主程式 ---
if __name__ == "__main__":
    process_and_save_unique_urls()
