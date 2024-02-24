'''
@author: Sougata Saha
Institute: University at Buffalo
'''

from tqdm import tqdm
from preprocessor import Preprocessor
from indexer import Indexer
from collections import OrderedDict
from linkedlist import LinkedList, Node
import inspect as inspector
import sys
import argparse
import json
import time
import random
import flask
from flask import Flask
from flask import request
import hashlib

app = Flask(__name__)


class ProjectRunner:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.indexer = Indexer()

    def _merge(self, l1, l2):
        """ Implement the merge algorithm to merge 2 postings list at a time.
        Use appropriate parameters & return types.
        While merging 2 postings list, preserve the maximum tf-idf value of a document.
        To be implemented."""
        i = l1
        j = l2
        if isinstance(l1, LinkedList):
            i =i.start_node
        if isinstance(l2, LinkedList):
            j=j.start_node
        nc = 0
        results = LinkedList()
        results.start_node = Node(-1)
        dummy = results.start_node
        while i is not None and j is not None:
            if i.value == j.value:
                dummy.next = Node(i.value)
                dummy = dummy.next
                dummy.tf = max(i.tf, j.tf)
                i = i.next
                j = j.next
            elif i.value < j.value:
                i = i.next
            else:
                j = j.next
            nc += 1
        results.start_node = results.start_node.next
        return nc, results

    def _mergeSkip(self, l1, l2):
        i = l1
        j = l2
        if isinstance(l1, LinkedList):
            i =i.start_node
        if isinstance(l2, LinkedList):
            j=j.start_node
        nc = 0
        results = LinkedList()
        results.start_node = Node(-1)
        dummy = results.start_node
        while i is not None and j is not None:
            if i.value == j.value:
                dummy.next = Node(i.value)
                dummy = dummy.next
                dummy.tf = max(i.tf, j.tf)
                i = i.next
                j = j.next
            elif i.value < j.value:
                if i.skip_pointer and i.skip_pointer.value < j.value:
                    # nc += 1
                    i = i.skip_pointer
                else:
                    i = i.next
            elif i.value > j.value:
                if j.skip_pointer and j.skip_pointer.value < i.value:
                    # nc += 1
                    j = j.skip_pointer
                else:
                    j = j.next
            nc += 1
        results.start_node = results.start_node.next
        if results.start_node is not None:
            results.add_skip_connections()
        return nc, results

    def _daat_and(self, query_terms, qpl, skip=False):
        pointers = []
        for i in range(0, len(query_terms)):
            curr = qpl[query_terms[i]]
            if curr is None:
                return [], None, 0, 0
            pointers.append(curr.start_node)
        n_c = 0
        res = []
        for i in range(0, len(pointers) - 1):
            if i == 0:
                if not skip:
                    nc, res = self._merge(pointers[0], pointers[1])
                else:
                    nc, res = self._mergeSkip(pointers[0], pointers[1])
            else:
                if not skip:
                    nc, res = self._merge(res, pointers[i + 1])
                else:
                    nc, res = self._mergeSkip(res, pointers[i + 1])
            n_c += nc
        if res:
            k = self.convert_to_list(res, 'next')
        else:
            k=[]
            res = LinkedList()
        return k, res, n_c, len(k)

    def _get_postings(self):
        """ Function to get the postings list of a term from the index.
            Use appropriate parameters & return types.
            To be implemented."""
        raise NotImplementedError

    def _output_formatter(self, op):
        """ This formats the result in the required format.
            Do NOT change."""
        if op is None or len(op) == 0:
            return [], 0
        op_no_score = [int(i) for i in op]
        results_cnt = len(op_no_score)
        return op_no_score, results_cnt

    def run_indexer(self, corpus):
        """ This function reads & indexes the corpus. After creating the inverted index,
            it sorts the index by the terms, add skip pointers, and calculates the tf-idf scores.
            Already implemented, but you can modify the orchestration, as you seem fit."""
        with open(corpus, 'r') as fp:
            for line in tqdm(fp.readlines()):
                doc_id, document = self.preprocessor.get_doc_id(line)
                tokenized_document = self.preprocessor.tokenizer(document)[0].split(' ')
                self.indexer.document[doc_id] = tokenized_document
                self.indexer.generate_inverted_index(doc_id, tokenized_document)
        self.indexer.sort_terms()
        self.indexer.add_skip_connections()
        self.indexer.calculate_tf_idf()
        print('running the cde')
        for key, v in self.indexer.inverted_index.items():
            if key == 'vet':
                print('This is = ', key, end=" ")
                v.display_linked_list()
                print('___ skip length --- ', v.skip_length, '----number of skips --- ', v.n_skips,
                      ' -----length----- ', v.length, '<---')
                v.display_skip_list()
                print('\/')

    def sanity_checker(self, command):
        """ DO NOT MODIFY THIS. THIS IS USED BY THE GRADER. """

        index = self.indexer.get_index()
        kw = random.choice(list(index.keys()))
        return {"index_type": str(type(index)),
                "indexer_type": str(type(self.indexer)),
                "post_mem": str(index[kw]),
                "post_type": str(type(index[kw])),
                "node_mem": str(index[kw].start_node),
                "node_type": str(type(index[kw].start_node)),
                "node_value": str(index[kw].start_node.value),
                "command_result": eval(command) if "." in command else ""}

    def convert_to_list(self, l1, ptrType):
        ls = []
        curr = None
        if isinstance(l1, Node):
            curr = l1
        if isinstance(l1, LinkedList):
            curr = l1.start_node
        while curr:
            ls.append(curr.value)
            if ptrType == 'next':
                curr = curr.next
            if ptrType == 'skip':
                curr = curr.skip_pointer
        if len(ls) == 1 and ptrType == 'skip':
            return []
        return ls

    def get_posting_list(self, query, inverted_index):
        try:
            return inverted_index[query]
        except:
            return None

    def get_posting_listAsList(self, query, posting_list, ptrType):
        try:
            return self.convert_to_list(posting_list[query[0]], ptrType)
        except:
            return []

    def run_queries(self, query_list, random_command='random'):
        """ DO NOT CHANGE THE output_dict definition"""
        output_dict = {'postingsList': {},
                       'postingsListSkip': {},
                       'daatAnd': {},
                       'daatAndSkip': {},
                       'daatAndTfIdf': {},
                       'daatAndSkipTfIdf': {},
                       'sanity': self.sanity_checker(random_command)}

        output_dict_ll = {'postingsList': {}}
        for query in tqdm(query_list):

            """ Run each query against the index. You should do the following for each query:
                    1. Pre-process & tokenize the query.
                    2. For each query token, get the postings list & postings list with skip pointers.
                    3. Get the DAAT AND query results & number of comparisons with & without skip pointers.
                    4. Get the DAAT AND query results & number of comparisons with & without skip pointers, 
                        along with sorting by tf-idf scores."""
            input_term_arr = []  # Tokenized query. To be implemented.
            input_term_arr = self.preprocessor.tokenizer(query.split())[0].split(' ')

            for term in input_term_arr:
                postings, skip_postings = None, None

                """ Implement logic to populate initialize the above variables.
                    The below code formats your result to the required format.
                    To be implemented."""

                output_dict['postingsList'][term] = self.get_posting_listAsList([term], self.indexer.inverted_index,
                                                                                'next')
                output_dict['postingsListSkip'][term] = self.get_posting_listAsList([term],
                                                                                    self.indexer.inverted_index,
                                                                                    'skip')
                output_dict_ll['postingsList'][term] = self.get_posting_list(term, self.indexer.inverted_index)
            

            and_results_no_skip, res1, and_comparisons_no_skip, and_op_num_docs_no_skip = self._daat_and(
                input_term_arr, output_dict_ll['postingsList'])
            and_results_skip, res2, and_comparisons_skip, and_op_num_docs_skip = self._daat_and(
                input_term_arr, output_dict_ll['postingsList'], skip=True)

            """ Implement logic to populate initialize the above variables.
                The below code formats your result to the required format.
                To be implemented."""

            output_dict['daatAnd'][query.strip()] = {}
            output_dict['daatAnd'][query.strip()]['results'] = and_results_no_skip
            output_dict['daatAnd'][query.strip()]['num_docs'] = and_op_num_docs_no_skip
            output_dict['daatAnd'][query.strip()]['num_comparisons'] = and_comparisons_no_skip
            output_dict['daatAnd'][query.strip()] = dict(sorted(output_dict['daatAnd'][query.strip()].items()))
            #
            output_dict['daatAndSkip'][query.strip()] = {}
            output_dict['daatAndSkip'][query.strip()]['results'] = and_results_skip
            output_dict['daatAndSkip'][query.strip()]['num_docs'] = and_op_num_docs_skip
            output_dict['daatAndSkip'][query.strip()]['num_comparisons'] = and_comparisons_skip
            output_dict['daatAndSkip'][query.strip()] = dict(sorted(output_dict['daatAndSkip'][query.strip()].items()))
            if res1 is not None:
                res1.sort_by_tf_idf()
            if res2 is not None:
                res2.sort_by_tf_idf()
            output_dict['daatAndTfIdf'][query.strip()] = {}
            if res1 is not None:
                output_dict['daatAndTfIdf'][query.strip()]['results'] = self.convert_to_list(res1.start_node, 'next')
            else:
                output_dict['daatAndTfIdf'][query.strip()]['results'] = []
            output_dict['daatAndTfIdf'][query.strip()]['num_docs'] = and_op_num_docs_no_skip
            output_dict['daatAndTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_no_skip
            output_dict['daatAndTfIdf'][query.strip()] = dict(sorted(output_dict['daatAndTfIdf'][query.strip()].items()))


            output_dict['daatAndSkipTfIdf'][query.strip()] = {}
            if res2 is not None:
                output_dict['daatAndSkipTfIdf'][query.strip()]['results'] = self.convert_to_list(res2.start_node, 'next')
            else:
                output_dict['daatAndSkipTfIdf'][query.strip()]['results'] = []
            output_dict['daatAndSkipTfIdf'][query.strip()]['num_docs'] = and_op_num_docs_skip
            output_dict['daatAndSkipTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_skip
            output_dict['daatAndSkipTfIdf'][query.strip()] = dict(sorted(output_dict['daatAndSkipTfIdf'][query.strip()].items()))


        output_dict['postingsList'] = dict(sorted(output_dict['postingsList'].items()))
        output_dict['postingsListSkip'] = dict(sorted(output_dict['postingsListSkip'].items()))
        output_dict['daatAnd'] = dict(sorted(output_dict['daatAnd'].items()))
        output_dict['daatAndSkip'] = dict(sorted(output_dict['daatAndSkip'].items()))
        output_dict['daatAndTfIdf'] = dict(sorted(output_dict['daatAndTfIdf'].items()))
        output_dict['daatAndSkipTfIdf'] = dict(sorted(output_dict['daatAndSkipTfIdf'].items()))
        output_dict = dict(sorted(output_dict.items()))

        return output_dict


@app.route("/execute_query", methods=['POST'])
def execute_query():
    """ This function handles the POST request to your endpoint.
        Do NOT change it."""
    start_time = time.time()

    queries = request.json["queries"]

    """ Running the queries against the pre-loaded index. """
    output_dict = runner.run_queries(queries, random_command='random')

    """ Dumping the results to a JSON file. """


    response = {
        "Response": output_dict,
        "time_taken": str(time.time() - start_time)
    }

    with open(output_location, 'w') as fp:
        json.dump(response, fp)

    return flask.jsonify(response)


if __name__ == "__main__":
    """ Driver code for the project, which defines the global variables.
        Do NOT change it."""

    output_location = "project2_output.json"
    # parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # parser.add_argument("--corpus", type=str, help="Corpus File name, with path.")
    # parser.add_argument("--output_location", type=str, help="Output file name.", default=output_location)
    # parser.add_argument("--username", type=str,
    #                     help="Your UB username. It's the part of your UB email id before the @buffalo.edu. "
    #                          "DO NOT pass incorrect value here")
    #
    # argv = parser.parse_args()

    corpus = './data/input_corpus.txt'
    # query_list = './data/queries.txt'
    output_location = output_location
    # username_hash = hashlib.md5(argv.username.encode()).hexdigest()

    """ Initialize the project runner"""
    runner = ProjectRunner()

    """ Index the documents from beforehand. When the API endpoint is hit, queries are run against 
        this pre-loaded in memory index. """
    runner.run_indexer(corpus)
    # runner.run_queries(query_list, random_command='random')

    app.run(host="0.0.0.0", port=9999)
