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