'''
@author: Atish Sinha
Institute: University at Buffalo
'''

from linkedlist import LinkedList
from collections import OrderedDict


class Indexer:
    def __init__(self):
        """ Add more attributes if needed"""
        self.inverted_index = OrderedDict({})
        self.freq_calc = {}
        self.document = {}

    def get_index(self):
        """ Function to get the index.
            Already implemented."""
        return self.inverted_index

    def generate_inverted_index(self, doc_id, document):
        """ This function adds each tokenized document to the index. This in turn uses the function add_to_index
            Already implemented."""
        # posting_list = OrderedDict({})
        # fre_calc = {}
        # self.document = document
        for values in document:
            if values in self.freq_calc:
                if doc_id in self.freq_calc[values]:
                    self.freq_calc[values][doc_id] += 1
                else:
                    self.freq_calc[values][doc_id] = 1
            else:
                self.freq_calc[values] = {doc_id: 1}
            if values in self.inverted_index:
                self.inverted_index[values].insert_insertion_sort(doc_id)
            else:
                self.inverted_index[values] = LinkedList()
                self.inverted_index[values].insert_insertion_sort(doc_id)
        # print(self.inverted_index)
        return self.inverted_index

    def add_to_index(self, term_, doc_id_):
        """ This function adds each term & document id to the index.
            If a term is not present in the index, then add the term to the index & initialize a new postings list (linked list).
            If a term is present, then add the document to the appropriate position in the posstings list of the term.
            To be implemented."""
        raise NotImplementedError

    def sort_terms(self):
        """ Sorting the index by terms.
            Already implemented."""
        sorted_index = OrderedDict({})
        for k in sorted(self.inverted_index.keys()):
            sorted_index[k] = self.inverted_index[k]
        self.inverted_index = sorted_index

    def calculate_tf_idf(self):
        """ Calculate tf-idf score for each document in the postings lists of the index.
            To be implemented."""
        for key, vals in self.inverted_index.items():
            curr = vals.start_node
            idf = vals.idf
            while curr is not None:
                curr.tf = (self.freq_calc[key][curr.value] / len(self.document[curr.value])) * idf
                curr = curr.next

    def add_skip_connections(self):
        """ For each postings list in the index, add skip pointers.
            To be implemented."""
        for key, vals in self.inverted_index.items():
            vals.add_skip_connections()
