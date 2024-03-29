import os
import sqlite3
import argparse
import pandas as pd
import gzip
from variants_coords_tools import change_file_write_acces


def read_scorefile(loc_scorefile):
    '''Loads PGS Catalog Scoring file and parses the header into a dictionary'''
    if loc_scorefile.endswith('.gz'):
        f = gzip.open(loc_scorefile,'rt')
    else:
        f = open(loc_scorefile, 'rt')

    df_scoring = pd.read_table(loc_scorefile, float_precision='round_trip', comment='#',
                               dtype = {'chr_position' : 'object',
                                        'chr_name' : 'object',
                                        'hm_chr': 'object',
                                        'hm_pos': 'object'})

    # Make sure certain columns maintain specific datatypes
    if 'reference_allele' in df_scoring.columns:
        df_scoring = df_scoring.rename(columns={"reference_allele": "other_allele"})

    return df_scoring


def clean_rsIDs(raw_rslist):
    '''
    Takes a list of values, removes anything that doesn't look like an rsID and splits any variants that
    are haplotypes, combinations, or interactions
    '''
    cln_rslist = set()
    for x in raw_rslist:
        if type(x) is str and x.startswith('rs'):
            if '_x_' in x:
                x = [y.strip() for y in x.split('_x_')]
            elif ';' in x:
                x = [y.strip() for y in x.split(';')]
            elif ',' in x:
                x = [y.strip() for y in x.split(',')]
            else:
                cln_rslist.add(x)

            if type(x) == list:
                for i in x:
                    if i.startswith('rs'):
                        cln_rslist.add(i)
    return(list(cln_rslist))


def get_variants_with_coords(sqlite_file):
    '''
    Check if the variant ID is already present in the Knowledge Base
    '''
    sqlite_connection = sqlite3.connect(sqlite_file)
    sqlite_cursor = sqlite_connection.cursor()
    rsIDs_list = set()
    for variant in sqlite_cursor.execute('SELECT varname FROM variant'):
       rsIDs_list.add(variant[0])
    sqlite_cursor.close()
    sqlite_connection.close()
    return rsIDs_list


################################################################################

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--scores_ids", help='List of scores IDs', required=True, metavar='PGS_IDS')
    argparser.add_argument("--scores_dir", help='Directory hosting the scoring files', required=True, metavar='PGS_DIR')
    argparser.add_argument("--var_file", help='Path to the variants output file', required=True, metavar='VAR_FILE')
    argparser.add_argument("--sqlite_file", help='Path to the SQLlite file containing the variants with coordinates already assigned', required=True, metavar='SQLITE_FILE')

    args = argparser.parse_args()

    scores_dir = args.scores_dir
    var_file = args.var_file
    sqlite_file = args.sqlite_file

    # Check if the Scoring file directory exists
    if not os.path.isdir(scores_dir):
        print("Directory '"+scores_dir+"' can't be found")
        exit(1)

    # Check if the SQLite file exists
    if not os.path.isfile(sqlite_file):
        print("File '"+sqlite_file+"' can't be found")
        exit(1)

    existing_rsIDs_with_coords = get_variants_with_coords(sqlite_file)

    var_list = set()

    # Prepare the list of Score IDs
    scores_ids_list = args.scores_ids
    for char in ('[',']',' '):
        scores_ids_list = scores_ids_list.replace(char,'')

    for score_id in scores_ids_list.split(','):
        # Scoring file
        scorefile = scores_dir+'/'+score_id+'.txt.gz'
         # Check if the Scoring file exists
        if not os.path.isfile(scorefile):
            print("File '"+scorefile+"' can't be found")
            exit(1)
        
        # Extract rsID from Scoring file
        df_scoring = read_scorefile(scorefile)
        if 'rsID' in df_scoring:
            rsIDs = clean_rsIDs(list(df_scoring['rsID']))

            for rsID in rsIDs:
                if not rsID in var_list  and not rsID in existing_rsIDs_with_coords:
                    var_list.add(rsID)
        else:
            print(f'- {score_id}: missing rsID for {df_scoring}')
    
    print(f'Variants: {len(var_list)}')

    # Create "variants" directory if it doesn't exist
    var_dir = os.path.dirname(var_file)
    if not os.path.isdir(var_dir):
        os.makedirs(var_dir)

    # Print the list of variants in a file
    file_out = open(var_file, 'w')
    for var_id in var_list:
        file_out.write(f'{var_id}\n')
    file_out.close()
    change_file_write_acces(var_file)


if __name__ == '__main__':
    main()