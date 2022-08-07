# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 19:23:55 2022

@author:  https://github.com/vik1109/

подготовка выборок:
    test.csv - тестовая выборка
    train.csv - тренироваочная выборка
    rest.csv - остаток

"""
#imports
import pandas as pd
#местоположение файла 'msg.csv'
msg_file = "DB/msg.csv"
#количество строк для отбора
test_num_of_stings = 200
train_num_of_stings = 800
#имя целевого файла
test_file = "DB/test.csv"
train_file = "DB/train.csv"
rest_file = "DB/rest.csv"

#загрузка данных
df = pd.read_csv(msg_file, index_col = 0, sep = ';', encoding='utf-8-sig', on_bad_lines='skip')

#подготовим тестовую выборку размером test_num_of_stings
test = df.sample(test_num_of_stings, random_state = 12345)
#удалим строки переданные в тест из изначальной выборки
df = df.drop(test.index).reset_index(drop = True)
test = test.reset_index(drop = True)

#подготовим обучающую выборку выборку размером train_num_of_stings
train = df.sample(train_num_of_stings, random_state = 12345)
#удалим строки переданные в обучение из изначальной выборки
df = df.drop(train.index).reset_index(drop = True)
train = train.reset_index(drop = True)

try:
    test.to_csv(test_file, sep = ';', encoding='utf-8-sig')
    print('Test успешно!!')
    train.to_csv(train_file, sep = ';', encoding='utf-8-sig')
    print('Train успешно!!')
    df.to_csv(rest_file, sep = ';', encoding='utf-8-sig')
    print('Rest успешно!!')
except:
    print('Ошибка доступа к файлу!!!!')
