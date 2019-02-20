import argparse
import pandas as pd
import numpy as np
from collections import defaultdict
import datahelper

class Graph:
    '''
        This class is used to represent depdencies between cells. It offers
        topological_sort based on the underlying graphself.
    '''
     # Constructor
    def __init__(self):
        # default dictionary to store graph
        self.graph = defaultdict(set)

    # function to add an edge to graph
    def add_edge(self, u, v):
        '''
        Adds an edge between u and v where u has an edge directed at v.
        Args:
            self: Self pointer.
            u: The Parent
            v: The dependent
        '''
        self.graph[u].add(v)

    def get_edges(self,u):
        return self.graph[u]

    def convert_to_key(self, row_index,column):
        return '{}{}'.format(column,row_index)

    def build_graph(self, dataset):
        '''
        This function builds an internal graph based on the provided dataset.
        Args:
            self: Self pointer.
            dataset: Numpy Matrix of the underlying data.
        '''
        # TODO: Figure out refs_ok
        it = np.nditer(dataset, flags=['multi_index','refs_ok'])
        # TODO: Maybe we can vectorize this?
        while not it.finished:
            current = self.convert_to_key(it.multi_index[0] + 1, \
                                    datahelper.to_excel(it.multi_index[1]+1))
            # print('Key is {}'.format(current))
            _ = self.graph[current]

            for v in [parent for parent in datahelper.get_alphanumeric(str(it[0])) \
                        if datahelper.isvalid_alphanumeric(parent, dataset)]:
                self.add_edge(v,current)
            it.iternext()
        verboseprint(self.graph)

    # TODO: We can change this to a generator function that returns order.
    # To find the cell in cycles, we can find keys in graph but not in order.
    def topological_sort(self):
        seen = set()
        stack = []
        order = []
        cycle = []
        for start,value in self.graph.items():
            q = [start]
            while q:
                v = q.pop()
                if v not in seen:
                    seen.add(v)
                    verboseprint('visiting:{}'.format(v))
                    q.extend(self.graph[v])

                    while stack and v not in self.graph[stack[-1]]:
                        order.append(stack.pop())
                    stack.append(v)
                elif v in stack:
                    verboseprint('Saw duplicate and in current stack'.format(v))
                    cycle.extend(stack)
                    stack.clear()
                    break;

        #The result so is in the order of how we should processing, we might keep it as reversed to process as pop
        return stack + order[::-1], cycle

def update_process_order(process_order, dataset):
    '''
    Update the data in dataset according to the order in process_order
    ARGS:
        process_order: A list that contains the topological order of cells
        dataset: Data represented in Ajacency Matrix
    '''
    for index, v in enumerate(process_order):
        try:
            cell = datahelper.get_cell_by_alphanumeric(v, dataset)
            depedencies = datahelper.get_alphanumeric(cell)
            verboseprint('For {}->{}, replace {}'.format(v, cell, depedencies))

            list_of_words = [w if w not in depedencies else \
                    datahelper.get_cell_by_alphanumeric(w, dataset) for w in cell.split()]
            verboseprint("After replacement: {}".format(list_of_words))
            datahelper.set_cell_by_alphanumeric(v,eval_postfix(list_of_words), dataset)
        except:
            verboseprint('set {} to error'.format(v))
            datahelper.set_cell_error(v, dataset)

def process_cycle(cycle, dataset):
    '''
    Update the data in dataset to @ERROR_VALUE if the cell is one of those
    affected by circular dependency(s)
    ARGS:
        cycle: A list that belongs to any circular depdencies
        dataset: Data represented in Ajacency Matrix
    '''
    if cycle:
        rows, columns = map(list, \
            zip(*[datahelper.get_row_column_by_alphanumeric(v) for v in cycle]))
        dataset[np.array(rows), np.array(columns)] = datahelper.ERROR_VALUE

# def generate_tuples(cycle):
#     for v in cycle:
#          yield datahelper.get_row_column_by_alphanumeric(v)

def eval_postfix(text):
    """ This function evaluates the post fix operations
    Args:
        text (list): List of strings, each representing a word

    Returns:
        String: The return value that is the result of the evaluation

    Raise:
        ValueError: If there's an incorrect character or evaluation fails to
        complete
    """
    if not text:
        return 0
    s = list()
    verboseprint('Eval postfix {}'.format(text))
    for symbol in text:
        result = None
        # print('current symbol is %s' % symbol )
        # TODO: We need to make sure the '-' is in the front, not in the back
        if datahelper.isdigit(symbol):
            s.append(int(symbol))
        elif not len(s) == 0:
            right = s.pop()
            left = s.pop()
            if symbol == "+":
                result = left + right
            elif symbol == "-":
                result = left - right
            elif symbol == "*":
                result = left * right
            elif symbol == "/":
                result = left / right
            else:
                raise ValueError()
                # return ERROR_VALUE
            if result is not None:
                s.append(result)
                # print(s)
        else:
            # return ERROR_VALUE
            raise ValueError()

    if len(s) > 1:
        # return ERROR_VALUE
        raise ValueError()

    return str(s.pop())

def process_files(inputfile, testfile):
    '''
    This function jump starts the process from reading the data from disk to
    validating results.
        ARGS
    '''
    # Step 1: Read data
    df = datahelper.read_data(inputfile)
    verboseprint('Data is read')

    # We'll use numpy arrays for speed reasons
    dataset = df.values

    # Step 2: Build the graph
    g = Graph()
    g.build_graph(dataset)
    print('Graph is built')

    # Step 3: Sort topolotically
    process_order, cycle = g.topological_sort()
    print('Topological sort is done.')
    verboseprint('Process Order')
    verboseprint('Detected Cycle')

    # Step 4: Update the set by process order
    update_process_order(process_order,dataset)
    print('process dataset is complete')

    # Step 5: Mark Errors
    process_cycle(cycle, dataset)
    print('process cycle is complete')

    # Step 6: Run Tests
    if testfile:
        df_validate = datahelper.read_data(testfile)
        print('Result and Test files match: {}'.format(df.equals(df_validate)))
        if not df.equals(df_validate):
            print(datahelper.df_diff(df,df_validate))

    # Step 7: Record results
    resultfile = '{}.result'.format(inputfile)
    df.to_csv(resultfile,header=False, index=False)
    print('Written to: {}'.format(resultfile))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="data input filename")
    parser.add_argument("-t", "--test", help="data validate filename")
    parser.add_argument("-v", "--verbose", help="verbose print", \
                        action="store_true")
    args = parser.parse_args()
    if args.test and not args.input:
        parser.error('The -t/--test file argument requires -i/--input argument')

    inputfile = args.input if args.input else 'datafiles/input.csv'
    # TODO: Could make this more concise?
    if args.input and args.test:
        testfile = args.test
    elif args.input and not args.test:
        testfile = None
    else:
        testfile = 'datafiles/validate_output.csv'
    print('=== Start ===')
    print('Input File: {}, Test File: {}'.format(inputfile, testfile))

    # Print if verbose is set, else do not print.
    verboseprint = print if args.verbose else lambda *a, **k: None

    process_files(inputfile, testfile)
    print('=== End ===')
