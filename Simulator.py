import numpy as np
import itertools
import pandas as pd
import time

#TODO UserVocabulary
class User():
    """
    Containse the list of logical operations for the user, associated with their frequency scores.
    Can generate a text based on this data
    """
    def __init__(self, user_id):
        self.user_id = user_id
        self.session_id = None

        self.logical_operations_scores = dict()

        self.sessions = list()
        self.texts = list()
        self.texts_logical_operations = list()
        self.locations = list()

    def add_logical_operation(self, logical_operation, score):
        """
        :param logical_operation: tuple of letters
        :param score: float number, frequency score for this logical operatoin
        """
        assert type(logical_operation) is tuple
        assert all([type(letter) is str for letter in logical_operation])
        assert type(score) in [int, float]
        self.logical_operations_scores[logical_operation] = score

    def del_logical_operation(self, logical_operation):
        if logical_operation not in self.logical_operations_scores:
            return # maybe throw an exception
        del self.logical_operations_scores[logical_operation]

    def set_session(self, session_id):
        self.session_id = session_id

    def get_probabilities(self):
        """
        :return: a list of frequency probabilities, lineary proportional to the scores
        """
        scores = self.logical_operations_scores.values()
        total_scores= sum(scores)
        probs = [score/total_scores for score in scores]
        assert np.isclose(sum(probs), 1)
        return probs

    def generate_text(self, text_size_logical_operations):
        """
        :param text_size_logical_operations: number of logical operations occurrences in the new text
        :return: a flat sequence of letters, with #text_size occurrences of user's logical operations
        """
        assert self.session_id is not None
        logical_operations = list(self.logical_operations_scores.keys())
        probs = self.get_probabilities()

        num_logical_operations = len(logical_operations)
        text_logical_operations_indices = np.random.choice(a=range(num_logical_operations),
                                                           size=text_size_logical_operations,
                                                           replace=True,
                                                           p = probs)
        text_logical_operations = [logical_operations[i] for i in text_logical_operations_indices]
        text = list(itertools.chain.from_iterable(text_logical_operations))

        self.texts.append(text)
        self.texts_logical_operations.append(text_logical_operations)
        self.sessions.append(self.session_id)
        self.locations.append(self.get_locations(text_logical_operations))

        text_entry = {"user_id" : self.user_id,
                      "session_id" : self.session_id,
                      "text" : self.texts[-1],
                      "size" : len(self.texts[-1]),
                      "locations_basic" : self.locations[-1][0],
                      "locations_full" : self.locations[-1][1]
                      }
        return text_entry

    def get_histogram(self):
        """
        :return: histogram data frame. columns: logical_operation, cnt [occurrences], percentage [occurrences]
        example:
                    logical_operation       cnt         percentage      user_id
        0          (s1, s2)                 71          0.71            user_1
        1          (s3, s4)                 29          0.29            user_1

        """
        import collections
        self.histogram = collections.Counter()
        for text_logical_operations in self.texts_logical_operations:
            cur_hist = collections.Counter(text_logical_operations)
            self.histogram.update(cur_hist)

        df_histogram = pd.DataFrame(list(self.histogram.items()), columns = ["logical_operation", "cnt"])
        df_histogram["percentage"] = df_histogram["cnt"]/df_histogram["cnt"].sum()
        df_histogram["user_id"] = self.user_id

        return df_histogram


    def get_locations(self, text_logical_operations):
        """

        :param text_logical_operations: text as list of tuples. each tuple is a logical operation
        :return: dictionary of logical_operation to (begin,end) indices in the text
        example:

        text_logical_operations = [('a','b'), ('c','d','e'), ('a','b')]

        df_logical_operations_locations will be:
                    logical_operation   begin_index     end_index
            0       (a, b)              0               1
            1       (c, d, e)           2               4
            2       (a, b)              5               6

        df_full_logical_operations_locations will be:
                      logical_operation text        text_index  lo_index
            0         (a, b)            a           0           0
            1         (a, b)            b           1           1
            2         (c, d, e)         c           2           0
            3         (c, d, e)         d           3           1
            4         (c, d, e)         e           4           2
            5         (a, b)            a           5           0
            6         (a, b)            b           6           1

        """
        logical_operations_locations = list()
        full_logical_operations_locations = list()
        total_len = 0
        for logical_operation_occ in text_logical_operations:
            begin_index_in_text = total_len
            size = len(logical_operation_occ)
            end_index_in_text = begin_index_in_text + size - 1 # end_index is inclusive

            logical_operations_locations.append([logical_operation_occ, begin_index_in_text, end_index_in_text])

            lo_full = pd.DataFrame([  [logical_operation_occ] * size,
                                      list(logical_operation_occ),
                            list(range(begin_index_in_text, begin_index_in_text + size)),
                            list(range(size))]).T
            full_logical_operations_locations.append(lo_full)

            total_len += size

        df_logical_operations_locations = pd.DataFrame(logical_operations_locations, columns = ["logical_operation", "begin_index", "end_index"])

        full_logical_operations_locations = pd.concat(full_logical_operations_locations)
        full_logical_operations_locations.columns = ["logical_operation","text", "text_index","lo_index"]
        full_logical_operations_locations.reset_index(inplace=True, drop=True)

        return df_logical_operations_locations, full_logical_operations_locations

class Simulator():
    def __init__(self):
        self.users = dict()
        self.text_entries = list()

        np.random.seed(0)

    def _user_exists(self, user_id):
        return user_id in self.users.keys()

    def add_user(self, user_id):
        assert not self._user_exists(user_id)
        self.users[user_id] = User(user_id=user_id)

    def add_logical_opration_to_user(self, user_id, logical_operation, score):
        assert self._user_exists(user_id)
        user = self.users[user_id]
        user.add_logical_operation(logical_operation, score)

    def del_logical_operation_from_user(self, user_id, logical_operation):
        assert self._user_exists(user_id)
        user = self.users[user_id]
        user.del_logical_operation(logical_operation)

    def generate_text_for_user(self, user_id, text_size_logical_operations):
        assert self._user_exists(user_id)
        user = self.users[user_id]
        text_entry = user.generate_text(text_size_logical_operations)
        self.text_entries.append(text_entry)

    def set_session(self, user_id, session_id):
        assert self._user_exists(user_id)
        user = self.users[user_id]
        user.set_session(session_id)

    def get_text_entries(self):
        return self.text_entries

    def clear(self):
        self.text_entries = list() # users stays

    def get_histogram(self):
        """
        :return: union of all users' historams
        example:
                logical_operation   cnt     percentage  user_id
        0      (s1, s2, s3)         96      0.872727    user_1
        1      (u4, u5, u6)         2       0.018182    user_1
        2      (s4, s5, s6)         12      0.109091    user_1
        0      (s4, s5, s6)         100     1.000000    user_2
        """

        df_histogram = pd.concat([user.get_histogram() for user in self.users.values()])
        df_histogram.sort_values(by=["user_id", "logical_operation"], inplace=True)
        return df_histogram


