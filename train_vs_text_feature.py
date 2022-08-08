# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 15:39:51 2022

@author: https://github.com/vik1109/
"""
#imports
from catboost import CatBoostClassifier, Pool
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sklearn.metrics import f1_score, recall_score, precision_score, roc_auc_score
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

train_df = pd.read_csv('DB/train.csv', index_col = 0, sep = ';', encoding='utf-8-sig', on_bad_lines='skip')
test_df = pd.read_csv('DB/test.csv', index_col = 0, sep = ';', encoding='utf-8-sig', on_bad_lines='skip')

X = train_df.drop(['date', 'user','target', 'site_', 'allergens_', 'medicins_', 'symptom_'], axis = 1)
y = train_df['target']
X = X.fillna('other')

X_test = test_df.drop(['date', 'user', 'target', 'site_', 'allergens_', 'medicins_', 'symptom_'], axis = 1)
y_test = test_df['target']
X_test = X_test.fillna('other') 

cat_features = ['city', 'moscow_district', 'region', 'area']
numeric_features = ['site', 'allergens', 'medicins', 'symptom', 'negative', 'positive']
text_features = ['msg']

scaler = StandardScaler()
scaler.fit(X[numeric_features])
X[numeric_features] = scaler.transform(X[numeric_features])
X_test[numeric_features] = scaler.transform(X_test[numeric_features])

train_data = Pool(X, label = y, cat_features=cat_features, text_features = text_features)
test_data = Pool(X_test, label = y_test, cat_features=cat_features, text_features = text_features)

classes = np.unique(y)
weights = compute_class_weight(class_weight='balanced', classes=classes, y=y)

model_ct =  CatBoostClassifier(verbose = 10,
                               eval_metric='AUC',
                               max_depth=8,
                               learning_rate = 0.1,
                               class_weights = weights,
                               early_stopping_rounds=100)
model_ct.fit(train_data, plot = True, use_best_model = True, eval_set = test_data)
print("F1_Score", f1_score(y_test, model_ct.predict(X_test)))
print("F1_Score на константной модели", f1_score(y_test, pd.Series([1]*len(y_test))))
print("precision_score", precision_score(y_test, model_ct.predict(X_test)))
print("recall_score", recall_score(y_test, model_ct.predict(X_test)))
print("ROC_AUC_SCORE", roc_auc_score(y_test, model_ct.predict_proba(X_test)[:, 1]))
model_ct.save_model('model/cat_model_vs_text')
print('Обучение закончено, модель сохранена.')
