from collections import defaultdict
import csv, re
import pandas as pd
import numpy as np

ERROR_VALUE = "#ERR"

### DataSet high-level functions ###
def read_data(file_name):
    df = pd.read_csv(file_name,header=None,index_col=False,
        names=list(range(1,get_num_columns(file_name)+1)))
    # Default blank roles to 0
    df = df.fillna(0)
    # Rename columns, assuming a-z. Todo support aa, ab
    # base_value = ord('A')
    # df.columns = [str(chr(base_value + int(index))) for index in df.columns]
    df.columns = [to_excel(index)for index in df.columns]
    # start row index at 1
    df.index += 1

    #TODO: Total hack, forcing every column to be string...
    df = df[list(df.columns)] = df[list(df.columns)].astype(str)

    # df = df.apply(lambda x: x.str.strip().str.lower())
    # df[df.applymap(len) < 1] = np.nan
    df = df.apply(np.vectorize(clean_df_cell))
    return df

def df_diff(generated, expected):
	dfBool = (generated != expected).stack()
	diff = pd.concat([generated.stack()[dfBool],expected.stack()[dfBool]], \
                    axis=1)
	diff.columns=["Generated", "Expected"]
	return diff

def get_num_columns(filename):
    '''
    This function returns ths number of columns for csv files.
    As some csv files might be malformed and missing columns, we need to loop
    through the file to find the row with the highest number of columns.

    ARGS:
        filname: The filename to process

    RETURNS:
        (int): The max of columns counted
    '''
    #TODO: Consider a separte step to clean the CSV file
    maxcount = 0
    with open(filename, "r") as f:
        reader = csv.reader(f)  # create a CSV reader
        for row in reader:  # iterate over the available rows
            # verboseprint("Processing row: {}".format(row))
            maxcount = len(row) if len(row) > maxcount else maxcount
    # verboseprint('Num Columns return: {}'.format(maxcount))
    return maxcount

clean_df_cell = lambda text: text.strip().upper()
digit_regex = r'[A-Za-z]+[0-9]+\b'
isdigit = lambda text:True if type(text) == int else len(text) > 0 and \
            (text.isdigit() or text.lstrip('-').isdigit())
index_regex = r'\b[A-Za-z]+[0-9]+\b'
isindex = lambda text: re.match(index_regex, text) is not None
get_alphanumeric = lambda text:re.findall(index_regex, text)

'''
DICT Mapping Excel Style index to rows and columns.
'''
INDEX_MAP = defaultdict(str)
def isvalid_alphanumeric(key, dataset):
    if not isindex(key):
        return False
    # Might want to set it as False
    tuple = get_row_column_by_alphanumeric(key, True)
    # return tuple[0] <= df.shape[0] and tuple[1] in df.columns
    return tuple[0] < dataset.shape[0] and tuple[1] < dataset.shape[1]

def get_cell_by_alphanumeric(key, dataset):
    index = get_row_column_by_alphanumeric(key)
    # return dataset.loc[index[0], index[1]]
    return dataset[index[0],index[1]]

def set_cell_by_alphanumeric(key, value, dataset):
    index = get_row_column_by_alphanumeric(key)
    # print('{} -> {}'.format(key,index))
    # verboseprint('set {} to {}'.format(index,value))
    # dataset.loc[index[0], index[1]] = str(value)
    dataset[index[0],index[1]] = str(value)

def set_cell_error(key, dataset):
    set_cell_by_alphanumeric(key,ERROR_VALUE, dataset)

def get_row_column_by_alphanumeric(key, add_cache=True):
    '''
    Parse key to column and row, eg B7 - row 6, column 1
    '''
    if key in INDEX_MAP:
        return INDEX_MAP.get(key)

    # TODO: We should change the following to use regex instead
    column = from_excel(''.join(filter(str.isalpha, key))) - 1
    # Row index in DataFrame starts at 0. Values from csv file start 1 based
    row = int(''.join(filter(isdigit, key))) - 1
    cache = (row,column)
    if add_cache:
        # verboseprint('Caching {}->{},{}'.format(key,row,column))
        INDEX_MAP[key] = cache
    return cache
### END HELPERS ###

# Note code recipe is from https://stackoverflow.com/questions/48983939/convert-a-number-to-excel-s-base-26
def divmod_excel(n):
    a, b = divmod(n, 26)
    if b == 0:
        return a - 1, b + 26
    return a, b

import string
def to_excel(num):
    chars = []
    while num > 0:
        num, d = divmod_excel(num)
        chars.append(string.ascii_uppercase[d - 1])
    return ''.join(reversed(chars))

from functools import reduce
def from_excel(chars):
    return reduce(lambda r, x: r * 26 + x + 1, map(string.ascii_uppercase.index, chars), 0)
