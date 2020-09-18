import sqlite3 as sql
import numpy as np


class VocabularyBox:

    def __init__(self, path='verbs.db', drop=0.5):
        self.conn = sql.connect(path)
        self.cur = self.conn.cursor()
        self.drop = drop

    def get_number_rows(self, tablename):
        return self.cur.execute("SELECT COUNT(*) FROM %s" % tablename).fetchone()[0]

    def get_table_names(self):
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return self.cur.fetchall()

    def get_col_names(self, tablename):
        """ Get column names of a table """
        reader = self.cur.execute("SELECT * FROM {}".format(tablename))
        return [x[0] for x in reader.description]

    def get_col(self, tablename, col):
        """ Get column of a table """
        self.cur.execute("SELECT %s FROM %s" % (col, tablename))
        return np.squeeze(self.cur.fetchall())

    def get_row(self, tablename, word):
        """ Get row of a table """
        colname = self.cur.execute("SELECT * FROM {}".format(tablename)).description[0][0]
        self.cur.execute("SELECT * FROM %s WHERE %s = '%s'" % (tablename, colname, word))
        return self.cur.fetchall()

    def get_conjugation(self, inf_verb):
        """ Get the conjugation from the given inf_verb """
        conjucations = self.get_row("conjugation", word=inf_verb)
        assert conjucations is not None, "The verb is not in the database. Remember to give the infinitive form of the verb."
        return np.squeeze(conjucations)[2:]

    def get_probabilities(self):
        return self.get_col("conjugation", "probabilities")

    def get_word(self, tablename):
        p = self.get_probabilities()
        idx = np.random.choice(self.get_number_rows(tablename), p=p/p.sum())
        colname = self.cur.execute("SELECT * FROM {}".format(tablename)).description[0][0]
        return self.get_col(tablename, colname)[idx], p[idx]

    def update_prob(self, tablename, word, new_prob):
        colname = self.cur.execute("SELECT * FROM {}".format(tablename)).description[0][0]
        self.cur.execute("UPDATE %s SET %s = %s WHERE %s = '%s'" % (tablename, "probabilities", new_prob, colname, word))
        self.conn.commit()

    def start(self, tablename):

        idx = 0
        while True:
            word, p = self.get_word(tablename)
            conjugation = self.get_conjugation(word)
            conj_idx = np.random.choice(6)
            solution = input("\nConjugate %s (%s): \t" % (word, self.get_col_names(tablename)[2:][conj_idx]))
            if solution.lower() == "exit":
                return
            success = solution == conjugation[conj_idx]
            new_prob = self.drop * p if success else 1. / self.drop * p
            self.update_prob(tablename, word, new_prob)
            if success == 1:
                print("That was correct")
            else:
                print("The right conjugation is %s" % conjugation[conj_idx])
            idx += 1
            if idx % 10 == 0:
                inp = input("Want to continue? [Y/n]")
                if inp.lower() in ["n", "no"]:
                    return

    def close(self):
        self.cur.close()
        self.conn.close()

if __name__ == '__main__':

    voc = VocabularyBox()
    voc.start("conjugation")
    """
    print("get_table_names", voc.get_table_names())
    print("get_number_rows", voc.get_number_rows("conjugation"))
    print("get_col_names", voc.get_col_names("conjugation"))
    print("get_col", voc.get_col("conjugation", "Infinitive_form"))
    print("get_row", voc.get_row("conjugation", word="haben"))
    print("get_conjugation", voc.get_conjugation("sein"))
    print("get_probabilities", voc.get_probabilities())
    print("Word to conjugate", voc.get_word("conjugation"))
    print(voc.update_prob())
    """
    voc.close()
