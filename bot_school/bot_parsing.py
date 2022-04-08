import pandas as pd
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import telebot
import numpy as np
import matplotlib.pyplot as plt


# # Scrap school portal

df_date = pd.DataFrame(columns=['date'])
for i in range(365):
  df_date.loc[i] = '01/01/2022'

df_date['date'] = pd.to_datetime(df_date['date'], format='%d/%m/%Y')

for i in range(364):
  df_date.loc[i+1] = df_date['date'].iloc[i] + pd.Timedelta(days=1)

df_date['weekday'] = df_date['date'].dt.weekday
df_date['month'] = df_date['date'].dt.month
df_date['day'] = df_date['date'].dt.day
df_date['year'] = df_date['date'].dt.year
df_date = df_date[df_date['weekday'] == 0]

df_date = df_date.reset_index(drop=True)


# Получение оценок

# Фунцкия авторизации:

def autorization(day_month_year):
    global soup    
    session = requests.Session()
    payload = {'login':'login', 
              'password':'password'
             }
    s = session.post("https://login.school.mosreg.ru/login/?ReturnUrl=https%3a%2f%2fschool.mosreg.ru%2fcurrentprogressmodeselector", data=payload)
    s = session.get(f"https://school.mosreg.ru/currentprogress/result/2000003074022/50774/2021/{day_month_year}?UserComeFromSelector=True")
    soup = BeautifulSoup(s.text, 'html.parser')
    return soup  


# Добавим функцию для поиска информации в журнале:


def give_report_soup(day_month_year):    
    autorization(day_month_year)

    with open(f"Полный_отчет_{day_month_year}.html", "w") as file:
      file.write(str(soup))

    if len(soup) < 5: # в это случае страница с ошибкой
        return 'Данных нет'



def give_themes_soup(day_month_year):    
    autorization(day_month_year)

    with open(f"Изучаемые_темы_{day_month_year}.html", "w") as file:
      file.write(str(soup.select('div.current-progress-themes')))

    if len(soup) < 5: # в это случае страница с ошибкой
        return 'Данных нет'


def give_marks_soup(day_month_year):    
    autorization(day_month_year)

    with open(f"Оценки_{day_month_year}.html", "w") as file:
      file.write(str(soup.select('div.current-progress-marks')))

    if len(soup) < 5: # в это случае страница с ошибкой
        return 'Данных нет'



def give_schedule_soup(day_month_year):    
    autorization(day_month_year)

    with open(f"Рассписание_{day_month_year}.html", "w") as file:
      file.write(str(soup.select('div.current-progress-schedule')))

    if len(soup) < 5: # в это случае страница с ошибкой
        return 'Данных нет'



def give_homeworks_soup(day_month_year):    
    autorization(day_month_year)

    with open(f"Домашнее_задание_{day_month_year}.html", "w") as file:
      file.write(str(soup.select('div.current-progress-homeworks')))

    if len(soup) < 5: # в это случае страница с ошибкой
        return 'Данных нет'


# Пишем бота


TOKEN = '1234567890'
tb = telebot.TeleBot(TOKEN)



features = ''
goal = ''
age = 0

@tb.message_handler(content_types=['text', 'photo', 'document'])

# приветсвие
def start(message):
  try:
    if message.text == '/poehali':
        tb.send_message(message.from_user.id, '''Привет. Я бот успеваемости ребенка за 2022 год. Выбери месяц отчета:''')
        tb.send_message(message.from_user.id, f"Январь: /1, Февраль: /2,  Март: /3, Апрель: /4, Май: /5,")
        tb.send_message(message.from_user.id, f"Сентябрь: /9, Октябрь: /10, Ноябрь: /11, Декабрь: /12")
        tb.register_next_step_handler(message, get_month); # следующий шаг – функция get_month_day
    else:

        tb.send_message(message.from_user.id, '''Выбери месяц отчета:''')
        tb.send_message(message.from_user.id, f"Январь: /1, Февраль: /2,  Март: /3, Апрель: /4, Май: /5,")
        tb.send_message(message.from_user.id, f"Сентябрь: /9, Октябрь: /10, Ноябрь: /11, Декабрь: /12")
        tb.register_next_step_handler(message, get_month); # следующий шаг – функция get_month_day
  except:
    tb.send_message(message.from_user.id, f"Для нового поиска нажми на /poehali")


def get_month(message): # получаем что будем выводить
    try:
      global month_bot
      month_bot = message.text
      df_date_new = df_date[df_date['month'] == int(''.join(filter(str.isdigit, month_bot)))]
      tb.send_message(message.from_user.id, 'Выбери дату начала недели, за эту неделю отправится отчет:')
      for i in range(len(df_date_new)):
        day = list(df_date_new['day'])
        month = list(df_date_new['month'])
        year = list(df_date_new['year'])
        tb.send_message(message.from_user.id, f"/{day[i]:02d}_{month[i]:02d}_{year[i]}")
      tb.register_next_step_handler(message, get_day)
    except:
      tb.send_message(message.from_user.id, f"Для нового поиска нажми на /poehali")


def get_day(message): # получаем что будем выводить
    try:
      global day_bot
      day_bot = message.text
      day_bot = day_bot.replace("_", ".")
      day_bot = day_bot.replace("/", "")    

      tb.send_message(message.from_user.id, ''' Выберете тип отчета:
      1. Изучаемые темы на неделю: /give_themes        
      2. Оценки за неделю: /give_marks       
      3. Рассписание на неделю: /give_schedule  
      4. Домашнее задание на неделю: /give_homeworks            
      ''')
      tb.register_next_step_handler(message, give_report); # следующий шаг – функция get_features
    except:
      tb.send_message(message.from_user.id, f"Для нового поиска нажми на /poehali")

def give_report(message): # получаем параметр для вывода полного отчета за неделю
    
    if message.text == '/give_themes':
      try:
          give_themes_soup(day_bot)
          # sendDocument
          doc = open(f"Изучаемые_темы_{day_bot}.html", 'rb')
          tb.send_document(message.from_user.id, doc)
          tb.send_message(message.from_user.id, f"Новый отчет /poehali")  
      except:
          tb.send_message(message.from_user.id, f"Для нового поиска нажми на /poehali") 

    if message.text == '/give_marks':

      try:
          give_marks_soup(day_bot)
          # sendDocument
          doc = open(f"Оценки_{day_bot}.html", 'rb')
          tb.send_document(message.from_user.id, doc)
          tb.send_message(message.from_user.id, f"Новый отчет /poehali")  
      except:
          tb.send_message(message.from_user.id, f"Для нового поиска нажми на /poehali") 

    if message.text == '/give_schedule':

      try:
          give_schedule_soup(day_bot)
          # sendDocument
          doc = open(f"Рассписание_{day_bot}.html", 'rb')
          tb.send_document(message.from_user.id, doc)
          tb.send_message(message.from_user.id, f"Новый отчет /poehali")  
      except:
          tb.send_message(message.from_user.id, f"Для нового поиска нажми на /poehali") 

    if message.text == '/give_homeworks':

      try:
          give_homeworks_soup(day_bot)
          # sendDocument
          doc = open(f"Домашнее_задание_{day_bot}.html", 'rb')
          tb.send_document(message.from_user.id, doc)
          tb.send_message(message.from_user.id, f"Новый отчет /poehali")  
      except:
          tb.send_message(message.from_user.id, f"Для нового поиска нажми на /poehali")  



tb.polling(none_stop=True, interval=0)
