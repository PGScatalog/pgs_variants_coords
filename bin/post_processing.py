import os
import argparse
import sqlite3


class RemoveYDuplicates:
    vars_list = set()
    chr_x = 'X'
    chr_y = 'Y'
    var_col = 'current_varname'
    sqlite_query_sel = f"SELECT DISTINCT {var_col} FROM variant_coords WHERE chr='{chr_x}' AND {var_col} IN (SELECT {var_col} FROM variant_coords WHERE chr='{chr_y}');"
    sqlite_query_del = f"DELETE FROM variant_coords WHERE current_varname=? and chr='{chr_y}';"


    def __init__(self,sqlite_file):
        self.sqlite_file = sqlite_file
        try:
            self.sqlite_connection = sqlite3.connect(self.sqlite_file)
            self.sqlite_cursor = self.sqlite_connection.cursor()
        except sqlite3.Error as e:
            print(f"Failed to connect to the SQLite DB: {e}")


    def get_current_var(self):
        self.sqlite_cursor.execute(self.sqlite_query_sel)
        variants = self.sqlite_cursor.fetchall()
        for data in variants:
            self.vars_list.add(data[0])
        print(f"List of variants with coordinates on both X and Y: {','.join(self.vars_list)}")


    def remove_extra_y_coords(self):
        for var in self.vars_list:
            try:
                self.sqlite_cursor.execute(self.sqlite_query_del, (var,))
                self.sqlite_connection.commit()
            except sqlite3.Error as e:
                print(f"Failed to delete record in sqlite table: {e}")


################################################################################

def main():

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--sqlite_file", help='Path to the SQLlite file containing the variants with coordinates already assigned', required=True, metavar='SQLITE_FILE')

    args = argparser.parse_args()

    sqlite_file = args.sqlite_file

    current_var = RemoveYDuplicates(sqlite_file)
    current_var.get_current_var()
    current_var.remove_extra_y_coords()


if __name__ == '__main__':
    main()