#!/usr/bin/env nextflow

nextflow.enable.dsl=2

include { get_variants_list as GET_VARIANTS_LIST } from './nf_modules/variants_list'
include { prepare_vcf_files as PREPARE_VCF_FILES } from './nf_modules/vcf_files'
include { var2location_vcf as VAR2LOC_VCF } from './nf_modules/var2loc_vcf'
include { merge_var2location_vcf as MERGE_VAR2LOC_VCF } from './nf_modules/merge_var2loc_vcf'
include { compare_vars_lists as COMPARE_VARS_LIST } from './nf_modules/compare_vars'
include { var2location_ensembl as VAR2LOC_ENSEMBL } from './nf_modules/var2loc_ensembl'
include { post_processing as POST_PROCESSING } from './nf_modules/post_process'
include { update_variant_kb as UPDATE_VARIANTS_KB_1 } from './nf_modules/variants_kb'
include { update_variant_kb as UPDATE_VARIANTS_KB_2 } from './nf_modules/variants_kb'


workflow {
  // Channels
  pgs_ids_list = channel.value(params.pgs)
  chromosomes = channel.of(1..22, 'X', 'Y', 'MT')

  // Prepare variants list and their locations
  GET_VARIANTS_LIST(pgs_ids_list)

  // Prepare filtered VCF files
  PREPARE_VCF_FILES(chromosomes, GET_VARIANTS_LIST.out)

  // Extract data from VCF files
  VAR2LOC_VCF(PREPARE_VCF_FILES.out.chr, PREPARE_VCF_FILES.out.filtered_vcf_file)
  MERGE_VAR2LOC_VCF(VAR2LOC_VCF.out.toList())

  // Add new variants to KB
  UPDATE_VARIANTS_KB_1(MERGE_VAR2LOC_VCF.out.merged_file, params.sqlite_file_path)

  // Look at missing variants
  COMPARE_VARS_LIST(UPDATE_VARIANTS_KB_1.out)
  VAR2LOC_ENSEMBL(COMPARE_VARS_LIST.out, params.sqlite_file_path)

  // Add new variants to KB
  UPDATE_VARIANTS_KB_2(VAR2LOC_ENSEMBL.out, params.sqlite_file_path)

  // KB post-processing
  POST_PROCESSING(UPDATE_VARIANTS_KB_2.out,params.sqlite_file_path)
}