import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print(f'pp: {project_path}')
run_query_path = os.path.join(
    project_path, 'src/smallquery/functions/run_query')
sys.path.append(run_query_path)
