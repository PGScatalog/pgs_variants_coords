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