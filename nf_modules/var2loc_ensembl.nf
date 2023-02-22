process var2location_ensembl {
  input:
    val var_file_path
    val sqlite_file
  output:
    val params.var_file_path_ensembl
  script:
  """
  python $params.loc_pipeline/bin/var2location_ensembl.py --var_file ${var_file_path} --var_info_file ${params.var_file_path_ensembl} --sqlite_file ${sqlite_file} --genomebuild ${params.genomebuild}
  """
}