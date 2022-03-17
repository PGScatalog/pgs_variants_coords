process update_variant_kb {
  input:
    val data_var_file
    val sqlite_file
  output:
    val data_var_file
  script:
  """
  python $params.loc_pipeline/bin/update_variant_location_kb.py --merged_var_file ${data_var_file} --sqlite_file ${sqlite_file}
  """
}