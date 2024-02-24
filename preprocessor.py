'''
@author: Atish Sinha
'''

import collections
from nltk.stem import PorterStemmer
import re
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')


class Preprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.ps = PorterStemmer()

    def get_doc_id(self, doc):
        """ Splits each line of the document, into doc_id & text.
            Already implemented"""
        arr = doc.split()
        return int(arr[0]), arr[1:]

    def tokenizer(self, text):
        """ Implement logic to pre-process & tokenize document text.
            Write the code in such a way that it can be re-used for processing the user's query.
            To be implemented."""
        processed_lines = []
        arr = [val.lower() for val in text]
        # print(arr)
        line = ' '.join(arr)
        line = re.sub(r'[\u2010-\u2015-]', ' ', line)
        line = re.sub(r'\.', '', line)
        line = re.sub(r'/', ' ', line)
        line = re.sub(r'[^a-zA-Z0-9\s]', ' ', line)
        line = re.sub(r'\s+', ' ', line)
        tokens = line.split()
        tokens = [token for token in tokens if token not in self.stop_words]
        stemmed_tokens = [self.ps.stem(token) for token in tokens]
        processed_line = ' '.join(stemmed_tokens).strip()
        processed_lines.append(processed_line)
        processed_document = processed_lines
        return processed_document
