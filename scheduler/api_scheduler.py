import schedule
import os, time, json
import requests

from dotenv import load_dotenv
load_dotenv()

from email_service import send_email

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fastapi_host=os.getenv('fastapi')
email_reciever=os.getenv('SMTP_GMAIL_EMAIL_RECIEVER')

def make_api_call():

    logger.info('Getting short squeeze results...')

    max_retries = 2
    for retry in range(max_retries + 1):
        try:
            stock_results_response = requests.get(f'http://{fastapi_host}:8000/api/stock-results')
            stock_results_response.raise_for_status()  # Raises an exception for non-2xx status codes

            # Process the response data here
            stock_results = stock_results_response.json()
            logger.info('Results recieved.')
            return stock_results

        except requests.RequestException as e:
            logger.info(f"API call failed: {str(e)}")
            if retry < max_retries:
                logger.info(f"Retrying... (attempt {retry + 1}/{max_retries})")
            else:
                raise ValueError("API call failed after multiple attempts.") 

def update_database(results:dict):
    logger.info('Attemting to Update Database')

    body=json.dumps(results)
    headers = {
        'Content-Type': 'application/json'
    }

    requests.post(url=f'http://{fastapi_host}:8000/api/insert-mysql', headers=headers, data=body)


def job():
    try:
        logger.info("Making API call...")
        results = make_api_call()
        update_database(results)
        send_email(email_reciever, 'PROJ SHRTSQZ - SUCCESS', 'Today, the job has ran successfully. Nice work')
    except Exception as e:
        logger.info("Job Failed...")
        send_email(email_reciever, 'PROJ SHRTSQZ - FAILED', f'Today, the job has failed. See error here: {e}')


# Schedule the job to run every weekday at 7 PM (11 PM UTC)
schedule.every().monday.at("23:00").do(job)
schedule.every().tuesday.at("23:00").do(job)
schedule.every().wednesday.at("23:00").do(job)
schedule.every().thursday.at("23:00").do(job)
schedule.every().friday.at("23:00").do(job)

from datetime import datetime

logger.info("Date/Time: " + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

while True:
    schedule.run_pending()
    time.sleep(1)