#%% FM
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# 設置 WebDriver
driver = webdriver.Chrome()
driver.get("https://www.family.com.tw/Marketing/zh/Map")
wait = WebDriverWait(driver, 10)

# **切換到 iframe**
iframe = wait.until(EC.presence_of_element_located((By.ID, "map-iframe")))
driver.switch_to.frame(iframe)

# **取得所有縣市**
taiwan_map = wait.until(EC.presence_of_element_located((By.ID, "taiwanMap")))
city_elements = taiwan_map.find_elements(By.TAG_NAME, "div")

# **存儲資料**
data = []

# **遍歷所有縣市**
for city in city_elements:
    city_name = city.text.strip()

    print(f"👉 開始爬取縣市：{city_name}")
    city.click()
    time.sleep(2)  # 等待頁面更新

    # **取得區域列表**
    show_town_list = wait.until(EC.presence_of_element_located((By.ID, "showTownList")))
    town_elements = show_town_list.find_elements(By.TAG_NAME, "li")
    # **遍歷所有區域**
    for town in town_elements:
        town_name = town.text.strip()
        
        print(f"   🔹 開始爬取區域：{town_name}")
        town.click()
        time.sleep(2)  # 等待頁面更新

        # **取得最大頁數**
        page_bu_content = wait.until(EC.presence_of_element_located((By.ID, "page_bu_content")))
        page_numbers = page_bu_content.find_elements(By.TAG_NAME, "li")
        max_page_number = len(page_numbers)  # 最大頁數

        # **爬取所有頁面的店鋪資訊**
        current_page = 1
        while current_page <= max_page_number:
            print(f"      📝 正在爬取第 {current_page} 頁的資料...")
            
            # **爬取店鋪資訊**
            table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "graybigbox")))
            rows = table.find_elements(By.TAG_NAME, "tr")

            # **解析資料**
            for row in rows[1:]:  # 跳過標題列
                tds = row.find_elements(By.TAG_NAME, "td")
                
                # 檢查 tds 長度確保資料正確
                if len(tds) < 5:
                    continue

                store_name = tds[0].text.strip()
                details = tds[1].text.strip()

                # 透過關鍵字提取資料
                store_number = ""
                service_number = ""
                address = ""
                phone = ""

                # 解析 '店舖號：019762'
                if "店舖號：" in details:
                    store_number = details.split("店舖號：")[1].split()[0]
                # 解析 '服務編號：15012'
                if "服務編號：" in details:
                    service_number = details.split("服務編號：")[1].split()[0]
                # 解析 '地址：宜蘭縣宜蘭市大福路一段４３號，４５號'
                if "地址：" in details:
                    address = details.split("地址：")[1].split("電話：")[0].strip()
                # 解析 '電話：03-9108022 , 03-9301476'
                if "電話：" in details:
                    phone = details.split("電話：")[1].strip()

                # 檢查是否所有資料都有效
                if store_name and store_number and address:
                    data.append([city_name, town_name, store_name, store_number, service_number, address, phone])

            # **點擊下一頁按鈕 (每次都重新抓取)**
            if current_page < max_page_number:
                page_bu_content = wait.until(EC.presence_of_element_located((By.ID, "page_bu_content")))  # 重新取得
                page_numbers = page_bu_content.find_elements(By.TAG_NAME, "li")
                next_button = page_numbers[current_page]  # 確保拿到當前頁面的下一頁按鈕
                next_button.click()
                time.sleep(2)  # 等待翻頁
                current_page += 1
            else:
                break  # 如果是最後一頁，退出迴圈

# **儲存資料到 CSV**
df = pd.DataFrame(data, columns=["縣市", "區域", "店鋪名稱", "店舖號", "服務編號", "地址", "電話"])
save_p = r'C:\Users\FM20250202.csv'
df.to_csv(save_p, index=False, encoding="utf-8-sig")

print("✅ 完成爬取！資料已儲存為 familymart_stores.csv")

# **關閉 WebDriver**
driver.quit()

