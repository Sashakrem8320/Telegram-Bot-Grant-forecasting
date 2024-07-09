import asyncio
from aiogram import Bot, Router, Dispatcher, types, F
from aiogram.filters.command import Command, CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

import warnings
import logging
import requests
import datetime
import joblib
import pandas as pd

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
bot = Bot(token="<Тут могла быть ваша реклама>",default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

users_dict = dict()

bern_goal = joblib.load('model/bern_goal.joblib')
bern_desc = joblib.load('model/bern_desc.joblib')
bern_soc = joblib.load('model/bern_soc.joblib')
bern_tasks = joblib.load('model/bern_tasks.joblib')
bern_main = joblib.load('model/bern_main.joblib')
style_model = joblib.load('model/formal.joblib')
vc_desc=joblib.load('model/vc_desc.joblib')
vc_goal=joblib.load('model/vc_goal.joblib')
vc_soc=joblib.load('model/vc_soc.joblib')
vc_tasks=joblib.load('model/vc_tasks.joblib')

class WaitData(StatesGroup):
	waiting_inn = State()
	waiting_project_name = State()
	waiting_project_description = State()
	waiting_soc_signif = State()
	waiting_tasks = State()
	waiting_goal = State()
	waiting_grant_req_money = State()
	waiting_implem_start = State()
	waiting_implem_end = State()
	waiting_soc = State()

def get_name(name:str) -> str:
	return name.replace('&','&amp').replace('<','&lt').replace('>','&gt')

def check_inn(inn:int) -> bool:
	inn = str(inn)
	if len(inn) != 10:
		return False
	else:
		s = 0
		k = [2,4,10,3,5,9,4,6,8]
		for i in range(9):
			s = int(inn[i])*k[i] + s
		if (s%11)%10 == int(inn[-1]):
			return True
		else:
			return False

async def model(message:types.Message,description:str,direction:str,tasks:str,goal:str,money_req_grant:int,work_days:int,soc:int) -> None:
	vc_direction = {
		'Выявление и поддержка молодых талантов в области культуры и искусства':[0,0,0,0,0,0,1,0,0,0,0,0,0],
		'Защита прав и свобод человека и гражданина, в том числе защита прав заключенных':[1,0,0,0,0,0,0,0,0,0,0,0,0],
		'Охрана здоровья граждан, пропаганда здорового образа жизни':[0,1,0,0,0,0,0,0,0,0,0,0,0],
		'Охрана окружающей среды и защита животных':[0,0,1,0,0,0,0,0,0,0,0,0,0],
		'Поддержка молодежных проектов, реализация которых охватывает виды деятельности, предусмотренные статьей 31 Федерального закона от 12 января 1996 г. № 7-ФЗ «О некоммерческих организациях»':[0,0,0,1,0,0,0,0,0,0,0,0,0],
		'Поддержка молодежных проектов, реализация которых охватывает виды деятельности, предусмотренные статьей 31.1 Федерального закона от 12 января 1996 г. № 7-ФЗ «О некоммерческих организациях»':[0,0,0,0,1,0,0,0,0,0,0,0,0],
		'Поддержка проектов в области культуры и искусства':[0,0,0,0,0,1,0,0,0,0,0,0,0],
		'Поддержка проектов в области науки, образования, просвещения':[0,0,0,0,0,0,1,0,0,0,0,0,0],
		'Поддержка семьи, материнства, отцовства и детства':[0,0,0,0,0,0,0,1,0,0,0,0,0],
		'Развитие институтов гражданского общества':[0,0,0,0,0,0,0,0,1,0,0,0,0],
		'Развитие общественной дипломатии и поддержка соотечественников':[0,0,0,0,0,0,0,0,0,1,0,0,0],
		'Сохранение исторической памяти':[1,0,0,0,0,0,0,0,0,0,1,0,0],
		'Социальное обслуживание, социальная поддержка и защита граждан':[0,0,0,0,0,0,0,0,0,0,0,1,0],
		'Укрепление межнационального и межрелигиозного согласия':[0,0,0,0,0,0,0,0,0,0,0,0,1]
	}

	vector_desc = vc_desc.transform(pd.Series([description]))
	vector_goal = vc_goal.transform(pd.Series([goal]))
	vector_tasks = vc_goal.transform(pd.Series([tasks]))
	vector_soc = vc_soc.transform(pd.Series([soc]))
	vector_direct = vc_direction[direction]

	form_desc = style_model.predict_proba(vector_desc)[0][1]
	form_goal = style_model.predict_proba(vector_goal)[0][1]
	form_tasks = style_model.predict_proba(vector_tasks)[0][1]
	form_soc = style_model.predict_proba(vector_soc)[0][1]

	desc_len = len(description.split(' '))
	goal_len = len(goal.split(' '))
	tasks_len = len(tasks.split(' '))
	soc_len = len(soc.split(' '))

	vector_data = pd.concat(
		[
			pd.DataFrame([money_req_grant]),
			pd.DataFrame([form_desc]),
			pd.DataFrame([form_soc]),
			pd.DataFrame([form_tasks]),
			pd.DataFrame([form_goal]),
			pd.DataFrame([desc_len]),
			pd.DataFrame([soc_len]),
			pd.DataFrame([tasks_len]),
			pd.DataFrame([goal_len]),
			pd.DataFrame([work_days]),
			pd.DataFrame([datetime.datetime.now().year]),
			pd.DataFrame([vector_direct]),
			pd.DataFrame(vector_goal.toarray()),
			pd.DataFrame(vector_tasks.toarray()),
			pd.DataFrame(vector_soc.toarray()),
			pd.DataFrame(vector_desc.toarray())
		]
	,axis='columns')

	df_1 = pd.DataFrame([form_desc])
	df_2 = pd.DataFrame([desc_len])
	df_3 = pd.DataFrame(vector_desc.toarray())
	df_1 = pd.concat([df_1,df_2,df_3],axis='columns',ignore_index=True)

	desc_percent= round(bern_desc.predict_proba(df_1)[0][1]*100,2)
	goal_percent= round(bern_goal.predict_proba(pd.concat([pd.DataFrame([form_goal]),pd.DataFrame([goal_len]),pd.DataFrame(vector_goal.toarray())],axis='columns'))[0][1]*100,2)
	soc_percent= round(bern_soc.predict_proba(pd.concat([pd.DataFrame([form_soc]),pd.DataFrame([soc_len]),pd.DataFrame(vector_soc.toarray())],axis='columns'))[0][1]*100,2)
	tasks_percent= round(bern_tasks.predict_proba(pd.concat([pd.DataFrame([form_tasks]),pd.DataFrame([tasks_len]),pd.DataFrame(vector_tasks.toarray())],axis='columns'))[0][1]*100,2)
	all_answer = 'Проект скорее всего получит грант🎉' if bern_main.predict_proba(vector_data)[0][1]*100 == 100 else 'Проект скорее всего не получит грант😭'

	hype_desc = '👍' if desc_percent >=50 else '👎'
	hype_goal = '👍' if goal_percent >=50 else '👎'
	hype_soc = '👍' if soc_percent >=50 else '👎'
	hype_tasks = '👍' if tasks_percent >=50 else '👎'

	await message.answer(f'<i><b><u>✨Оценка заявки</u></b></i>\n<b>Шанс прохождения проекта:</b> {all_answer}\n\n<b>Оценка описания:</b> {desc_percent}/100{hype_desc}\n<b>Оценка социальной значимости:</b> {soc_percent}/100{hype_soc}\n<b>Оценка задач:</b> {tasks_percent}/100{hype_tasks}\n<b>Оценка цели:</b> {goal_percent}/100{hype_goal}',reply_markup=types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text='Начать✨')]],one_time_keyboard=True,resize_keyboard=True))

