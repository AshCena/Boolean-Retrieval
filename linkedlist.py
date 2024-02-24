import math


class Node:

    def __init__(self, value=None, next=None, skip_pointer=None):
        """ Class to define the structure of each node in a linked list (postings list).
            Value: document id, Next: Pointer to the next node
            Add more parameters if needed.
            Hint: You may want to define skip pointers & appropriate score calculation here"""
        self.value = value
        self.tf = 0
        self.next = next
        self.skip_pointer = skip_pointer


class LinkedList:
    """ Class to define a linked list (postings list). Each element in the linked list is of the type 'Node'
        Each term in the inverted index has an associated linked list object.
        Feel free to add additional functions to this class."""

    def __init__(self):
        self.start_node = None
        self.end_node = None
        self.length, self.n_skips, self.idf = 0, 0, 0.0
        self.skip_length = None

    def insert_insertion_sort(self, val):
        if self.start_node is None:
            self.start_node = Node(int(val))
            self.end_node = self.start_node
        else:
            curr = self.start_node

            if curr.value > int(val):
                dummy = Node(int(val))
                dummy.next = self.start_node
                self.start_node = dummy
                self.length += 1
                return

            while curr.next and int(val) > curr.next.value:
                curr = curr.next
            if curr.next:
                if curr.next.value == int(val):
                    return
            temp = curr.next
            curr.next = Node(val)
            curr = curr.next
            curr.next = temp
            if temp is None:
                self.end_node = curr
        self.length += 1
        self.idf = 5000 / self.length
        self.n_skips = math.floor(math.sqrt(self.length))
        if self.n_skips * self.n_skips == self.length:
            self.n_skips = self.n_skips - 1
        self.skip_length = int(round(math.sqrt(self.length), 0))

    def display_linked_list(self):
        curr = self.start_node
        while curr is not None:
            print(curr.value, ' / ', curr.tf, end='--->')
            curr = curr.next

    def display_skip_list(self):
        curr = self.start_node
        k = 0
        while curr is not None and k <= self.n_skips:
            print(curr.value, end='--skip-->')
            curr = curr.skip_pointer
            k += 1

    def traverse_list(self):
        traversal = []
        if self.start_node is None:
            return
        else:
            """ Write logic to traverse the linked list.
                To be implemented."""
            curr = self.start_node
            while curr is not None:
                traversal.append(curr.value)
                curr = curr.next

            return traversal

    def traverse_skips(self):
        traversal = []
        if self.start_node is None:
            return
        else:
            """ Write logic to traverse the linked list using skip pointers.
                To be implemented."""
            curr = self.start_node
            while curr is not None:
                traversal.append(curr.value)
                curr = curr.skip_pointer

            return traversal

    def add_skip_connections(self):
        skips = 0
        curr_ = self.start_node
        # 2 | 1 <--length   | 1 2 5 9
        if self.n_skips == 1 and self.skip_length == 1:
            return
        while skips <= self.n_skips:
            k = 0
            start = curr_
            while k != self.skip_length and curr_.next:
                curr_ = curr_.next
                k += 1
            if curr_ != start.skip_pointer and k == self.skip_length:
                start.skip_pointer = curr_
            skips += 1
        if curr_ == start.skip_pointer:
            curr_.skip_pointer = None

    def merge_sorted_lists(self, ls, rs):

        dummy = Node(-1)
        curr = dummy

        while ls and rs:
            if ls.tf > rs.tf:
                curr.next = ls
                ls = ls.next
            elif ls.tf == rs.tf:
                if ls.value < rs.value:
                    curr.next = ls
                    ls = ls.next
            else:
                curr.next = rs
                rs = rs.next
            curr = curr.next

        curr.next = ls or rs
        return dummy.next

    def merge_sort_list(self, start_node):
        if not start_node or not start_node.next:
            return start_node

        mid = self.find_middle(start_node)
        mid_next = mid.next
        mid.next = None

        left_ll = self.merge_sort_list(start_node)
        right_ll = self.merge_sort_list(mid_next)

        sorted_list = self.merge_sorted_lists(left_ll, right_ll)
        self.start_node = sorted_list
        return sorted_list

    def find_middle(self, start_node=None):
        slwptr = start_node if start_node else self.start_node
        fstptr = start_node if start_node else self.start_node
        if not fstptr or not fstptr.next:
            return None

        while fstptr.next and fstptr.next.next:
            slwptr = slwptr.next
            fstptr = fstptr.next.next

        return slwptr

    def sort_by_tf_idf(self):
        """ Function to sort nodes of linked list by tf-idf score using merge sort """
        self.start_node = self.merge_sort_list(self.start_node)

    def insert_at_end(self, value):
        """ Write logic to add new elements to the linked list.
            Insert the element at an appropriate position, such that elements to the left are lower than the inserted
            element, and elements to the right are greater than the inserted element.
            To be implemented. """

        if self.start_node is None:
            self.start_node = Node(value)
            self.end_node = Node(value)
        else:
            tail = self.end_node
            tail.next = Node(value)
            self.end_node = tail.next
        self.length += 1
