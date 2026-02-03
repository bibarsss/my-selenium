from multiprocessing import Process
import os
from pathlib import Path
import re
import sqlite3

import pandas as pd
from common.read_pdf import read
from common.sqlite import safe_execute
from common.button import clickByText
from flow_types.baseWithoutExcel import WithoutExcelType
from browser.browser import Browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time


class GetSudType(WithoutExcelType):
    def label(self):
        return 'Получить суды с sud.kz'

    def table_name(self)->str:
        return 'get_sud'

    def migration(self):
        connection = sqlite3.connect(self.cfg.get('db_name'))

        cursor = connection.cursor()
        cursor.execute(f'''
            DROP TABLE IF EXISTS {self.table_name()}
            ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name()}(
                        id INTEGER PRIMARY KEY,
                        oblast TEXT,
                        podsudnost TEXT,
                        territory_podsudnost TEXT,
                        beneficiar TEXT,
                        beneficiar_bin TEXT
                    )
                            ''')
        connection.commit()
        connection.close()

    def start(self):
        self.migration()
        print('Парсим список областей...')
        browser = self.browser()
        browser.safe_get('https://sud.kz/rus/')

        menu = browser.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR,
             "aside.fixed-sidebar #block-menu-block-11 ul.menu"
             )))

        links = menu.find_elements(By.TAG_NAME, "a")

        regions = []
        for a in links:
            name = a.get_attribute("textContent").strip()
            url = a.get_attribute("href")
            regions.append({'oblast': name, 'link': url})

        browser.driver.quit()

        print('Проходим по областям для получения подсудностей и другие...')
        n_workers = int(self.cfg.get("count_process") or 1)
        chunks = self.chunk_list(regions, n_workers)

        processes = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self._process_regions, args=(chunk, wid))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()


        connection = sqlite3.connect(self.cfg.get('db_name'), timeout=30)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout = 5000;")
        connection.row_factory = sqlite3.Row

        rows = connection.execute(f"""
                                  SELECT oblast, podsudnost, territory_podsudnost, beneficiar, beneficiar_bin
                                  FROM {self.table_name()} ORDER BY oblast
                                    """).fetchall()

        connection.close()

        columns = ["Область", "Подсудность", "Тер подсудность", "бенефициар", "БИН"]
        output_path = "output.xlsx"

        df = pd.DataFrame(rows, columns=columns)
        df.to_excel(output_path, index=False)

    def _process_regions(self, regions, worker_id):
        print(f"[Worker {worker_id}] starting...")

        connection = sqlite3.connect(self.cfg.get('db_name'), timeout=30)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout = 5000;")
        connection.row_factory = sqlite3.Row

        browser = self.browser()
        for region in regions:
            browser.safe_get(region['link'] + 'rus/')
#
            for _ in range(10):
                if browser.htmlHasText('Сайты районных судов'):
                    break
                time.sleep(1)
            else:
                continue

            subregions = []

            try:
                select_element = browser.driver.find_element(By.ID, "edit-district")

                options = select_element.find_elements(By.TAG_NAME, "option")
                for opt in options:
                    value = opt.get_attribute("value").strip()
                    text = opt.get_attribute("textContent").strip()
                    if value != "0":
                        subregions.append({'oblast': region['oblast'], 'podsudnost': text, 'link': value})
            except Exception as e:
                continue

            for subregion in subregions:
                browser.safe_get(subregion['link'])
                for _ in range(10):
                    if browser.htmlHasText('Бенефициар'):
                        break
                    time.sleep(1)
                else:
                    continue

                beneficiar = ''
                beneficiar_bin = ''
                territory_podsudnost = ''

                try:
                    table = browser.driver.find_element(By.CSS_SELECTOR, "div.content table")
                    cells = table.find_elements(By.TAG_NAME, "td")

                    for i, cell in enumerate(cells):
                        text = cell.text.strip()
                        if "Бенефициар" in text and i + 1 < len(cells):
                            beneficiar = cells[i + 1].text.strip()
                        elif "БИН бенефициара" in text and i + 1 < len(cells):
                            beneficiar_bin = cells[i + 1].text.strip()

                    clickByText(browser, 'a', 'Подробнее...')
                    for _ in range(10):
                        time.sleep(1)
                        if not browser.tagWithTextHasClass('a', 'Подробнее...', 'progress-disabled'):
                            break
                    else:
                        continue

                    microdistricts = []

                    try:
                        article = browser.driver.find_element(By.CSS_SELECTOR, "div#colorbox article.node")

                        html_lines = article.get_attribute("innerHTML").split("<br>")

                        for line in html_lines:
                            clean_line = line.split("<")[0].strip()
                            if clean_line:
                                microdistricts.append(clean_line)

                    except:
                        pass

                    territory_podsudnost = '! '.join(microdistricts)

                except:
                    pass

                data = {
                    'podsudnost': subregion['podsudnost'],
                    'oblast': subregion['oblast'],
                    'territory_podsudnost': territory_podsudnost,
                    'beneficiar': beneficiar,
                    'beneficiar_bin': beneficiar_bin
                }

                columns = ", ".join(data.keys())
                placeholders = ", ".join(["?"] * len(data))
                values = tuple(data.values())

                query = f"INSERT INTO {self.table_name()} ({columns}) VALUES ({placeholders})"

                safe_execute(connection, query, values)

        connection.commit()
        connection.close()

        print(f"[Worker {worker_id}] Finished")
