import os
import argparse
import sqlite3


#-------------------#
# Class VariantToKb #
#-------------------#
# Import the variant information in the Knowledge Base (KB) 

class VariantToKb:
    columns_var_list = ['varname','current_varname','source_rest_api']
    columns_var = ','.join(columns_var_list)
    columns_coords_list = ['current_varname','alleles','chr','start','end']
    columns_coords = ','.join(columns_coords_list)
    sqlite_variant_query = f"INSERT OR IGNORE INTO variant ({columns_var}) VALUES (?, ?, ?);"
    sqlite_variant_coords_query = f"INSERT OR IGNORE INTO variant_coords ({columns_coords}) VALUES (?, ?, ?, ?, ?);"
    max_insert = 250

    def __init__(self,merged_var_file,sqlite_file):
        '''
        > Variables:
            - merged_var_file: Path to the file containing all the variant information to import
            - sqlite_file: Path to the Knowledge Base file (SQLite)
        '''
        self.var_file = merged_var_file
        self.sqlite_file = sqlite_file
        try:
            self.sqlite_connection = sqlite3.connect(self.sqlite_file)
            self.sqlite_cursor = self.sqlite_connection.cursor()
        except sqlite3.Error as e:
            print(f"Failed to connect to the SQLite DB: {e}")


    def check_variant_in_kb(self,varname):
        '''
        Check if the variant is already in the KB
        > Variable:
            - varname: variant name (i.e. ID)
        > Return: integer - number of occurences found in the KB
        '''
        sql_query = f"SELECT count(varname) FROM variant WHERE varname='{varname}';"
        self.sqlite_cursor.execute(sql_query)
        numberOfRows = self.sqlite_cursor.fetchone()[0]
        return numberOfRows

    def check_variant_coords_in_kb(self,varname,chr,start):
        '''
        Check if the variant is already in the KB
        > Variable:
            - varname: variant name (i.e. ID)
            - chr: chromosome name
            - start: start position
        > Return: integer - number of occurences found in the KB
        '''
        sql_query = f"SELECT count(current_varname) FROM variant_coords WHERE current_varname='{varname}' AND chr='{chr}' AND start={start};"
        self.sqlite_cursor.execute(sql_query)
        numberOfRows = self.sqlite_cursor.fetchone()[0]
        return numberOfRows


    def generate_insert_variant_tuple(self,data):
        '''
        Format the variant information into a tuple
        > Variable:
            - data: variant information for the split line
        > Return: tuple - variant information
        '''
        varname = data[0]
        current_varname = data[1]
        source_rest_api = data[6]
        return (varname, current_varname, source_rest_api)


    def generate_insert_variant_coords_tuple(self,data):
        '''
        Format the variant information into a tuple
        > Variable:
            - data: variant information for the split line
        > Return: tuple - variant coords information
        '''
        current_varname = data[1]
        alleles = data[2]
        chr = data[3]
        start = data[4]
        end = data[5]
        return (current_varname, alleles, chr, start, end)


    def add_variants_to_kb(self, data_list):
        '''
        Execute the SQL query to import the variant information into the KB
        > Variable:
            - data_list: list of tuples. Each tuple contains the information of a variant.
        '''
        try:
            self.sqlite_cursor.executemany(self.sqlite_variant_query, data_list)
            self.sqlite_connection.commit()
        except sqlite3.Error as e:
            print(f"Failed to insert multiple records into sqlite table: {e}")
    

    def add_variant_coords_to_kb(self, data_list):
        '''
        Execute the SQL query to import the variant information into the KB
        > Variable:
            - data_list: list of tuples. Each tuple contains the information of a variant.
        '''
        try:
            self.sqlite_cursor.executemany(self.sqlite_variant_coords_query, data_list)
            self.sqlite_connection.commit()
        except sqlite3.Error as e:
            print(f"Failed to insert multiple records into sqlite table: {e}")


    def parse_merged_file(self):
        '''
        Read the variants file and parse each line to extract its information
        '''
        count_addition = 0
        total_variants = set()
        variant_rows_list = []
        coords_rows_list = []
        # Read variants data file
        with open(self.var_file, 'r') as f:
            for line in f:
                data = line.strip().split('\t')
                varname = data[0]
                current_varname = data[1]
                chr = data[3]
                start = data[4]

                total_variants.add(varname)

                var_in_kb = self.check_variant_in_kb(varname)
                # New variant
                if var_in_kb == 0:
                    var_row = self.generate_insert_variant_tuple(data)
                    variant_rows_list.append(var_row)

                # Check coordinates
                coords_in_kb = self.check_variant_coords_in_kb(current_varname,chr,start)
                # Add new coordinates
                if coords_in_kb == 0:
                    coords_row = self.generate_insert_variant_coords_tuple(data)
                    coords_rows_list.append(coords_row)

                # Insert variant and coordinates information into the KB
                if len(variant_rows_list) == self.max_insert:
                    self.add_variants_to_kb(variant_rows_list)
                    count_addition += len(variant_rows_list)
                    variant_rows_list = []
                    self.add_variant_coords_to_kb(coords_rows_list)
                    coords_rows_list = []
        # Insert the remaining variant and coordinates information into the KB
        if len(variant_rows_list):
            self.add_variants_to_kb(variant_rows_list)
            count_addition += len(variant_rows_list)
        if len(coords_rows_list):
            self.add_variant_coords_to_kb(coords_rows_list)
        print(f"> Variants added to the KB: {count_addition}/{len(total_variants)}.")
        self.sqlite_cursor.close()
        self.sqlite_connection.close()


################################################################################

def main():

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--merged_var_file", help='Path to the merged variants information file', required=True, metavar='VAR_FILE')
    argparser.add_argument("--sqlite_file", help='Path to the SQLlite file containing the variants with coordinates already assigned', required=True, metavar='SQLITE_FILE')

    args = argparser.parse_args()

    merged_var_file = args.merged_var_file
    sqlite_file = args.sqlite_file

    # Check if the merged variants information file exists
    if not os.path.isfile(merged_var_file):
        print("File '"+merged_var_file+"' can't be found")
        exit(1)

    # Check if the SQLite file exists
    if not os.path.isfile(sqlite_file):
        print("File '"+sqlite_file+"' can't be found")
        exit(1)

    # Extract the variants information and import it into the KB
    var2kb = VariantToKb(merged_var_file,sqlite_file)
    var2kb.parse_merged_file()


if __name__ == '__main__':
    main()