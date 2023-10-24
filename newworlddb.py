from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv
import time
import os
import pandas as pd
def save_to_csv(row):
    title = row[0]
    item_type = row[1]
    perk1, perk2, perk3, perk4, perk5, perk6 = row[2]
    dropped_by = row[3]
    comments = row[4]
    if not os.path.exists('data.csv'):
        with open("data.csv", "w", newline="") as csvfile:
            fieldnames = ["name", "item_type", "perk1", "perk2", "perk3", "perk4", "perk5", "perk6", "dropped_by", "comments"]
            writer = csv.writer(csvfile, dialect='excel')
            writer.writerow(fieldnames)
            writer.writerow([title, item_type, perk1, perk2, perk3, perk4, perk5, perk6, dropped_by, comments])
    else:
        with open('data.csv', 'a', newline="") as csvfile:
            writer = csv.writer(csvfile, dialect='excel')
            writer.writerow([title, item_type, perk1, perk2, perk3, perk4, perk5, perk6, dropped_by, comments])


def get_data(url):
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless") # disable this to view whats happening
    options.add_argument('--lang=en')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    def find_elem_or_false(parent, selector, num='single'):
        try:
            if num == 'single':
                WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                elem = parent.find_element(By.CSS_SELECTOR, selector)
                return elem
            else:
                WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                elem = parent.find_elements(By.CSS_SELECTOR, selector)
                return elem
        except:
            return False

    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h1.text-shadow.svelte-6xe72n")))
    title = driver.find_element(By.CSS_SELECTOR, "h1.text-shadow.svelte-6xe72n").text

    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span.h6.mb-0.text-shadow > span.d-flex.justify-content-between > span")))
    item_type = driver.find_element(By.CSS_SELECTOR, "span.h6.mb-0.text-shadow > span.d-flex.justify-content-between > span").text.strip()

    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.perk-info.svelte-8zj9mg")))
    perks = driver.find_elements(By.CSS_SELECTOR, "div.perk-info.svelte-8zj9mg")
    perks_list = []
    for perk in perks:
        info = find_elem_or_false(perk, "a")
        if not info:
            info = perk.find_element(By.CSS_SELECTOR, "span.perk-name.svelte-8zj9mg")
        if len(perks_list) == 6:
            perks_list.pop(0)
        perks_list.append(info.text)
    if len(perks_list) < 6:
        perks_list.append(None) 
    
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.svelte-k2fu6v")))
    buttons = driver.find_elements(By.CSS_SELECTOR, "div.nav-item.svelte-k2fu6v")
    scroll = driver.find_element(By.CSS_SELECTOR, ".eg-banner-holder.clear-holder")
    driver.execute_script("arguments[0].scrollIntoView();", scroll)
    dropped_by = None
    comments_area = None
    for button in buttons:
        if "Comments" in button.text:
            comments_area = button.find_element(By.CSS_SELECTOR, "button.svelte-k2fu6v")
        if "Dropped By" in button.text or "Gathered From" in button.text:
            dropped_button = button.find_element(By.CSS_SELECTOR, "button.svelte-k2fu6v")
            dropped_button.click()
            WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a.table-item-name.svelte-18wwooz")))
            link = find_elem_or_false(driver, "a.table-item-name.svelte-18wwooz")
            dropped_by = [link.get_attribute('href'), link.text] if link else None

    comments_strings = []
    if not dropped_by and comments_area:
        time.sleep(3)
        comments_area.click()

        comments = find_elem_or_false(driver, ".comment-body.svelte-56squ4", num="multiple")
        if comments:
            for comment in comments:
                comment = find_elem_or_false(comment, "p")
                if comment: comments_strings.append(comment.text)

    c_strings = comments_strings if comments_strings else None
    dropped = f'=HYPERLINK("{dropped_by[0]}", "{dropped_by[1]}")' if dropped_by and isinstance(dropped_by[0], str) and isinstance(dropped_by[1], str) else None
    save_to_csv([title, item_type, perks_list, dropped, c_strings])

    driver.quit()


def main(url):
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless") # disable this to view whats happening
    options.add_argument('--lang=en')
    options.add_argument("--disable-notifications")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1600, 900)
    driver.get(url)

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ellipsis .svelte-137gzfr")))
    variable = driver.find_elements(By.CSS_SELECTOR, ".ellipsis .svelte-137gzfr")

    for el in variable:
        if os.path.exists('data.csv'):
            df = pd.read_csv('data.csv', encoding="iso-8859-1", encoding_errors="ignore")
            if el.text in df['name'].values:
                continue
        try:
            get_data(el.get_attribute("href"))
        except: pass
        # get_data(el.get_attribute("href"))
        # break
    driver.quit()


if __name__ == "__main__":
    link = 'https://nwdb.info/db/items/page/1?rarity=100&sort=name_asc'
    main(link)