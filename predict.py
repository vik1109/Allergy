# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 21:06:43 2022

@author: 72090
"""
from catboost import CatBoostClassifier, Pool
import pandas as pd

train_df = pd.read_csv('DB/rest.csv', index_col = 0, sep = ';', encoding='utf-8-sig', on_bad_lines='skip')

X_rest = train_df.drop(['date', 'user', 'msg'], axis = 1)
X_rest = X_rest.fillna('other')

cat_features = ['city', 'moscow_district', 'region', 'area']
numeric_features = ['site', 'allergens', 'medicins', 'symptom', 'negative', 'positive']

model = CatBoostClassifier()

prediction = model.load_model('model/cat_model', format='cbm').predict_proba(X_rest)

train_df['predict'] = pd.Series(prediction[:, 1])

train_df.to_csv('DB/prediction.csv', sep = ';', encoding='utf-8-sig')