import base64
import requests
import uuid
import requests
import json
import os

client_id = os.getenv('CLIENT_ID')
secret = os.getenv('SECRET')
auth = os.getenv('AUTH')

credentials = f"{client_id}:{secret}"
encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

requests.packages.urllib3.disable_warnings()


def get_token(auth_token, scope='GIGACHAT_API_PERS'):
    """
      Выполняет POST-запрос к эндпоинту, который выдает токен.

      Параметры:
      - auth_token (str): токен авторизации, необходимый для запроса.
      - область (str): область действия запроса API. По умолчанию — «GIGACHAT_API_PERS».

      Возвращает:
      - ответ API, где токен и срок его "годности".
      """
    # Создадим идентификатор UUID (36 знаков)
    rq_uid = str(uuid.uuid4())

    # API URL
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    # Заголовки
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': rq_uid,
        'Authorization': f'Basic {auth_token}'
    }

    # Тело запроса
    payload = {
        'scope': scope
    }

    try:
        # Делаем POST запрос с отключенной SSL верификацией
        # (можно скачать сертификаты Минцифры, тогда отключать проверку не надо)
        resp = requests.post(url, headers=headers, data=payload, verify=False)
        return resp
    except requests.RequestException as e:
        print(f"Ошибка: {str(e)}")
        return -1


response = get_token(auth)
if response != 1:
    giga_token = response.json()['access_token']

prompt_answer = f'''
Отвечай так, как будто ты врач и ведешь беседу с пациентом: обращайся на Вы, иногда используй шутки, но отвечай в деловом стиле.
По симптомам в приведенном тексте тебе надо понять, какие заболевания вероятно могут быть у человека. 
Также тебе нужно дать рекомендацию по дальнейшему лечению.
Пример:
- у меня сегодня болел живот и была рвота.
- Вероятнее всего, у вас отравление. Вам следует промыть желудок и как можно скорее обратиться ко врачу.
'''


def send_answer(token=giga_token, msg=None, dialog_history=None):
    """
    Отправляет POST-запрос к API чата для получения ответа от модели GigaChat.

    Параметры:
    - auth_token (str): Токен для авторизации в API.
    - user_message (str): Сообщение от пользователя, для которого нужно получить ответ.

    Возвращает:
    - str: Ответ от API в виде текстовой строки.
    """
    if dialog_history is None:
        dialog_history = [
            {
                'role': 'system',
                'content': prompt_answer
            },
            {
                "role": "user",  # Роль отправителя (пользователь)
                "content": msg  # Содержание сообщения
            }
        ]
    else:
        dialog_history.append(
            {
                "role": "user",
                "content": msg
            }
        )

    # URL API, к которому мы обращаемся
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    # Подготовка данных запроса в формате JSON
    payload = json.dumps({
        "model": "GigaChat",  # Используемая модель
        "messages": dialog_history,
        "temperature": 1,  # Температура генерации
        "top_p": 0.1,  # Параметр top_p для контроля разнообразия ответов
        "n": 1,  # Количество возвращаемых ответов
        "stream": False,  # Потоковая ли передача ответов
        "max_tokens": 512,  # Максимальное количество токенов в ответе
        "repetition_penalty": 1,  # Штраф за повторения
        "update_interval": 0  # Интервал обновления (для потоковой передачи)
    })

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/json',  # Тип содержимого - JSON
        'Accept': 'application/json',  # Принимаем ответ в формате JSON
        'Authorization': f'Bearer {token}'  # Токен авторизации
    }

    try:
        resp = requests.request("POST", url, headers=headers, data=payload, verify=False)
        ans = resp.json()['choices'][0]['message']['content']
        dialog_history.append(
            {
                'role': 'assistant',
                'content': ans
            }
        )
        return ans, dialog_history
    except requests.RequestException as e:
        # Обработка исключения в случае ошибки запроса
        print(f"Произошла ошибка: {str(e)}")
        return 'В данный момент HealthAssistant недоступен из-за технических неполадок', dialog_history


if __name__ == '__main__':
    pass
    # for req in """1. У меня часто болит голова, кружится и тошнит.
    # 2. Я постоянно чувствую слабость, у меня болят мышцы и суставы.
    # 3. У меня непрерывно болит горло, сопли текут, и температура поднимается.
    # 4. У меня появилась сыпь на коже, зуд и покраснение.
    # 5. Я постоянно мучаюсь от кашля, у меня затруднено дышание и боль в груди.
    # 6. У меня бывают приступы тошноты, рвоты и расстройства желудка.
    # 7. Я чувствую давление и боль в животе, возникают отрыжка и изжога.
    # 8. У меня непрерывно болят уши, от них идет выделение и сопли.
    # 9. Я ощущаю постоянное жжение и зуд в глазах, они красные и вялые.
    # 10. У меня непрерывно болит мочевой пузырь, бывают частые и плохие мочеиспускания.
    # 11. У меня появилась непонятная слабость, покраснение кожи и отеки.
    # 12. Я стал замечать проблемы с памятью, нарушения сна и чувство депрессии.
    # 13. У меня постоянно болит колено, оно опухшее и ограничено в движении.
    # 14. У меня бывают сильные колющие боли в груди, ощущение стука и обморока.
    # 15. Я почувствовал наросты и покраснение в области лимфоузлов, температура увеличилась.""".split('\n'):
    #     print(f'''Вопрос: {req}
    # {return_pred_recommend(req)}
    # ''')
    dialog_history = None
    for i in range(5):
        request = input()
        answer, dialog_history = send_answer(msg=request, dialog_history=dialog_history)
        print(f'- {answer}')
        print(dialog_history)
        print()

