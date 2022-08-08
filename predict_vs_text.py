# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 21:06:43 2022

@author: 72090
"""
from catboost import CatBoostClassifier, Pool
import pandas as pd

#Загрузка сообщений
X_rest = pd.read_csv('DB/rest.csv', index_col = 0, sep = ';', encoding='utf-8-sig', on_bad_lines='skip')

#Удаляем лишние столбцы
X_rest = X_rest.drop(['date', 'user'], axis = 1)
X_rest = X_rest.fillna('other')

#списки типов столбцов
cat_features = ['city', 'moscow_district', 'region', 'area']
numeric_features = ['site', 'allergens', 'medicins', 'symptom', 'negative', 'positive']
text_features = ['msg']

#подготовка пула данных для модели
data = Pool(X_rest, cat_features=cat_features, text_features = text_features)

#инициализация модели
model = CatBoostClassifier()

#Загружаем модель и запускаем предсказание вероятностей
prediction = model.load_model('model/cat_model_vs_text', format='cbm').predict_proba(data)

#сохраняем столбец с вероятностями
X_rest['predict'] = pd.Series((prediction[:, 1]> 0.3411492842925379)*1)

#сохраняем файл с предсказаниями
X_rest.to_csv('DB/prediction_vs_test.csv', sep = ';', encoding='utf-8-sig')