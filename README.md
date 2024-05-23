# Amp-scanner
remember to clone **recursively** or init submodules after cloning

# flow
- set up environment with requirements
```shell
# inference
python experiments_tools/scripts_experiments/run_inference.py -i experiments_tools/data -o all_out -s fasta

# convert outputs
python experiments_tools/scripts_experiments/convert_outputs.py -i all_out -s tsv

# analyze
python experiments_tools/scripts_experiments/analyze_task_1_and_2.py -i all_out -o all_out/task_1_2.tsv 
python experiments_tools/scripts_experiments/analyze_task_4.py all_out/experiments_data/data/dbaasp/clustered/paired_MD.tsv all_out/task_4.tsv
```