# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 16:00:52 2022

@author: https://github.com/vik1109/

Получаем на фход выгрузку от сервиса https://vk.barkov.net/comments.aspx
отбираем топонимы
выгружаем в папку DB подготовленный файл 'msg.cvs', sep = ';', encoding='utf-8-sig' 

"""

#imports
import pandas as pd
from work_func import file_to_list
import re

#загружаем файл и разбиваем файл на список

class AdressSearch:
    def __init__(self, msg):
        """
        Инициализируем все переменные:
        df - таблица пандас для зранения данных
        adresses_df - словарь топонимов
        drug_df - словарь лекарств
        body_df - словарь симптомов
        navec - русские эмбединги
        ner - модель
        """    
        self.df = self.base_create(msg)
        self.df['city'] =''
        self.df['moscow_district'] =''
        self.df['region'] = ''
        self.df['area'] = ''
        
        self.cities = pd.read_csv('DB/cities_utf_sig.csv', sep = ';')
        self.regions = pd.read_csv('DB/regions.csv', sep = ';')
        self.areas = pd.read_csv('DB/area.csv', sep = ';')
        self.moscow_districts = pd.read_csv('DB/moscow_districts.csv', sep = ';')
        
    def base_create(self, msg):
        listed_data = [] #будущий список сообщений
        tmp_msg = ''     #временная переменная для сообщения
        tmp_user = ''    #временная переменная для имени пользователя
        tmp_date = ''    #временная переменная для даты
        quota = 0        #переменная для хранения индекса запятой
        
        #интересующие нас сообщения хранятся в последнем элементе списка first_split
        #еще раз разбиваем список
        second_split = msg[-1].split('\n\n________________\n\n')

        #цикл поиска запятой и символа '\n'
        for item in second_split:
            for i in range(len(item)):
                #запомним индекс запятой
                if item[i] == ',':
                    quota = i
                #найдем первый \n
                if item[i] == '\n':
                    #подстрока с сообщением. от символа \n до конца строки
                    tmp_msg = item[(i+1):].strip()
                    if tmp_msg.find(']') != -1:
                        tmp_msg = tmp_msg[(tmp_msg.find(']')+3):]
                    #подстрока с датой от начала до запятой
                    tmp_date = item[:(quota)]
                    tmp_date = ' '.join(tmp_date.split(' ')[:-1]).strip() #оставим только дату
                    #подстрока с именем пользователя от запятой до \n
                    tmp_user = item[(quota+1):(i)].strip()
                    #заканчиваем цикл досрочно
                    break
            #делаем список [tmp_date, tmp_user, tmp_msg] и закидиваем в списое сообщений
            listed_data.append([tmp_date, tmp_user, tmp_msg])
            #не обязательно, но мне кажется так лучше, что бы случайностей не было
            tmp_msg = ''
            tmp_user = ''
            tmp_date = ''
            quota = 0
        #из списка делаем датафрейм
        df = pd.DataFrame(listed_data, columns = ['date', 'user', 'msg'])

        #уберем из сообщений все смайлики и лишние пробелы
        df['msg'] = df['msg'].map(lambda x: re.sub('[^.0-9а-яА-ЯЁё,]', ' ', x))
        df['msg'] = df['msg'].map(lambda x: re.sub(r"^\s+|\s+$", "", x))

        #удалим строки, где поле msg пустое
        df = df.drop(df[(df['msg']=='') ].index).reset_index(drop = True)
        return df        
        
    def pars_all(self):
        """
        Функция, которая по этапно вызывает:
        1. поиск по словарю топонимов городов
        2. поиск по словарю топонимов округов Москвы
        3. поиск по словарю топонимов регионов.
        """
        print("Начинаем поиск по словарю топонимов городов.")
        self.city_parser() #поиск оп словарю топонимов городов
        
        print("Начинаем поиск по словарю топонимов округов Москвы.")
        self.moscow_district_parser() #поиск оп словарю топонимов округов Москвы
        
        print("Начинаем поиск по словарю топонимов регионов.")
        self.region_parser() #поиск оп словарю топонимов округов Москвы
        
        print("Начинаем поиск по словарю топонимов районов.")
        self.area_parser() #поиск оп словарю топонимов районов     
        
          
    def re_search(self, pars_value, msg):
        return re.search(fr"\b{pars_value}\b", msg, re.I) is not None
        
    def final(self):
        for i in range(len(self.df)):
            if self.df['city'][i] != '':
                self.df.loc[i, 'final'] = self.df['city'][i]
            else:
                if self.df['ner_predict'][i] != '':
                    self.df.loc[i, 'final'] = self.df['ner_predict'][i]
                
        
    def city_parser(self): #парсинг по словарю городов
        dict_counter = len(self.cities)
        print("Начало поиска топонимов по городам....")
        for i in range(dict_counter):
            if i == dict_counter//3: print("Обработана треть словаря топонимов.")
            if i == (dict_counter//3)*2: print("Обработаны две трети словаря топонимов.")
            for j in range(len(self.df)):
                if self.re_search(self.cities['re'][i], self.df['msg'][j]):
                    if self.df.loc[j, 'city'] == '':
                        self.df.loc[j, 'city'] = self.cities['city'][i]
                    else:
                        if self.df.loc[j, 'city'] != self.df['city'][j]:
                            self.df.loc[j, 'city'] = self.df.loc[j, 'city'] + ', ' + self.cities['city'][i]
        print("Поиcк топонимов закончен. Обработан словарь размером:", dict_counter)
    
    def moscow_district_parser(self): #парсинг по словарю округов Москвы
        dictionary = self.moscow_districts
        dict_counter = len(dictionary)
        print("Начало поиска топонимов по округам Москвы....")
        for i in range(dict_counter):
            if i == dict_counter//3: print("Обработана треть словаря топонимов по округам Москвы.")
            if i == (dict_counter//3)*2: print("Обработаны две трети словаря топонимов по округам Москвы.")
            for j in range(len(self.df)):
                if re.search(fr"\b{dictionary['re'][i]}\b", self.df['msg'][j], re.I) is not None:
                    if self.df.loc[j, 'moscow_district'] == '':
                        self.df.loc[j, 'moscow_district'] = dictionary['district'][i]
                    else:
                        if dictionary['district'][i] != self.df.loc[j, 'moscow_district']:
                            self.df.loc[j, 'moscow_district'] = self.df.loc[j, 'moscow_district'] + ', ' + dictionary['district'][i]
        print("Поиcк топонимов  по округам Москвы закончен. Обработан словарь размером:", dict_counter)
        
    def region_parser(self):  #парсинг по словарю регионов
        dictionary = self.regions
        dict_counter = len(dictionary)
        print("Начало поиска топонимов по регионам....")
        for i in range(dict_counter):
            if i == dict_counter//3: print("Обработана треть словаря топонимов по регионам.")
            if i == (dict_counter//3)*2: print("Обработаны две трети словаря топонимов по регионам.")
            for j in range(len(self.df)):
                if self.re_search(dictionary['re'][i], self.df['msg'][j]): #re.search(fr"\b{dictionary['re'][i]}\b", self.df['msg'][j], re.I) is not None:
                    if self.df['region'][j] == '':
                        self.df.loc[j, 'region'] = dictionary['region'][i]
                    else:
                        if dictionary['region'][i] != self.df['region'][j]:
                            self.df.loc[j, 'region'] = self.df.loc[j, 'region'] + ', ' + dictionary['region'][i]
        print("Поиcк топонимов  по регионам. Обработан словарь размером:", dict_counter)
    
    def area_parser(self): #парсинг по словарю районов
        dictionary = self.areas
        dict_counter = len(dictionary)
        print("Начало поиска топонимов по районам....")
        for i in range(dict_counter):
            if i == dict_counter//3: print("Обработана треть словаря топонимов по районам.")
            if i == (dict_counter//3)*2: print("Обработаны две трети словаря топонимов по районам.")
            for j in range(len(self.df)):
                if self.re_search(dictionary['re'][i], self.df['msg'][j]): #re.search(fr"\b{dictionary['re'][i]}\b", self.df['msg'][j].lower()) is not None:
                    if self.df['area'][j] == '':
                        self.df.loc[j, 'area'] = dictionary['area'][i]
                    else:
                        if dictionary['area'][i] != self.df['area'][j]:
                            self.df.loc[j, 'area'] = self.df.loc[j, 'area'] + ', ' + dictionary['area'][i]
        print("Поиcк топонимов  по районам. Обработан словарь размером:", dict_counter)
                
    def to_csv(self, name = 'DB/msg.csv'):
        self.df = self.df.drop(self.df[(self.df['city'] =='') & (self.df['moscow_district'] =='') & (self.df['region'] == '') & (self.df['area'] == '')].index).reset_index(drop = True)
        self.df.to_csv(name, sep = ';', encoding='utf-8-sig')
        print('Successful!!')
        
if __name__ == "__main__":
    db = AdressSearch(file_to_list('text/posts.txt', '\n--------------------------\n'))
    db.pars_all()
    db.to_csv()

    