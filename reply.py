from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

leave_or_keep_dialog = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Покинуть диалог')]],
                                           resize_keyboard=True)

choice_func_hr = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='1️⃣'), KeyboardButton(text='📅')]],
                                     resize_keyboard=True)

leave_check_one_day_hr = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Вернуться назад')]], resize_keyboard=True)

start_choice_kb = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='🦉 Поговорить с ассистентом')
    ],
    [
        KeyboardButton(text='✍ Записать пульс'),
        KeyboardButton(text='🗓️ Отследить пульс')
    ]
],
    resize_keyboard=True,
)

leave_or_keep_put_hr = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='1 🔄'), KeyboardButton(text='2 🏠')]],
                                           resize_keyboard=True)

del_kbd = ReplyKeyboardRemove()

if __name__ == '__main__':
    print(leave_or_keep_put_hr.__dict__['keyboard'][0][1].text)
    print(start_choice_kb.__dict__['keyboard'][0][0].text)
