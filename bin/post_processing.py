import os
import argparse
import sqlite3


class RemoveYDuplicates:
    var2current = {}
    ycoords2remove = {}
    chr_x = 'X'
    chr_y = 'Y'
    columns_coords_list = ['current_varname','chr','start']
    columns_coords = ','.join(columns_coords_list)
    sqlite_query_sel = f"SELECT {columns_coords} FROM variant_coords WHERE chr='{chr_x}' or chr='{chr_y}';"
    sqlite_query_del = f"DELETE FROM variant_coords WHERE current_varname=? and chr='{chr_y}' and start=?;"

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
            current_varname = data[0]
            chr = data[1]
            start = data[2]
            if current_varname in self.var2current.keys():
                self.var2current[current_varname][chr] = start
            else:
                self.var2current[current_varname] = { chr: start }
    

    def filter_current_var(self):
        for var in self.var2current.keys():
            var_coords = self.var2current[var]
            if self.chr_x in var_coords and self.chr_y in var_coords:
                if var_coords[self.chr_x] == var_coords[self.chr_y]:
                    self.ycoords2remove[var] = var_coords[self.chr_y]
        for v in self.ycoords2remove.keys():
            print(f"- {v}: {self.ycoords2remove[v]}")
        print(f"COUNT: {len(self.ycoords2remove.keys())}")


    def remove_y_coords(self):
         for var in self.ycoords2remove.keys():
            start = self.ycoords2remove[var]
            try:
                self.sqlite_cursor.execute(self.sqlite_query_del, (var,start))
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
    current_var.filter_current_var()
    #current_var.remove_y_coords()


if __name__ == '__main__':
    main()