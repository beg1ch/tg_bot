import sqlite3
from datetime import datetime
import random

conn = sqlite3.connect('med_bot.db',
                       detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
cursor = conn.cursor()


def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS user
    (id INTEGER PRIMARY KEY, 
    user_name TEXT NOT NULL
    )''')

    # cursor.execute('''CREATE TABLE IF NOT EXISTS medicine
    # (medicine_name TEXT PRIMARY KEY,
    #  taking_time_1 TEXT DEFAULT NULL,
    #  taking_time_2 TEXT DEFAULT NULL,
    #  taking_time_3 TEXT DEFAULT NULL,
    #  id INTEGER NOT NULL,
    #  FOREIGN KEY(id) REFERENCES user(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS heart_rate
    (date DATE,
     time TIMESTAMP,
     heart_rate_indicator INTEGER NOT NULL,
     id INTEGER NOT NULL,
     FOREIGN KEY(id) REFERENCES user(id));''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS request_response
    (date DATE,
    time TIME,
    user_name TEXT NOT NULL,
    request TEXT NOT NULL,
    response TEXT NOT NULL,
    id NOT NULL,
    FOREIGN KEY(id) REFERENCES user(id)
    );
    ''')
    conn.commit()


def insert_request_response(date: object = None, time: object = None, user_name: object = None, request: object = None, response: object = None, user_id: object = None) -> None:
    cursor.execute('INSERT OR IGNORE INTO request_response(date, time, user_name, request, response, id) VALUES(?, ?, ?, ?, ?, ?)',
                   (date, time, user_name, request, response, user_id))
    conn.commit()


def insert_into_user(user_id=None, name=None) -> None:
    cursor.execute('INSERT OR IGNORE INTO user(id, user_name) VALUES(?, ?)', (user_id, name,))
    conn.commit()


def insert_into_hr(date=None, time=None, heart_rate_indicator=None, user_id=None) -> None:
    cursor.execute('INSERT OR IGNORE INTO heart_rate(date, time, heart_rate_indicator, id) VALUES(?, ?, ?, ?)',
                   (date, time, heart_rate_indicator, user_id,))
    conn.commit()


def get_hr_for_some_day(date: object = None, user_id: object = None) -> object:
    cursor.execute('SELECT time, heart_rate_indicator FROM heart_rate WHERE date=? AND id=?', (date, user_id))
    answer = cursor.fetchall()
    if answer:
        return answer
    else:
        pass


def get_agr_val_from_hr(user_id=None, start_date=None, end_date=None):
    cursor.execute('''
    SELECT AVG(heart_rate_indicator), MAX(heart_rate_indicator), MIN(heart_rate_indicator) 
    FROM heart_rate 
    WHERE (date BETWEEN ? AND ?) AND id=? 
    GROUP BY id''',
                   (start_date, end_date, user_id))
    answer = cursor.fetchall()
    if answer:
        avg, max_val, min_val = map(lambda x: round(x), answer[0])
        return avg, max_val, min_val
    else:
        pass


if __name__ == '__main__':
    # d = datetime.now().isoformat().split('T')
    create_tables()
    # insert_into_user(user_id=1, name='zuzz')
    # insert_into_hr(date=d[0], user_id=1, heart_rate_indicator=120)
    # update_hr(hr_ind=140, date=d[0], user_id=1)
    #
    # print(get_for_some_day(date=d[0], user_id=1))

    # insert_into_user(user_id=2, name='митя')
    # d, t = datetime.now().isoformat().split('T')
    # insert_into_hr(user_id=2, date=d, time=datetime.now(), heart_rate_indicator=150)
    # print(get_hr_for_some_day(date=d, user_id=2)[0][0].isoformat().split('T')[2])
    #
    # print(get_agr_val_from_hr(start_date=))
    import faker

    fake = faker.Faker()

    for i in range(100):
        rand_date = fake.date_time()
        d = rand_date.isoformat().split('T')[0]
        insert_into_hr(date=d, user_id=2, heart_rate_indicator=random.randint(50, 150), time=rand_date)
    start_time = datetime.strptime('1800-12-02' + ' 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
    end_time = datetime.strptime('2024-02-02' + ' 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
    print(get_agr_val_from_hr(start_date='1800-12-02', end_date='2024-02-02', user_id=2))

    #
    # date, time = datetime.now().isoformat().split('T')
    # request = 'у меня болит живот'
    # answer = send_answer(msg=request)
    # insert_request_response(time=time,
    #                         date=date,
    #                         user_id=2,
    #                         user_name='митя',
    #                         request=request,
    #                         response=answer)