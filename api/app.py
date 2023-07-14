# main.py
import os, re
from typing import List
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options as ChromeOptions

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

class Result(BaseModel):
    asOfDate: str
    ticker: str
    company: str
    sector: str
    industry: str
    shares_float: str
    float_short_perct: float
    short_ratio: float
    high_50d_perct: float
    high_52w_perct: float
    change_open_perct: float
    prev_close: float
    current_price: float

class Data(BaseModel):
    count: int
    results: List[Result]

@app.get("/api/stock-results")
def get_stock_results():

    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}

    driver = webdriver.Chrome(options=chrome_options)

    driver.get('https://finviz.com/screener.ashx?v=152&f=sh_short_high,ta_highlow50d_b0to10h&ft=3&o=-shortinterestratio&c=1,2,3,4,25,30,31,55,57,60,81,65')

    date_field = driver.find_element(By.CSS_SELECTOR, "#time > div > div > span").text
    count_field =  driver.find_element(By.CSS_SELECTOR, "td.count-text:nth-child(1)")

    current_date = datetime.now().date()
    formatted_date = current_date.strftime('%Y-%m-%d')    

    text = count_field.text
    match = re.search(r'(\d+)\s+Total', text)

    if match:
        number = match.group(1)

    page_count = int(number)//20

    data_list = []

    while page_count >= 0:

        table = driver.find_element(By.CSS_SELECTOR, '.table-light > tbody:nth-child(1)')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        num_rows = len(rows) - 1
        tr_count = 2

        for i in range(1, num_rows+1):

            item_dict = {}

            ticker = rows[i].find_element(By.CSS_SELECTOR, f"tr:nth-child({tr_count}) > td:nth-child(1) > a:nth-child(1)").text
            company = rows[i].find_element(By.CSS_SELECTOR, f"tr:nth-child({tr_count}) > td:nth-child(2) > a:nth-child(1)").text
            sector = rows[i].find_element(By.CSS_SELECTOR, f"tr:nth-child({tr_count}) > td:nth-child(3) > a:nth-child(1)").text
            industry = rows[i].find_element(By.CSS_SELECTOR, f"tr:nth-child({tr_count}) > td:nth-child(4) > a:nth-child(1)").text
            shares_float = rows[i].find_element(By.CSS_SELECTOR, f"tr:nth-child({tr_count}) > td:nth-child(5) > a:nth-child(1)").text
            float_short_perct = rows[i].find_element(By.CSS_SELECTOR, f"tr:nth-child({tr_count}) > td:nth-child(6) > a:nth-child(1)").text
            float_short_perct = float("{:.6f}".format(float(float_short_perct.rstrip("%"))/100))
            short_ratio = rows[i].find_element(By.CSS_SELECTOR, f"tr:nth-child({tr_count}) > td:nth-child(7) > a:nth-child(1)").text
            short_ratio = float(short_ratio)
            high_50d_perct = rows[i].find_element(By.CSS_SELECTOR, f"tr:nth-child({tr_count}) > td:nth-child(8) > a:nth-child(1)").text
            high_50d_perct = float("{:.6f}".format(float(high_50d_perct.rstrip("%"))/100))
            high_52w_perct = rows[i].find_element(By.CSS_SELECTOR, f"tr:nth-child({tr_count}) > td:nth-child(9) > a:nth-child(1)").text
            high_52w_perct = float("{:.6f}".format(float(high_52w_perct.rstrip("%"))/100))
            change_open_perct = rows[i].find_element(By.CSS_SELECTOR, f"tr:nth-child({tr_count}) > td:nth-child(10) > a:nth-child(1)").text
            change_open_perct = float("{:.6f}".format(float(change_open_perct.rstrip("%"))/100))
            prev_close = rows[i].find_element(By.CSS_SELECTOR, f"tr:nth-child({tr_count}) > td:nth-child(11) > a:nth-child(1)").text
            prev_close = float(prev_close)
            current_price = rows[i].find_element(By.CSS_SELECTOR, f"tr:nth-child({tr_count}) > td:nth-child(12) > a:nth-child(1)").text
            current_price = float(current_price)

            item_dict = {
                'asOfDate': formatted_date,
                'ticker': ticker,
                'company': company,
                'sector': sector,
                'industry': industry,
                'shares_float': shares_float,
                'float_short_perct': float_short_perct,
                'short_ratio': short_ratio,
                'high_50d_perct': high_50d_perct,
                'high_52w_perct' : high_52w_perct,
                'change_open_perct' : change_open_perct,
                'prev_close' : prev_close,
                'current_price': current_price
            }

            data_list.append(item_dict)
            tr_count+=1
        
        if page_count != 0:
            next_page_button = driver.find_element(By.CSS_SELECTOR, "a.align-middle > svg:nth-child(1)").click()
        page_count-=1

    response = {
        "count": number,
        "results": data_list
    }

    return response

@app.post("/api/insert-mysql")
def process_data(data: Data):
    import mysql.connector

    # Access the received data
    count = data.count
    results = data.results

    MYSQL_HOST=os.getenv('MYSQL_HOST')
    MYSQL_USER=os.getenv('MYSQL_USER')
    MYSQL_PASSWORD=os.getenv('MYSQL_PASSWORD')
    MYSQL_DATABASE=os.getenv('MYSQL_DATABASE')
    MYSQL_TABLE=os.getenv('MYSQL_TABLE')

    # Connect to the MySQL database
    db = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    # Create a cursor object to interact with the database
    cursor = db.cursor()

    converted_list = [
        (
            result.asOfDate,
            result.ticker,
            result.company,
            result.sector,
            result.industry,
            result.float_short_perct,
            result.short_ratio,
            result.high_50d_perct,
            result.high_52w_perct,
            result.change_open_perct,
            result.prev_close,
            result.current_price,
            result.shares_float
        )
        for result in results
    ]    

    # SQL statement for inserting records
    sql = f"INSERT INTO {MYSQL_TABLE} (asOfDate, ticker, company, sector, industry, float_short_perct, short_ratio, high_50d_perct, high_52w_perct, change_open_perct, prev_close, current_price, shares_float) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    # Insert multiple records into the table
    cursor.executemany(sql, converted_list)

    # Commit the changes to the database
    db.commit()

    # Close the cursor and database connection
    cursor.close()
    db.close()

    return {"message": "Data Inserted Successfully"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)