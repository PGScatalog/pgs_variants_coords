process prepare_vcf_files {

  input:
    val chr
    val variants_list_file

  output:
    val "${chr}", emit: chr
    val "${params.loc_filtered_vcfs}/${params.vcf_file_prefix}${chr}.recode.vcf.gz", emit: filtered_vcf_file

  script:
  def filename = "${params.vcf_file_prefix}${chr}"
  def vcf_filename = "${params.loc_filtered_vcfs}/${params.vcf_file_prefix}${chr}.recode.vcf"
  """
  rm -f ${vcf_filename}.*
  $params.loc_vcftools --gzvcf ${params.loc_vcfs}/${filename}.vcf.gz --snps $variants_list_file --recode --recode-INFO TSA --out ${params.loc_filtered_vcfs}/${params.vcf_file_prefix}$chr
  bgzip ${vcf_filename}
  tabix ${vcf_filename}.gz
  chmod g+w ${vcf_filename}.gz
  chmod g+w ${vcf_filename}.gz.tbi
  """
}