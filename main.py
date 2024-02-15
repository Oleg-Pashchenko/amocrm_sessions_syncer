import schedule
import time
import requests

import database



def job():
    accounts = database.read_accounts()
    for account in accounts:
        try:
            session = requests.post(
                url='http://amocrm.avatarex.tech/create-tokens/',
                json={
                    'amo_host': account.host,
                    'amo_email': account.email,
                    'amo_password': account.password
                }).json()
            database.update_session(account, session['answer'])
        except Exception as e:
            print(e)


schedule.every(10).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
