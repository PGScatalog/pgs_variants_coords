#!/usr/bin/env nextflow

nextflow.enable.dsl=2

include { update_variant_kb as UPDATE_VARIANTS_KB_1 } from './modules/variants_kb'
include { update_variant_kb as UPDATE_VARIANTS_KB_2 } from './modules/variants_kb'

def list_to_string(data_list) {
  return data_list.join(',')
}


process get_variants_list {
  label 'medium_mem'
  input:
    val pgs_ids

  output:
    val params.vars_list_file_path

  script:
  """
  mkdir -p $params.loc_filtered_vcfs
  mkdir -p $params.loc_variants_files
  python $params.loc_pipeline/bin/variants_list.py \
    --scores_ids $pgs_ids \
    --scores_dir $params.loc_score_dir \
    --var_file $params.vars_list_file_path \
    --sqlite_file $params.sqlite_file_path
  """
}


process prepare_vcf_files {

  input:
    val chr
    val variants_list_file

  output:
    val "${chr}", emit: chr
    val "${params.loc_filtered_vcfs}/${params.vcf_file_prefix}${chr}.recode.vcf.gz", emit: filtered_vcf_file

  script:
  def filename = "${params.vcf_file_prefix}$chr"
  def vcf_filename = "${params.loc_filtered_vcfs}/${params.vcf_file_prefix}${chr}.recode.vcf"
  """
  rm -f ${vcf_filename}.*
  $params.loc_vcftools --gzvcf ${params.loc_vcfs}/${filename}.vcf.gz --snps $variants_list_file --recode --recode-INFO TSA --out ${params.loc_filtered_vcfs}/${params.vcf_file_prefix}$chr
  bgzip ${vcf_filename}
  tabix ${vcf_filename}.gz
  """
}


process var2location_vcf {

  input:
    val chr
    val filtered_vcf_file

  output:
    val "${params.loc_variants_files}/vars_chr${chr}.txt"

  script:
  """
  python $params.loc_pipeline/bin/extract_var_info_from_vcf.py --vcf ${filtered_vcf_file} --output ${params.loc_variants_files}/vars_chr${chr}.txt
  """
}


process merge_var2location_vcf {
  input: 
    path variants_file_chr
  
  output:
    val "${params.merged_var_file_path}", emit: merged_file
  
  """
  cat $variants_file_chr > ${params.merged_var_file_path} 
  """
}


process compare_vars_lists {
  input:
    val merged_var_file
  output:
    val params.no_coord_var_file_path
  script:
  """
  python $params.loc_pipeline/bin/compare_vars_lists.py --merged_var_file ${merged_var_file} --all_var_file ${params.var_file_path} --output_file ${params.no_coord_var_file_path}
  """
}


process var2location_ensembl {
  input:
    val var_file_path
    val sqlite_file
  output:
    val params.var_file_path_ensembl
  script:
  """
  python $params.loc_pipeline/bin/var2location_ensembl.py --var_file ${var_file_path} --var_info_file ${params.var_file_path_ensembl} --sqlite_file ${sqlite_file} --genebuild ${params.genebuild}
  """
}


process post_processing {
  input:
    val ensembl_var_file
    val sqlite_file
  script:
  """
  python $params.loc_pipeline/bin/post_processing.py --sqlite_file ${sqlite_file}
  """
}


workflow {
  // Prepare variants list and their locations
  get_variants_list(list_to_string(params.pgs))
  
  // Prepare filtered VCF files
  chromosomes = channel.of(1..22, 'X', 'Y', 'MT')
  //chromosomes = channel.fromList(params.chromosomes)
  prepare_vcf_files(chromosomes,get_variants_list.out)

  // Extract data from VCF files
  var2location_vcf(prepare_vcf_files.out.chr,prepare_vcf_files.out.filtered_vcf_file)
  merge_var2location_vcf(var2location_vcf.out.toList())

  // Add new variants to KB
  UPDATE_VARIANTS_KB_1(merge_var2location_vcf.out.merged_file,params.sqlite_file_path)
  
  // Look at missing variants
  compare_vars_lists(UPDATE_VARIANTS_KB_1.out)
  var2location_ensembl(compare_vars_lists.out,params.sqlite_file_path)

  // Add new variants to KB
  UPDATE_VARIANTS_KB_2(var2location_ensembl.out,params.sqlite_file_path)

  // KB post-processing
  post_processing(UPDATE_VARIANTS_KB_2.out,params.sqlite_file_path)
}