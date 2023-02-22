process merge_var2location_vcf {
  input:
    path variants_file_chr

  output:
    val "${params.merged_var_file_path}", emit: merged_file

  """
  cat $variants_file_chr > ${params.merged_var_file_path}
  """
}