import os
import argparse
from variants_coords_tools import change_file_write_acces


################################################################################

def main():

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--merged_var_file", help='Path to the file containing the variants with coordinates', required=True, metavar='MERGED_VAR_FILE')
    argparser.add_argument("--all_var_file", help='Path to the variants file (listing the variants from the different Scoring files', required=True, metavar='VAR_FILE')
    argparser.add_argument("--output_file", help='Path to the output file containing the list of variants without coordinates', required=True, metavar='NO_COORD_VAR_FILE')


    args = argparser.parse_args()

    merged_var_file = args.merged_var_file
    all_var_file = args.all_var_file
    no_coord_var_file = args.output_file

    # Check if variants file with coordinates exists
    if not os.path.isfile(merged_var_file):
        print("File '"+merged_var_file+"' can't be found")
        exit(1)

    # Check if variants list file exists
    if not os.path.isfile(all_var_file):
        print("File '"+all_var_file+"' can't be found")
        exit(1)

    merged_var_list = set()
    no_coord_var_list = set()

    # Extract the list of variants from the variants file with coordinates
    with open(merged_var_file, 'r') as f:
        for line in f:
            data = line.strip().split('\t')
            merged_var_list.add(data[0])
    
    # Extract the list of variants from the variants list file
    with open(all_var_file, 'r') as f:
        for line in f:
            data = line.strip().split('\t')
            varname = data[0]
            if varname not in merged_var_list:
                no_coord_var_list.add(varname)
    
    print(f'Variants: {len(no_coord_var_list)}')

    # Print the list of variants without coordinates in a file
    file_out = open(no_coord_var_file, 'w')
    for varname in no_coord_var_list:
        file_out.write(f'{varname}\n')
    file_out.close()
    change_file_write_acces(no_coord_var_file)



if __name__ == '__main__':
    main()