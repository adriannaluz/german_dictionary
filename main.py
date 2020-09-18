import sqlite3 as sql
import numpy as np



class VocabularyClass:

    def __init__(self, path='verbs.db'):
        self.conn = sql.connect(path)
        self.cur = self.conn.cursor()

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
        for i in range(3):
        # while True:
            word, p = self.get_word(tablename)
            conjugation = self.get_conjugation(word)
            idx = np.random.choice(6)
            solution = input("\nConjugate %s (%s): \t" % (word, self.get_col_names(tablename)[2:][idx]))
            success = solution == conjugation[idx]
            new_prob = 0.5 * p if success else 2 * p
            self.update_prob(tablename, word, new_prob)
            if success == 1:
                print("That was correct")
            else:
                print("The right conjugation is %s" % conjugation[idx])

    def close(self):
        self.cur.close()
        self.conn.close()

if __name__ == '__main__':
    voc = VocabularyClass()
    """print("get_table_names", voc.get_table_names())
    print("get_number_rows", voc.get_number_rows("conjugation"))
    print("get_col_names", voc.get_col_names("conjugation"))
    print("get_col", voc.get_col("conjugation", "Infinitive_form"))
    print("get_row", voc.get_row("conjugation", word="haben"))
    print("get_conjugation", voc.get_conjugation("sein"))
    print("get_probabilities", voc.get_probabilities())
    print("Word to conjugate", voc.get_word("conjugation"))
    print(voc.update_prob())"""
    voc.start("conjugation")
    voc.close()
    """

    rows = cur.fetchall()
    num_rows = len(rows)
    # print(num_rows)
    # for row in rows:
    #     print(row)

    # for row in cur.execute('SELECT * FROM conjugation'):
    #     print(row)

    print("From which verb would you like to know the conjugation?")
    conjugations = get_conjugation(cur, str(input()))

    for i, conj in enumerate(conjugations):
        if i == 0:
            continue
        form = col_names[i].split("_")
        print("%s person %s = " %(form[0], form[1]) , conj)


    for i, row in enumerate(rows):
        print(rows[i][0])
        #conjugations = get_conjugation(cur, str(input()))


    # Prepare a list of records to be inserted

    purchases = [(2,'John Paul','john.paul@xyz.com','B'),
                 (3,'Chris Paul','john.paul@xyz.com','A'),
                ]

    # Use executemany() to insert multiple records at a time
    cur.executemany('INSERT INTO consumers VALUES (?,?,?,?)', purchases)
    for row in cur.execute('SELECT * FROM consumers'):
        print(row)
    """
