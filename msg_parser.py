# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 17:37:54 2022

@author: https://github.com/vik1109/

Файл парсинга сообщений. Работа по умалчанию идет с файлом "DB/msg.csv"

Результат выгружается в файл 'DB/parsed_msg.csv'

"""
#imports
import pandas as pd

from work_func import file_to_list
from yargy import rule, Parser, or_
from yargy.pipelines import morph_pipeline
from yargy.interpretation import fact
#from yargy.predicates import gram#, #dictionary, eq#, normalized

#список препаратов
medicine_list = set(file_to_list('text/medicine.txt', separator = '\n'))
#загружаем список аллергенов
allergen_list = set(file_to_list('text/allergen.txt', separator = '\n'))
#загружаем список мест проявления аллергии
site_of_allergy_list = set(file_to_list('text/site.txt', separator = '\n'))
#загружаем список симптомов
symptom_list = set(file_to_list('text/symptoms.txt', separator = '\n'))
#загружаем список негативно окрашенных высказываний
negative_list = set(file_to_list('text/negative.txt', separator = '\n'))
#загружаем список позитивно окрашенных высказываний
positive_list = set(file_to_list('text/positive.txt', separator = '\n'))

#местоположение файла 'msg.csv'
msg_file = "DB/rest.csv"



#объявим факт - SiteOfAllergy - место проявления аллергической реакции
SiteOfAllergy = fact(
    'SiteOfAllergy',
    ['site']
)

#объявим факт - Symptom - симптом проявления аллергической реакции
Symptom = fact(
    'Symptom',
    ['name']
)

#объявим факт - Allergen - аллерген
Allergen = fact(
    'Allergen',
    ['name']
)

#объявим факт - Medicine - лекарства
Medicine = fact(
    'Medicine',
    ['name']
)


#объявим факт - Negativation - негативное высказывание про аллергию
Negativation = fact(
    'Negativation',
    ['neg']

)

#объявим факт - Positive - позитивное высказывание про аллергию
Positive = fact(
    'Positive',
    ['pos']

)


##############################################
#                                            #
#           WORK WIHT SITE_OF_ALLERGY        #
#                                            #
##############################################

#морф пайплайн для мест реакции на аллерген
SITE_OF_ALLERGY_PIPELINE = morph_pipeline(
    site_of_allergy_list
).interpretation(
    SiteOfAllergy.site.normalized()
)

SITE_OF_ALLERGY_RULE = rule(
    SITE_OF_ALLERGY_PIPELINE,
).interpretation(
    SiteOfAllergy
)

##############################################
#                                            #
#              WORK WIHT SYMPTOMS            #
#                                            #
##############################################

#морф пайплайн для симптомов
SYMPTOM_PYPLEINE = morph_pipeline(
    symptom_list
).interpretation(
    Symptom.name.normalized()
)

SYMPTOM_RULE = rule(
    SYMPTOM_PYPLEINE
).interpretation(
    Symptom
)

##############################################
#                                            #
#              WORK WIHT MEDUCINE            #
#                                            #
##############################################

#пайплан для препаратов от аллергии
MEDICINE_PIPELINE = morph_pipeline(
    medicine_list
).interpretation(
    Medicine.name #.normalized().custom(lambda x: x.title())
)

MEDICINE_RULE = rule(
    MEDICINE_PIPELINE
).interpretation(
    Medicine
)

##############################################
#                                            #
#              WORK WIHT ALLERGEN            #
#                                            #
##############################################

#морф пайплайн для аллергенов
ALLERGEN_PIPELINE = morph_pipeline(
    allergen_list
).interpretation(
    Allergen.name.normalized().custom(lambda x: x.title())
)

ALLERGEN_RULE = rule(
    ALLERGEN_PIPELINE
).interpretation(
    Allergen
)

##############################################
#                                            #
#             NEGATIVE    RULE               #
#                                            #
##############################################

#морф пайплайн для негативно окрашенных высказываний
NEGATIVE_PIPELINE = morph_pipeline(
    negative_list
    ).interpretation(
        Negativation.neg.const('нет')
        )

NEGATIVE_RULE = rule(
    NEGATIVE_PIPELINE
).interpretation(
    Negativation
)

##############################################
#                                            #
#             POSITEVE    RULE               #
#                                            #
##############################################

#морф пайплайн для позитивно окрашенных высказываний
POSITEVE_PIPELINE = morph_pipeline(
    positive_list
    ).interpretation(
    Positive.pos.const('есть')
)

POSITEVE_RULE = rule(
    POSITEVE_PIPELINE
).interpretation(
    Positive
)

ALLERGY = or_(
    
    SITE_OF_ALLERGY_RULE,
    MEDICINE_RULE,
    SYMPTOM_RULE,
    ALLERGEN_RULE
    
)

smpl = pd.read_csv(msg_file, index_col = 0, sep = ';', encoding='utf-8-sig', on_bad_lines='skip')


parser = Parser(SITE_OF_ALLERGY_RULE)
smpl['site'] = smpl['msg'].apply(lambda x: len([match.fact.site  for match in parser.findall(x)]))
smpl['site_'] = smpl['msg'].apply(lambda x: ', '.join([match.fact.site  for match in parser.findall(x)]))
print('Site done!')
parser = Parser(ALLERGEN_RULE)
smpl['allergens'] = smpl['msg'].apply(lambda x: len([match.fact.name for match in parser.findall(x)]))
smpl['allergens_'] = smpl['msg'].apply(lambda x: ', '.join([match.fact.name for match in parser.findall(x)]))
print('Allergens done!')
parser = Parser(MEDICINE_RULE)
smpl['medicins'] = smpl['msg'].apply(lambda x: len([match.fact.name for match in parser.findall(x)]))
smpl['medicins_'] = smpl['msg'].apply(lambda x: ', '.join([match.fact.name for match in parser.findall(x)]))
print('Medicins done!')
parser = Parser(SYMPTOM_RULE)
smpl['symptom'] = smpl['msg'].apply(lambda x: len([match.fact.name for match in parser.findall(x)]))
smpl['symptom_'] = smpl['msg'].apply(lambda x: ', '.join([match.fact.name for match in parser.findall(x)]))
print('Symptom done!')
parser = Parser(NEGATIVE_RULE)
smpl['negative'] = smpl['msg'].apply(lambda x: len([match.fact.neg for match in parser.findall(x)]))
print('Negative done!')
parser = Parser(POSITEVE_RULE)
smpl['positive'] = smpl['msg'].apply(lambda x: len([match.fact.pos for match in parser.findall(x)]))
print('Positive done!')
try:
    smpl.to_csv(msg_file, sep = ';', encoding='utf-8-sig')
    print('Успешно!!')
except:
    print('Ошибка доступа к файлу!!!!')