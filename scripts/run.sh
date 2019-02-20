#!/bin/bash
python3 main.py -i datafiles/input.csv -t datafiles/validate_output.csv
python3 main.py -i datafiles/input_cycle.csv -t datafiles/validate_cycle.csv
python3 main.py -i datafiles/input_basic.csv
python3 main.py -i datafiles/input_invalid_strings.csv
python3 main.py -i datafiles/input_out_of_bounds.csv
python3 main.py -i datafiles/input_missing_columns.csv
