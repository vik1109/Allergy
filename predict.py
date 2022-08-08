# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 21:06:43 2022

@author: https://github.com/vik1109/
"""
from catboost import CatBoostClassifier, Pool
import pandas as pd

X_rest = pd.read_csv('DB/rest.csv', index_col = 0, sep = ';', encoding='utf-8-sig', on_bad_lines='skip')

X = X_rest.drop(['date', 'user', 'msg' , 'site_', 'allergens_', 'medicins_', 'symptom_'], axis = 1)
X = X.fillna('other')

cat_features = ['city', 'moscow_district', 'region', 'area']
numeric_features = ['site', 'allergens', 'medicins', 'symptom', 'negative', 'positive']

model = CatBoostClassifier()

prediction = model.load_model('model/cat_model', format='cbm').predict_proba(X)

X_rest['predict'] = pd.Series(prediction[:, 1])

X_rest.to_csv('DB/prediction.csv', sep = ';', encoding='utf-8-sig')