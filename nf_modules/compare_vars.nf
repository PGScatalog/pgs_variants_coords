process compare_vars_lists {
  input:
    val merged_var_file
  output:
    val params.no_coord_var_file_path
  script:
  """
  python $params.loc_pipeline/bin/compare_vars_lists.py --merged_var_file ${merged_var_file} --all_var_file ${params.vars_list_file_path} --output_file ${params.no_coord_var_file_path}
  """
}