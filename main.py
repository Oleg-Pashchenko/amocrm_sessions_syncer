import schedule
import time
import requests

import database


def job():
    accounts = database.read_accounts()
    for account in accounts:
        if 'bitrix24.ru' in account['host']:
            continue
        try:
            if '@' in account['email']:
                session = requests.post(
                    url='http://amocrm.avatarex.tech/create-tokens/',
                    json={
                        'amo_host': account['host'].strip(),
                        'amo_email': account['email'].strip(),
                        'amo_password': account['password'].strip()
                    }).json()
            else:
                data = {
                        'amo_host': account['host'].strip(),
                        'refresh_token': account['email'].strip(),
                        'client_id': account['client_id'],
                        'client_secret': account['client_secret']
                    }
                session = requests.post(
                    url='http://amocrm.avatarex.tech/add-tokens/',
                    json=data).json()
            database.update_session(account, session['answer'])
            print(account['host'])
        except Exception as e:
            print(account['host'], 'error', e)


schedule.every(10).minutes.do(job)

job()
print('completed')

while True:
    schedule.run_pending()
    time.sleep(1)
