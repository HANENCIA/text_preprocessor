import pandas as pd
import re

from konlpy.tag import Hannanum
from konlpy.tag import Kkma
from konlpy.tag import Komoran
from konlpy.tag import Mecab
from konlpy.tag import Okt

from collections import Counter
from itertools import chain


# Konlpy를 이용하여 명사 추출
#
# 1. Sample Data/Input Exmaple
# input_data = ['구아바 구아바 망고를 유혹하네 딱 걸렸네, 포시즌을 낳았네', '젖소방은 없습니다.']
# konlpy_opt = 'Hannanum', 'Kkma', 'Komoran', 'Mecab', 'Okt' 중 1개 입력
# Konlpy tag Package: https://konlpy-ko.readthedocs.io/ko/latest/api/konlpy.tag/
# input: output_data = make_noun_voca_list(input_data, konlpy_opt)
#
# 2. Output Example/Data
# output_data: [['구아바', '구아바', '망고', '유혹', '포', '시즌'], ['젖', '소방']]

def make_noun_voca_list(raw_list, konlpy_opt):
    noun_voca_list = []
    assert konlpy_opt in ['Hannanum', 'Kkma', 'Komoran', 'Mecab', 'Okt']

    if konlpy_opt == 'Hannanum':
        nlp = Hannanum()
    elif konlpy_opt == 'Kkma':
        nlp = Kkma()
    elif konlpy_opt == 'Komoran':
        nlp = Komoran()
    elif konlpy_opt == 'Mecab':
        nlp = Mecab()
    elif konlpy_opt == 'Okt':
        nlp = Okt()

    for line in raw_list:
        if type(line).__name__ == 'float' or type(line).__name__ == 'int':
            noun_voca_list.append('')
        else:
            noun_voca_list.append(nlp.nouns(' '.join(re.compile('[가-힣0-9]+').findall(line))))

    return noun_voca_list


# 단어 리스트를 띄어쓰기를 기준으로 join
#
# 1. Sample Data/Input Exmaple
# input_data = [['사과', '바나나', '포도'], ['수박', '파인애플', '구아바']]
# input: output_data = make_sentence_list_from_voca_list(input_data)
#
# 2. Output Example/Data
# output_data: ['사과 바나나 포도', '수박 파인애플 구아바']

def make_sentence_list_from_voca_list(voca_list):
    sentence_list = []
    for voca_line in voca_list:
        sentence_list.append(" ".join(voca_line))
    return sentence_list


# 문장을 띄어쓰기를 기준으로 분할하여 list화
#
# 1. Sample Data/Input Exmaple
# input_data = ['사과 바나나 포도', '수박 파인애플 구아바']
# output_data = make_voca_list_from_sentence_list(input_data)
#
# 2. Output Example/Data
# output_data: [['사과', '바나나', '포도'], ['수박', '파인애플', '구아바']]

def make_voca_list_from_sentence_list(sentence_list):
    voca_list = []
    for sentence_line in sentence_list:
        voca_list.append(sentence_line.split(' '))
    return voca_list


# KoNLPy에서 추출된 한글 명사 리스트에서 두 글자로 이루어진 단어만 추출 후 STOPWORDS 삭제
#
# 1. Sample Data/Input Exmaple
# input_data = [['사과', '바나나', '포도'], ['수박', '파인애플', '구아바'], ['딸기', '산딸기']]
# stopwords = ['딸기']
# output_data = remove_stopwords(input_data, stopwords)
#
# 2. Output Example/Data
# output_data: [['사과', '바나나', '포도'], ['수박', '파인애플', '구아바'], ['산딸기']]

def remove_stopwords(voca_list, stopword_list):
    stopword_replaced_voca_list = []
    sentence_list = make_sentence_list_from_voca_list(voca_list)
    re_space = re.compile(r'\s+')

    for line in sentence_list:
        for stopword in stopword_list:
            line = ' '.join(re.compile('[가-힣]{2,}').findall(line))
            re_word = re.compile(r'\b{0}\b'.format(stopword))
            line = (re_space.sub(' ', re_word.sub('', line)).strip())
        stopword_replaced_voca_list.append(line.split(' '))

    return stopword_replaced_voca_list


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


def main():
    raw_path = 'data/sample_newspaper.csv'
    raw_list_name = '기사'

    output_path = 'data/sample_newspaper_modified.csv'
    output_list_name = '기사_명사'

    raw_df = pd.read_csv(raw_path, sep=',', encoding='utf-8')
    raw_list = raw_df[raw_list_name]

    raw_noun_voca_list = make_noun_voca_list(raw_list, 'Okt')

    stopwords = pd.ExcelFile('stopwords_ko_20191105.xlsx').parse('STOPWORDS').STOPWORDS
    stopwords_custom = ['우리', '최근']

    stopword_replaced_voca_list = remove_stopwords(raw_noun_voca_list, stopwords)
    stopword_replaced_voca_list = remove_stopwords(stopword_replaced_voca_list, stopwords_custom)

    print_most_common_words(stopword_replaced_voca_list, 200)

    raw_noun_sentence_list = make_sentence_list_from_voca_list(stopword_replaced_voca_list)
    raw_df[output_list_name] = raw_noun_sentence_list

    raw_df.to_csv(output_path, sep=',', index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    main()
