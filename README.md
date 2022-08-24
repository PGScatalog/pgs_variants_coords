# pgs_variants_coords

Pipeline written to fetch and store the variants locations on different assembly, in order to be quickly retrieve in the pgs-harmonizer.


## Requirements
- Install [Nextflow](https://www.nextflow.io/)
- Install SQLite
- Install [VCFtools](https://vcftools.github.io/downloads.html)
- Install Python 3.9 or more recent and then run `pip install requirements.txt`
- Download variants VCF files, e.g. https://ftp.ensembl.org/pub/current_variation/vcf/homo_sapiens/homo_sapiens-chr##.vcf.gz (and their indexes - .vcf.gz.csi)

If you start your SQLite knowledge base (KB) from scratch, please run the following command, e.g.:
```
sqlite3 variant_locations_37.db < knowledge_base_schema.sql
sqlite3 variant_locations_38.db < knowledge_base_schema.sql
```
Of course, you can name and place the SQLite knowledge base wherever you prefer.
As the SQLite knowledge base can become quite big, we found that it is more convinient to have a distinct KB per genome build.

## Running pipeline

### Nextflow pipeline configuration (nextflow.config)
```
root_dir = <path to the working directory (other than Nextflow's)>

params {
    pgs_num_from = <PGS ID start number, e.g. '20' for PGS000020>
    pgs_num_to = <PGS ID end number, e.g. '140' for PGS000140>
    genomebuild = <target genomebuild, e.g. '38'>
    pgs_ids_file = <name of the locally generated PGS IDs list file, e.g. "pgs_ids.txt">
    rest_api_url = <URL to the REST API server>
    vars_list_file_path = <path to the variants list file name, e.g. "$root_dir/vars_list.txt">
    var_files_path = <wildcard file name to store the variant coordinates on each VCF file (i.e. chromosome), e.g. "$root_dir/vars_files/vars_chr*.txt">
    merged_var_file_path = <file to merge the content of all the var_files_path, e.g. "$root_dir/vars_files/merged_var_file.txt">
    no_coord_var_file_path = <path to the file listing the variants missing in the VCF files that will be searched via the Ensembl REST API, e.g. "$root_dir/vars_files/no_coord_var_file.txt">
    missing_var_file_path = <path to the file listing the variants missing in the VCF files and the Ensembl REST API, e.g. "$root_dir/vars_files/vars_with_missing_info.txt">
    var_file_path_ensembl = <path to the file containing all the variant data fetched via the Ensembl REST API, e.g. "$root_dir/vars_list_ensembl.txt">
    sqlite_file_path = <path to the SQLite database>
    loc_pipeline = <path to the 'scoring_files_pipeline' directory>
    loc_score_dir = <path to the directory where the scoring files are stored, e.g. '${params.work_dir}/scorefiles/'>
    loc_vcftools = <path to the vcftools bin file, e.g. "..../bin/vcftools">
    loc_vcfs = <path to the 'Ensembl VCF' directory>
    loc_filtered_vcfs = <path to the directory to store the filtered VCF files>
    loc_variants_files = <path to the directory to store the var_files, e.g. "$root_dir/vars_files">
    vcf_file_prefix = <file name prefix used on each VCF files, e.g. "homo_sapiens-chr">'
}
```

If it runs on LSF, here is an example about what to add to nextflow.config:
```
process {
    queue = 'short'
    executor = 'lsf'
    withLabel: medium_mem {
        memory = '2 GB'
    }
    withLabel: retry_increasing_mem {
        errorStrategy = 'retry'
        memory = {1.GB * task.attempt}
        maxRetries = { task.exitStatus in [130,140] ? 6 : 2 }
    }
}
```

### Run Nextflow pipeline

```
nextflow pipeline_dsl2.nf -c nextflow_37.config
```