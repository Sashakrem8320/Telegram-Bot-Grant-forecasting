# ГрантОракул👾
***
Телеграм бот, который может предсказать получит ли ваш проект грант и подсказать, что возможно стоит улучшить.
***
### Функционал бота

Пользователю необходимо прислать боту: название проекта, описание, направление, цели, задачи, желаемую сумму гранта, обоснование социальной значимости, даты начала и конца работы над проектом, а так ИНН Вашей некоммерческой организации. 
После этого бот пришлёт пользователю результат, получит ли проект грант, а также советы по улучшению гранта
***
### Для кого предназначен этот бот?

Для юридических лиц и компаний
***
### Как запустить его у себя на компьютере?
> **Необходимые библиотеки:**
>
> pip install aiogram==3.10.0
> 
> pip install requests==2.32.3
> 
> pip install asyncio==3.4.3
> 
> pip install joblib==1.3.2
> 
> pip install pandas==2.2.2
> 
> pip install numpy==1.26.4
> 
> pip install scikit-learn==1.2.2
> 
> pip install scipy==1.14.0


> Замените **ТОКЕН** боту(Токен можно получить у @BotFather)

> Для запуска полноценной работы телеграмм бота, вам нужно запустить файл **bot/bot.py**
***
### Что используется в проекте?

- Библиотеки:
  - pandas
  - numpy
  - sklearn
  - nltk
  - string
- Модель ML:
  - Наивный Байес Бернулли
- Файлы моделей:
  - bern_desc.joblib
  - bern_goal.joblib
  - bern_main.joblib
  - bern_soc.joblib
  - bern_tasks.joblib
  - formal.joblib
  - vc_desc.joblib
  - vc_goal.joblib
  - vc_soc.joblib
  - vc_tasks.joblib
***
## Разрабатывали:
- Никнеймы GitHub:
  - [*Sashakrem8320*](https://github.com/Sashakrem8320)
  - 
  - [*Ezhovnik*](https://github.com/Ezhovnik)

  - [*Fl1nixxx*](https://github.com/Fl1nixxx)

  - [*Sinopt1ck*](https://github.com/Sinopt1ck)
