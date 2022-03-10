import os
import argparse
import sqlite3
import requests
import time


rest_api = {
    '37': 'https://grch37.rest.ensembl.org/variation/homo_sapiens',
    '38': 'https://rest.ensembl.org/variation/homo_sapiens'
}
vars_per_call = 20
max_requests = 100
chromosomes_list = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','X','Y','MT']
source_rest_api = '1' # boolean value


def get_mappings(variant_json,varname,var_current_name):
    '''
    Method to retrieve and filter mapping data
    > Parameters:
        - variant_json: JSON output from the REST API call
        - varname: Variant ID queried
        - var_current_name: Current variant ID in dbSNP
    > Return type: list (list of tuples)
    '''
    mappings = []
    if 'mappings' in variant_json:
        if len(variant_json['mappings']) != 0:
            tmp_mappings = []
            has_real_chr = 0
            has_patches = 0
            for location in variant_json['mappings']:
                chr = str(location['seq_region_name'])
                if chr in chromosomes_list:
                    has_real_chr = 1
                else:
                    has_patches = 1
                var_mapping = (
                    varname,
                    var_current_name,
                    location['allele_string'],
                    chr,
                    str(location['start']),
                    str(location['end']),
                    source_rest_api
                )
                tmp_mappings.append(var_mapping)

            # Select the coordinates, only selecting real chromosomes if possible
            if has_real_chr and has_patches and len(tmp_mappings) > 1:
                for tmp_mapping in tmp_mappings:
                    mapping_chr = tmp_mapping[3]
                    if mapping_chr in chromosomes_list:
                        mappings.append(tmp_mapping)
            else:
                mappings = tmp_mappings
    return mappings


def get_variant_info(ids,genebuild):
    '''
    Method to perform REST API calls to the Ensembl REST API
    > Parameters:
        - ids: list of variant IDs (rsID for instance)
    > Return type: string (the current name of the variant)
    '''
    variants_data = {}
    try:
        data_ids = '","'.join(ids)
        response = requests.post(rest_api[genebuild], headers={ "Content-Type" : "application/json"}, data='{ "ids":["'+data_ids+'"]}')
        response_json = response.json()
        response_json_ids = response_json.keys()
        variants_found = []
        for id in ids:
            if id in response_json_ids:
                variants_found.append(id)
                variant_json = response_json[id]
                if 'name' in variant_json:
                    var_current_name = variant_json['name']
                    mappings = get_mappings(variant_json,id,var_current_name)
                    if mappings and len(mappings) > 0:
                        variants_data[id] = mappings
    
        # Try to retrieve variants where the ID is now a synonym of a "current" variant
        if len(variants_found) != len(ids):
            missing_variants = list(set(ids) - set(variants_found))
            # For each missing variant ID
            for var in missing_variants:
                # Loop over the list of (current) variant IDs
                for current_id in response_json_ids:
                    variant_json = response_json[current_id]
                    # Check if the response contains the required data
                    if 'name' in variant_json:
                        var_current_name = variant_json['name']
                        if var in variant_json['synonyms'] and len(variant_json['mappings']) != 0:
                            var_current_name = variant_json['name']
                            mappings = get_mappings(variant_json,var,var_current_name)
                            if mappings and len(mappings) > 0:
                                variants_data[var] = mappings
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(f"Error: cant't retrieve the variant information via the Ensembl REST API: {e}")
    return variants_data


################################################################################

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--var_file", help='Path to the file containing the list of variant identifiers', required=True, metavar='VAR_FILE')
    argparser.add_argument("--var_info_file", help='Path to the output file containing the variants information', required=True, metavar='VAR_INFO_FILE')
    argparser.add_argument("--sqlite_file", help='Path to the SQLlite file containing the variants with coordinates already assigned', required=True, metavar='SQLITE_FILE')
    argparser.add_argument("--genebuild", help='GRCh genebuild assembly (e.g. 37)', required=True, metavar='GENEBUILD')


    args = argparser.parse_args()

    var_file = args.var_file
    var_info_file = args.var_info_file
    sqlite_file = args.sqlite_file
    genebuild = str(args.genebuild)

    # Check if variants file with the remaining list of variant identifiers exists
    if not os.path.isfile(var_file):
        print("File '"+var_file+"' can't be found")
        exit(1)

    var_info_list = set()
    missing_var_list = set()
    vars_list = []
    count_requests = 0
    # Read and parse the file containing list of variant identifiers
    with open(var_file, 'r') as f:
        for line in f:
            data = line.strip().split('\t')
            varname = data[0]
            vars_list.append(varname)
            if len(vars_list) == vars_per_call:
                vars_info = get_variant_info(vars_list,genebuild)
                vars_info_keys = vars_info.keys()

                # Pause the script
                count_requests += 1
                if count_requests == max_requests:
                    count_requests = 0
                    time.sleep(2)

                for var in vars_list:
                    if var in vars_info_keys:
                        for var_coords in vars_info[var]:
                            var_info_list.add(var_coords)
                    else:
                        missing_var_list.add(var)
                vars_list = []
    if len(vars_list):
        vars_info = get_variant_info(vars_list,genebuild)
        vars_info_keys = vars_info.keys()
        for var in vars_list:
            if var in vars_info_keys:
                for var_coords in vars_info[var]:
                    var_info_list.add(var_coords)
            else:
                missing_var_list.add(var)
        vars_list = []


    # Write found variant info into the text file
    output_var_file = open(var_info_file, 'w')
    for var_info in var_info_list:
        line = '\t'.join(var_info)
        output_var_file.write(f"{line}\n")
    output_var_file.close()

    # Write missing variants into an other text file
    sqlite_connection = sqlite3.connect(sqlite_file)
    sqlite_cursor = sqlite_connection.cursor()
    sql_insert = "INSERT OR IGNORE INTO variant (varname) VALUES ("
    for varname in missing_var_list:
        sqlite_cursor.execute(f"{sql_insert}'{varname}');")
        sqlite_connection.commit()
    sqlite_cursor.close()
    sqlite_connection.close()

if __name__ == '__main__':
    main()