import pandas as pd
import re

import html.parser
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

from collections import Counter
from itertools import chain


# Natural Language Toolkit(NLTK)을 이용하여 영어 전처리
#
# 1. Sample Data/Input Exmaple
# input_data = ['There is no cow level.', 'Power Overwhelming.']
# stem_opt = 'stem', 'lem', 'N' 중 1개 입력
# input: output_data = make_preprocessed_voca_list(raw_list, stem_opt)
#
# 2. Output Example/Data
# output_data: [['cow', 'level'], ['power', 'overwhelm']]

def make_preprocessed_voca_list(raw_list, stem_opt):
    preprocessed_voca_list = []
    assert stem_opt in ['stem', 'lem', 'N']
    stopword_list = set(stopwords.words('english'))

    if stem_opt == 'stem':
        stem = PorterStemmer()
    elif stem_opt == 'lem':
        stem = WordNetLemmatizer()

    for line in raw_list:
        if type(line).__name__ == 'float':
            preprocessed_voca_list.append('')
        else:
            sentence_temp = html.unescape(line).lower()
            sentence_temp = re.compile('[a-z]{3,}').findall(sentence_temp)
            sentence_temp = list(filter(lambda x: x not in stopword_list, sentence_temp))
            if stem_opt == 'stem':
                sentence_temp = [stem.stem(w) for w in sentence_temp]
            elif stem_opt == 'lem':
                sentence_temp = [stem.lemmatize(w) for w in sentence_temp]
            preprocessed_voca_list.append(sentence_temp)

    return preprocessed_voca_list

# 전처리된 영어 단어 리스트에서 STOPWORDS 삭제
#
# 1. Sample Data/Input Exmaple
# input_data = [['cow', 'level'], ['power', 'overwhelm']]
# stopwords = ['cow']
# output_data = remove_stopwords(input_data, stopwords)
#
# 2. Output Example/Data
# output_data: [['level'], ['power', 'overwhelm']]


def remove_stopwords(voca_list, stopword_list):
    stopword_replaced_voca_list = []

    for line in voca_list:
        stopword_replaced_voca_list.append(list(filter(lambda x: x not in stopword_list, line)))

    return stopword_replaced_voca_list


# 단어 리스트를 띄어쓰기를 기준으로 join
#
# 1. Sample Data/Input Exmaple
# input_data = [['cow', 'level'], ['power', 'overwhelm']]
# input: output_data = make_sentence_list_from_voca_list(input_data)
#
# 2. Output Example/Data
# output_data: ['cow level', 'power overwhelm']

def make_sentence_list_from_voca_list(voca_list):
    sentence_list = []
    for voca_line in voca_list:
        sentence_list.append(" ".join(voca_line))
    return sentence_list


# 단어 빈도순 출력
#
# 1. Sample Data/Input Exmaple
# input_data = [['사과', '바나나', '사과'], ['딸기', '사과', '바나나', '수박']]
# top_count = n (int, 상위 n위)
# print_most_common_words(input_data, 4)
#
# 2. Output Example/Data
# output_data: [('사과', 3), ('바나나', 2), ('딸기', 1), ('수박', 1)]
# 주의: 동 순위가 있다면 앞에 있는 element 순서대로 끊어짐 (예: [('사과', 3), ('바나나', 2), ('딸기', 1)])

def print_most_common_words(voca_list, top_count):
    print(Counter(list(chain.from_iterable(voca_list))).most_common(top_count))


# 단어 빈도 데이터 저장
#
# 1. Sample Data/Input Exmaple
# input_data = [['사과', '바나나', '사과'], ['딸기', '사과', '바나나', '수박']]
# top_count = n (int, 상위 n위, 저장 CSV 파일 경로)
# print_most_common_words(input_data, 4)
#
# 2. Output Example/Data
# output_data: CSV 파일
# Column Name: WORD, COUNT
# 주의: 동 순위가 있다면 앞에 있는 element 순서대로 끊어짐 (예: [('사과', 3), ('바나나', 2), ('딸기', 1)])

def save_most_common_words(voca_list, top_count, output_path):
    word_count_list = Counter(list(chain.from_iterable(voca_list))).most_common(top_count)
    word_list = []
    count_list = []
    for idx in range(len(word_count_list)):
        word_list.append(word_count_list[idx][0])
        count_list.append(word_count_list[idx][1])
    word_count_df = pd.DataFrame.from_records(zip(word_list, count_list), columns=['WORD', 'COUNT'])

    word_count_df.to_csv(output_path, sep=',', index=False, encoding='utf-8-sig')


def main():
    raw_path = 'data/sample_wos.csv'
    raw_list_name = 'ABSTRACT'

    output_path = 'data/sample_wos_modified.csv'
    output_list_name = 'ABSTRACT_FIXED'

    common_words_path = 'data/sample_wos_common_word.csv'

    raw_df = pd.read_csv(raw_path, sep=',', encoding='utf-8')
    raw_list = raw_df[raw_list_name]

    raw_voca_list = make_preprocessed_voca_list(raw_list, 'stem')

    stopwords_custom = ['use']

    stopword_replaced_voca_list = remove_stopwords(raw_voca_list, stopwords_custom)

    print_most_common_words(stopword_replaced_voca_list, 200)

    save_most_common_words(stopword_replaced_voca_list, 200, common_words_path)

    raw_sentence_list = make_sentence_list_from_voca_list(stopword_replaced_voca_list)
    raw_df[output_list_name] = raw_sentence_list

    raw_df.to_csv(output_path, sep=',', index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    main()