async def data_register(message:types.Message,step:int,state:FSMContext):
	if step == 0:
		users_dict[message.from_user.id] = dict()
		await message.answer(f'👨‍💻<i>Введите ИНН вашей НКО:</i>',reply_markup=None)
		await state.set_state(WaitData.waiting_inn)
	elif step == 1:
		if message.text is None:
			await message.answer('<b>🔍Текст сообщения не был найден!</b> ⚆_⚆')
			await message.answer(f'👨‍💻<i>Введите ИНН вашей НКО:</i>')
		else:
			try:
				inn = int(message.text)
				if check_inn(inn):
					cookies = {
						'_ym_uid': '1720186151535325611',
						'_ym_d': '1720186151',
						'_ym_isad': '2',
						'_ym_visorc': 'w',
						'qrator_msid': '1720186148.507.xqd605KOD4pgQVUP-pln4hk1s3j92e8bh4th91he9thi0l099',
					}

					headers = {
						'Accept': 'application/json, text/plain, */*',
						'Accept-Language': 'ru,en;q=0.9,es;q=0.8',
						'Connection': 'keep-alive',
						'Referer': 'https://bankrot.fedresurs.ru/bankrupts?searchString=6670044205&regionId=all&isActiveLegalCase=null&offset=0&limit=15',
						'Sec-Fetch-Dest': 'empty',
						'Sec-Fetch-Mode': 'cors',
						'Sec-Fetch-Site': 'same-origin',
						'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.6.0.0 Safari/537.36',
						'sec-ch-ua': '"Chromium";v="124", "YaBrowser";v="24.6", "Not-A.Brand";v="99", "Yowser";v="2.5"',
						'sec-ch-ua-mobile': '?0',
						'sec-ch-ua-platform': '"Linux"',
					}

					params = {
						'searchString': inn,
						'isActiveLegalCase': 'null',
						'limit': '15',
						'offset': '0',
					}

					response = requests.get('https://bankrot.fedresurs.ru/backend/cmpbankrupts', params=params, cookies=cookies, headers=headers).json()
					if response['total'] == 0:
						await message.answer(f'👨‍💻<i>Введите название проекта:</i>',reply_markup=None)
						await state.set_state(WaitData.waiting_project_name)
					else:
						await message.answer('<b>❌Организация-банкрот не может участвовать в конкурсе связи с <a href="https://президентскиегранты.рф/public/api/v1/file/get-document?filename=e1d12373-3ae5-47f3-99ce-667a673aa803.pdf">положением о конкурсе "Фонда президентских грантов"</a>!</b> ψ(._. )>',link_preview_options=types.LinkPreviewOptions(is_disabled=True),reply_markup=types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text='Начать✨')]],one_time_keyboard=True,resize_keyboard=True))
						del users_dict[message.from_user.id]
						return
				else:
					await message.answer('<b>❌Введенный ИНН не правильный! ψ(._. )></b>')
					await message.answer(f'👨‍💻<i>Введите ИНН вашей НКО:</i>')
			except ValueError:
				await message.answer('<b>🔍ИНН НКО должен быть целым числом!</b> ⚆_⚆')
				await message.answer(f'👨‍💻<i>Введите ИНН вашей НКО:</i>')
	elif step == 2:
		if message.text is None:
			await message.answer('<b>🔍Текст сообщения не был найден!</b> ⚆_⚆')
			await message.answer(f'👨‍💻<i>Введите название проекта:</i>')
		else:
			await message.answer(f'👨‍💻<i>Введите описание проекта:</i>',reply_markup=None)
			await state.set_state(WaitData.waiting_project_description)
	elif step==3:
		if message.text is None:
			await message.answer('🔍<i>Текст сообщения не был найден!</i> ⚆_⚆')
			await message.answer(f'👨‍💻<i>Введите описание проекта:</i>',reply_markup=None)
		else:
			users_dict[message.from_user.id][2] = message.text

			builder = InlineKeyboardBuilder()
			builder.row(types.InlineKeyboardButton(text='1',callback_data='Direction_1'),types.InlineKeyboardButton(text='2',callback_data='Direction_2'),types.InlineKeyboardButton(text='3',callback_data='Direction_3'),types.InlineKeyboardButton(text='4',callback_data='Direction_4'),types.InlineKeyboardButton(text='5',callback_data='Direction_5'),types.InlineKeyboardButton(text='6',callback_data='Direction_6'),types.InlineKeyboardButton(text='7',callback_data='Direction_7'))
			builder.row(types.InlineKeyboardButton(text='8',callback_data='Direction_8'),types.InlineKeyboardButton(text='9',callback_data='Direction_9'),types.InlineKeyboardButton(text='10',callback_data='Direction_10'),types.InlineKeyboardButton(text='11',callback_data='Direction_11'),types.InlineKeyboardButton(text='12',callback_data='Direction_12'),types.InlineKeyboardButton(text='13',callback_data='Direction_13'),types.InlineKeyboardButton(text='14',callback_data='Direction_14'))
			await message.answer(f'<i>👨‍💻Выберите конкурсное направление проверка:</i>\n\n<b>1 - Сохранение исторической памяти\n2-Развитие институтов гражданского общества\n3-Охрана окружающей среды\n4-Культура и искусства\n5-Охрана здоровья и пропаганда здорового образа жизни\n6-Поддержка семьи, материнства, отцовства и детства\n7-Укрепление межнационального и межрелигиозного согласия\n8-Социальное обслуживание и защита граждан\n9-Молодежные проекты(статья 31.1 ФЗ)\n10-Молодежные проекты(статья 31 ФЗ)\n11-Защита прав и свобод человека\n12-Общественная дипломатия\n13-Наука и просвещение\n14-Поддержка молодых талантов</b>',reply_markup=builder.as_markup())
	elif step == 4:
		await message.answer(f'👨‍💻<i>Введите задачи проекта:</i>',reply_markup=None)
		await state.set_state(WaitData.waiting_tasks)
	elif step == 5:
		if message.text is None:
			await message.answer('<b>🔍Текст сообщения не был найден!</b> ⚆_⚆')
			await message.answer(f'👨‍💻<i>Введите задачи проекта:</i>')
		else:
			users_dict[message.from_user.id][4] = message.text
			await message.answer(f'👨‍💻<i>Введите цель проекта:</i>',reply_markup=None)
			await state.set_state(WaitData.waiting_goal)
	elif step == 6:
		if message.text is None:
			await message.answer('<b>🔍Текст сообщения не был найден!</b> ⚆_⚆')
			await message.answer(f'👨‍💻<i>Введите цель проекта:</i>')
		else:
			users_dict[message.from_user.id][5] = message.text
			await message.answer(f'👨‍💻<i>Введите обоснование социальной значимости проекта:</i>',reply_markup=None)
			await state.set_state(WaitData.waiting_soc)
	elif step == 7:
		if message.text is None:
			await message.answer('<b>🔍Текст сообщения не был найден!</b> ⚆_⚆')
			await message.answer(f'👨‍💻<i>Введите обоснование социальной значимости проекта:</i>')
		else:
			users_dict[message.from_user.id][6] = message.text
			await message.answer(f'👨‍💻<i>Введите запрашиваемую сумму гранта:</i>',reply_markup=None)
			await state.set_state(WaitData.waiting_grant_req_money)
	elif step == 8:
		if message.text is None:
			await message.answer('<b>🔍Текст сообщения не был найден!</b> ⚆_⚆')
			await message.answer(f'👨‍💻<i>Введите запрашиваемую сумму гранта:</i>')
		else:
			try:
				money_req_grant = int(float(message.text))
				if money_req_grant < 0:
					await message.answer('<b>🤔Вы хотите чтобы у вас за грант отобрали деньги?</b> ⚆_⚆')
					await message.answer(f'👨‍💻<i>Введите запрашиваемую сумму гранта:</i>')
				else:
					users_dict[message.from_user.id][7] = money_req_grant
					await message.answer(f'👨‍💻<i>Введите дату <b>начала реализации</b> проекта в формате ДД.ММ.ГГГГ:</i>',reply_markup=None)
					await state.set_state(WaitData.waiting_implem_start)
			except ValueError:
				await message.answer('<b>❌Запрашиваемая сумма гранта - число! ψ(._. )></b>')
				await message.answer(f'👨‍💻<i>Введите запрашиваемую сумму гранта:</i>')
	elif step == 9:
		if message.text is None:
			await message.answer('<b>🔍Текст сообщения не был найден!</b> ⚆_⚆')
			await message.answer(f'👨‍💻<i>Введите дату <b>начала реализации</b> проекта в формате ДД.ММ.ГГГГ:</i>')
		else:
			try:
				d,m,y = map(int,message.text.split('.'))
				date = datetime.datetime(day=d,month=m,year=y)
				users_dict[message.from_user.id][8] = date
				await message.answer(f'👨‍💻<i>Введите дату <b>конца реализации</b> проекта в формате ДД.ММ.ГГГГ</i>',reply_markup=None)
				await state.set_state(WaitData.waiting_implem_end)
			except Exception as e:
				await message.answer('<b>❌Введенная дата неправильная! ψ(._. )></b>')
				await message.answer(f'👨‍💻<i>Введите дату <b>начала реализации</b> проекта в формате ДД.ММ.ГГГГ:</i>')
	elif step == 10:
		if message.text is None:
			await message.answer('<b>🔍Текст сообщения не был найден!</b> ⚆_⚆')
			await message.answer(f'👨‍💻<i>Введите дату <b>конца реализации</b> проекта в формате ДД.ММ.ГГГГ:</i>')
		else:
			try:
				d,m,y = map(int,message.text.split('.'))
				date = datetime.datetime(day=d,month=m,year=y)
				users_dict[message.from_user.id][9] = date

				await state.clear()
				m=await message.answer('<i>✨Начинаю творить чудеса...</i>',reply_markup=None)

				description = users_dict[message.from_user.id][2]
				direction = users_dict[message.from_user.id][3]
				tasks = users_dict[message.from_user.id][4]
				goal = users_dict[message.from_user.id][5]
				soc = users_dict[message.from_user.id][6]
				money_req_grant = users_dict[message.from_user.id][7]
				work_days = int(abs((users_dict[message.from_user.id][9]-users_dict[message.from_user.id][8]).total_seconds())//86400)

				await model(message,description,direction,tasks,goal,money_req_grant,work_days,soc)
				await m.delete()
				del users_dict[message.from_user.id]
				return
			except Exception as e:
			 	print(e)
			 	await message.answer('<b>❌Введенная дата неправильная! ψ(._. )></b>')
			 	await message.answer(f'👨‍💻<i>Введите дату конца реализации проекта в формате ДД.ММ.ГГГГ:</i>')

@dp.message(CommandStart())
@dp.message(Command('help'))
async def cmd_start(message:types.Message,state:FSMContext) -> None:
	await state.clear()
	await message.answer(
		f'Здравствуйте, {get_name(message.from_user.first_name)}! Я <b>ГрантОракул🧙‍♂️</b>\nЯ попробую предсказать Вам результаты подачи Вашей заявки на грант на основе Машинного Обучения.\n\n<b><i>Зачем это нужно?</i></b>\n•Сможете оценить качество своей заявки\n•Вы сможете усовершенствовать свою заявку перед подачей',
		reply_markup=types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text='Начать✨')]],one_time_keyboard=True,resize_keyboard=True)
	)

