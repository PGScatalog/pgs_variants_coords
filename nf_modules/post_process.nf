process post_processing {
input:
    val ensembl_var_file
    val sqlite_file
  script:
  """
  python $params.loc_pipeline/bin/post_processing.py --sqlite_file ${sqlite_file}
  """
}