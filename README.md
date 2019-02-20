# postfix_processor

This project processes cvs file and evaluate each cell's with a postfix processor.

## Dependencies
1. Python Version - Python 3.6.5 :: Anaconda, Inc.
2. The required depdencies are stored in requirements.txt. Download them with pip install -r requirements.txt

## Run the code:
You can run the following command:
```
 python3 main.py -i inputfilename.csv -t validatinfilename.csv
```

- ***-i*** is for the input filename. If none is entered, we default to datafiles/input.csv
- ***-t*** (optional)is for the validation filename. If none is entered and not custom inputfile is provided, we default to datafiles/validate_output.csv

For more examples, you can look at ***scripts/run.sh***. You can run that file by typing in bash run.sh in your terminal.

# Design
The data is processed through several steps. In the future, we can make a pipeline out of this. The steps are:
1. Read the data from the disk into memory as Dataframe. Clean up as necessary.
2. Build a graph based on the newly created Dataframe. This graph represents the relationships between cells. For example, if the A2 cell contains B1 D2 +, the graph would create B1->A2 and D2->A2 edges.
3. Run topological sort on the graph. This will create a list of cells sorted in the order to be processed. For our previous example, B1 and D2 will be processed before A2.
4. Evaluate cells in the order prescribed by topological sort.
5. Mark cells that were in in circular dependencies as errors.
6. If validatin file exists, compare results with validation files.
7. Save the result into datafiles/<inputfile name>.result
  
# File Structure
1. main.py - the backbone of the project. This is where most logic resides. 
2. datahelper.py - a file with helper methods.
3. scripts/run.sh - bash file that runs various input files in the scripts folder.
4. datafiles - folder that contains input and validation files. Output files are saved in this folder.
5. datafiles/data_generator.py - a helpful tool that allows me to generate input files.
6. requirements.txt - A list of required dependecies generated using pigar.
7. test.py - file for future unit tests!

# Considerations
1. Using Pandas DataFrame because I like their functionalities in dealing with messsy and missing data.
2. Using Numpy for performance reasons.
3. Correctness over performance was my approach. I would spend more time improving speed and reduce memory consumption if I could.
4. Didn't start with TDD because I was only planning to spend 2-3 hours on this!

# Known shortcomings
1. No Unit Tests :( -- Will add more I swear!
2. Data Files must be able to load into memory in full
3. Processing takes longer than I would like. For example, a file with 260,000 cells (100,000 rows x 26) currently takes about 85 secs. I have identified areas for improvement, but that's for another time.
4. I would love to use generators in some cases to reduce memory footprint and improve speed.