@dp.message(F.text == 'Начать✨')
async def cmd_predict(message:types.Message,state:FSMContext) -> None:
	await state.clear()
	if message.from_user.id not in users_dict.keys():
		await data_register(message,0,state)
	else:
		await data_register(message,max(list(users_dict[message.from_user.id].keys()))+1,state)

@dp.message(WaitData.waiting_inn)
async def handler_inn(message:types.Message,state:FSMContext) -> None:
	await data_register(message,1,state)

@dp.message(WaitData.waiting_project_name)
async def handler_project_name(message:types.Message,state:FSMContext) -> None:
	await data_register(message,2,state)

@dp.message(WaitData.waiting_project_description)
async def handler_project_description(message:types.Message,state:FSMContext) -> None:
	await data_register(message,3,state)

@dp.callback_query(F.data.startswith('Direction_'))
async def handler_direction(callback:types.CallbackQuery,state:FSMContext) -> None:
	number_dict = {
		'1':'Сохранение исторической памяти',
		'2':'Развитие институтов гражданского общества',
		'3':'Охрана окружающей среды и защита животных',
		'4':'Поддержка проектов в области культуры и искусства',
		'5':'Охрана здоровья граждан, пропаганда здорового образа жизни',
		'6':'Поддержка семьи, материнства, отцовства и детства',
		'7':'Укрепление межнационального и межрелигиозного согласия',
		'8':'Социальное обслуживание, социальная поддержка и защита граждан',
		'9':'Поддержка молодежных проектов, реализация которых охватывает виды деятельности, предусмотренные статьей 31.1 Федерального закона от 12 января 1996 г. № 7-ФЗ «О некоммерческих организациях»',
		'10':'Поддержка молодежных проектов, реализация которых охватывает виды деятельности, предусмотренные статьей 31 Федерального закона от 12 января 1996 г. № 7-ФЗ «О некоммерческих организациях»',
		'11':'Защита прав и свобод человека и гражданина, в том числе защита прав заключенных',
		'12':'Развитие общественной дипломатии и поддержка соотечественников',
		'13':'Поддержка проектов в области науки, образования, просвещения',
		'14':'Выявление и поддержка молодых талантов в области культуры и искусства'
	}
	category = number_dict[callback.data.split('_')[1]]
	users_dict[callback.from_user.id][3] = category
	await callback.message.answer(f'<i>Вы выбрали категорию {category}</i>')
	await callback.message.delete()
	await data_register(callback.message,4,state)

@dp.message(WaitData.waiting_tasks)
async def handler_tasks(message:types.Message,state:FSMContext) -> None:
	await data_register(message,5,state)

@dp.message(WaitData.waiting_goal)
async def handler_goal(message:types.Message,state:FSMContext) -> None:
	await data_register(message,6,state)

@dp.message(WaitData.waiting_soc)
async def handler_soc(message:types.Message,state:FSMContext) -> None:
	await data_register(message,7,state)

@dp.message(WaitData.waiting_grant_req_money)
async def handler_grant_req_money(message:types.Message,state:FSMContext) -> None:
	await data_register(message,8,state)

@dp.message(WaitData.waiting_implem_start)
async def handler_implem_start(message:types.Message,state:FSMContext) -> None:
	await data_register(message,9,state)

@dp.message(WaitData.waiting_implem_end)
async def handler_implem_end(message:types.Message,state:FSMContext) -> None:
	await data_register(message,10,state)

async def main():
	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(main())

