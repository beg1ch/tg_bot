from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime
from gigachat_model import send_answer
from config import MESSAGES
from utils import reformat_date, is_valid_date
import reply
from db import insert_into_hr, insert_into_user, insert_request_response, get_hr_for_some_day, get_agr_val_from_hr

user_private_router = Router()

kdb_choice_lst = reply.start_choice_kb.__dict__['keyboard']
kdb_dialog_lst = reply.leave_or_keep_dialog.__dict__['keyboard']
kdb_put_hr_lst = reply.leave_or_keep_put_hr.__dict__['keyboard']
kdb_choose_func_hr = reply.choice_func_hr.__dict__['keyboard']
kdb_leave_od_func = reply.leave_check_one_day_hr.__dict__['keyboard']


class Dialog(StatesGroup):
    dialog_history = State()


class PutHR(StatesGroup):
    hr_indicator = State()


class CheckHR(StatesGroup):
    get_function = State()
    one_day_hr = State()
    agr_func = State()
    get_start_date = State()
    get_end_date = State()


# START
@user_private_router.message(StateFilter('*'), CommandStart())
async def start_cmd(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if not (current_state is None):
        await state.clear()
        await msg.answer(MESSAGES['START'], reply_markup=reply.start_choice_kb, parse_mode=ParseMode.HTML)

    else:
        user_id = msg.from_user.id
        name = msg.from_user.full_name
        insert_into_user(user_id=user_id, name=name)
        await msg.answer(MESSAGES['START'], reply_markup=reply.start_choice_kb, parse_mode=ParseMode.HTML)


# START_PLACE
@user_private_router.message(Command('start_menu'))
@user_private_router.message(StateFilter('*'),
                             (F.text == kdb_dialog_lst[0][0].text) | (F.text == kdb_put_hr_lst[0][1].text))
async def start_place_cmd(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await msg.answer(MESSAGES['START_PLACE'], reply_markup=reply.start_choice_kb)

    else:
        await msg.answer(MESSAGES['START_PLACE'], reply_markup=reply.start_choice_kb)


# SUPPORT
@user_private_router.message(Command('support'), StateFilter('*'))
async def help_cmd(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await msg.answer(MESSAGES['SUPPORT'], reply_markup=reply.del_kbd)
    else:
        await msg.answer(MESSAGES['SUPPORT'], reply_markup=reply.del_kbd)


@user_private_router.message(Command('feedback'), StateFilter('*'))
async def help_cmd(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await msg.answer(MESSAGES['FEEDBACK'], reply_markup=reply.del_kbd)
    else:
        await msg.answer(MESSAGES['FEEDBACK'], reply_markup=reply.del_kbd)


# CHECK HEART RATE AND CHOOSE FUNC
@user_private_router.message(StateFilter(None),
                             (F.text == kdb_choice_lst[1][1].text) | (F.text == kdb_leave_od_func[0][0].text))
async def check_hr(msg: types.Message, state: FSMContext):
    await msg.answer(MESSAGES['CHECK_HR_SECTION'], reply_markup=reply.choice_func_hr)
    await state.set_state(CheckHR.get_function)


# GET DATE OF ONE DAY CHECK
@user_private_router.message(CheckHR.get_function, F.text == kdb_choose_func_hr[0][0].text)
async def get_date(msg: types.Message, state: FSMContext):
    await state.update_data(get_function='one day')
    await msg.answer(MESSAGES['CHECK_ONE_DAY_HR'], reply_markup=reply.del_kbd)
    await state.set_state(CheckHR.one_day_hr)


# RETURN TIME AND HEART RATE FOR ONE DAY CHECK
@user_private_router.message(CheckHR.one_day_hr)
async def return_hr(msg: types.Message, state: FSMContext):
    date = msg.text.strip()
    if is_valid_date(date):
        date_ref = reformat_date(date)
        await state.update_data(one_day_hr=date_ref)
        user_id = msg.from_user.id
        result = get_hr_for_some_day(date=date_ref, user_id=user_id)
        if result:
            time, hr = [t[0].isoformat().split('T')[1].split('.')[0] for t in result], [h[1] for h in result]
            date_str = ''
            for t, h in zip(time, hr):
                date_str += f'{t}: {h}\n'
            await state.clear()
            await msg.answer(f'Ваши показатели за {date}:\n' + date_str, reply_markup=reply.leave_check_one_day_hr)
        else:
            await state.clear()
            await msg.answer(f'За {date} данных нет', reply_markup=reply.leave_check_one_day_hr)
    else:
        await state.clear()
        await msg.answer('Вы ввели дату некорректно', reply_markup=reply.leave_check_one_day_hr)


# GET START DATE OF RANGE
@user_private_router.message(CheckHR.get_function, F.text == kdb_choose_func_hr[0][1].text)
async def get_start_date(msg: types.Message, state: FSMContext):
    await state.update_data(get_function='agr func')
    await msg.answer(MESSAGES['START_DATE'], reply_markup=reply.del_kbd, parse_mode=ParseMode.HTML)
    await state.set_state(CheckHR.get_start_date)


# GET END DATE OF RANGE
@user_private_router.message(CheckHR.get_start_date)
async def get_end_date(msg: types.Message, state: FSMContext):
    try:
        start_date = msg.text.strip()
        if is_valid_date(start_date):
            start_date_ref = reformat_date(start_date)
            await state.update_data(get_start_date=(start_date, start_date_ref))
            await msg.answer(MESSAGES['END_DATE'], parse_mode=ParseMode.HTML)
            await state.set_state(CheckHR.get_end_date)
        else:
            await state.clear()
            await msg.answer('Вы ввели дату некорректно', reply_markup=reply.leave_check_one_day_hr)
    except:
        await state.clear()
        await msg.answer('Вы ввели дату некорректно', reply_markup=reply.leave_check_one_day_hr)


# RETURN AGGREGATE FUNC AVG, MIN, MAX
@user_private_router.message(CheckHR.get_end_date)
async def get_end_date(msg: types.Message, state: FSMContext):
    try:
        end_date = msg.text
        if is_valid_date(end_date):
            end_date_ref = reformat_date(end_date)
            await state.update_data(get_end_date=end_date_ref)
            data = await state.get_data()
            start_date = data['get_start_date'][0]
            start_date_ref = data['get_start_date'][1]
            end_date_ref = data['get_end_date']
            user_id = msg.from_user.id
            result = get_agr_val_from_hr(start_date=start_date_ref, end_date=end_date_ref, user_id=user_id)
            if result:
                avg, max_val, min_val = get_agr_val_from_hr(start_date=start_date_ref, end_date=end_date_ref,
                                                            user_id=user_id)
                await state.clear()
                await msg.answer(
                    f'С {start_date} по {end_date} у вас следующие показатели пульса:\nсреднее значение - {avg}\nмаксимальное значение - {max_val}\nминимальное значение: {min_val}',
                    reply_markup=reply.leave_check_one_day_hr)
            else:
                await state.clear()
                await msg.answer(f'За промежуток с {start_date} по {end_date} данных не обнаружено.',
                                 reply_markup=reply.leave_check_one_day_hr)
        else:
            await state.clear()
            await msg.answer('Вы ввели дату некорректно',
                             reply_markup=reply.leave_check_one_day_hr)
    except:
        await state.clear()
        await msg.answer('Вы ввели дату некорректно',
                         reply_markup=reply.leave_check_one_day_hr)


# PUT HEART RATE INTO BD
@user_private_router.message(StateFilter(None),
                             (F.text == kdb_choice_lst[1][0].text) | (F.text == kdb_put_hr_lst[0][0].text))
async def put_hr(msg: types.Message, state: FSMContext):
    await msg.answer(MESSAGES['PUT_HR'], reply_markup=reply.del_kbd)
    await state.set_state(PutHR.hr_indicator)


# GET HEART RATE TO PUT IT INTO BD
@user_private_router.message(PutHR.hr_indicator)
async def get_hr(msg: types.Message, state: FSMContext):
    hr_indicator = msg.text
    try:
        if hr_indicator.isdigit():
            await msg.answer('Пульс успешно сохранен!' + MESSAGES['PUT_HR_SUCCESSFULLY'],
                             reply_markup=reply.leave_or_keep_put_hr)
            await state.update_data(hr_indicator=hr_indicator)
            data = await state.get_data()
            user_id = msg.from_user.id
            d, t = datetime.now().isoformat().split('T')
            insert_into_hr(user_id=user_id, heart_rate_indicator=data['hr_indicator'], date=d, time=datetime.now())
            await state.clear()
        else:
            await msg.answer(MESSAGES['ERROR_HR'], reply_markup=reply.leave_or_keep_put_hr)
    except:
        await msg.answer(MESSAGES['ERROR_HR'], reply_markup=reply.leave_or_keep_put_hr)


# HANDING DIALOG WITH ASSISTANT
@user_private_router.message(StateFilter(None),
                             (F.text == kdb_choice_lst[0][0].text))
async def dialog_handler_req(msg: types.Message, state: FSMContext):
    await msg.answer(MESSAGES['START_DIALOG'], reply_markup=reply.del_kbd)
    await state.set_state(Dialog.dialog_history)


# HANDING EACH DIALOG MESSAGE
@user_private_router.message(Dialog.dialog_history, F.text)
async def handle_message_req(msg: types.Message, state: FSMContext):
    try:
        if msg.text != kdb_dialog_lst[0][0].text:
            await state.update_data(dialog_history=None)
            with open('restricted_words.txt', 'r', encoding='UTF-8') as f:
                restricted_words = {line.strip() for line in f}
            req = msg.text
            if restricted_words.intersection(req.lower().split()):
                answer = MESSAGES['ERROR']
                await msg.answer(answer, reply_markup=reply.leave_or_keep_dialog)
            else:
                data = await state.get_data()
                dialog_history = data['dialog_history']
                answer, dialog_history = send_answer(msg=req, dialog_history=dialog_history)
                await state.update_data(dialog_history=dialog_history)
                if answer not in MESSAGES['NEW_INSULT_IND']:
                    await msg.answer(answer, reply_markup=reply.leave_or_keep_dialog)
                else:
                    answer = MESSAGES['ERROR']
                    await msg.answer(answer, reply_markup=reply.leave_or_keep_dialog)
            await state.set_state(Dialog.dialog_history)
            d, t = datetime.now().isoformat().split('T')
            user_id = msg.from_user.id
            name = msg.from_user.full_name
            insert_request_response(date=d, time=t, user_name=name, user_id=user_id, response=answer, request=req)
        else:
            await start_place_cmd(msg)
    except:
        await msg.answer('В данный момент HealthAssistant недоступен из-за технических неполадок',
                         reply_markup=reply.leave_or_keep_dialog)
