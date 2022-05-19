'''
VMP 2022-05-19: document stopwords
'''

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
total_stopwords = stopwords.words('english')

with open('/work/50114/twitter/nlp/basic_analysis/stopwords.txt', 'w') as filehandle:
    for stopword in total_stopwords:
        filehandle.write('%s, ' % stopword)