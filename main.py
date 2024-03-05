import schedule
import time
import requests

import database


def job():
    accounts = database.read_accounts()
    for account in accounts:
        if account.host != 'https://harmonyhomes.amocrm.ru/':
            continue
        try:
            session = requests.post(
                url='http://amocrm.avatarex.tech/create-tokens/',
                json={
                    'amo_host': account.host.strip(),
                    'amo_email': account.email.strip(),
                    'amo_password': account.password.strip()
                }).json()
            print(session)
            database.update_session(account, session['answer'])
        except Exception as e:
            print(e)


schedule.every(10).minutes.do(job)

print('completed')
while True:
    job()
    schedule.run_pending()
    time.sleep(1)
