# # Package developed by Colin Dewey for COMP SCI 576

def read_substitution_matrix(filename):
    """Reads a substitution matrix from a file.

    Args:
        filename: the name of the substitution matrix file
    Returns:
        A substitution matrix represented by a dictionary object indexed by
        character pair tuples. (e.g., ('S', 'A'))
    """
    matrix = dict()
    colnames = None
    with open(filename) as f:
        for line in f:
            if line.startswith("#"): 
                continue
            elif colnames is None: # first line
                colnames = line.split()
            else:
                row = line.split()
                rowname = row[0]
                for colname, value in zip(colnames, row[1:]):
                    matrix[(rowname, colname)] = int(value)
    return matrix

def match_mismatch_matrix(match_score, mismatch_score, alphabet):
    return {(a, b): match_score if a == b else mismatch_score 
            for a in alphabet for b in alphabet}

def submatrix_with_spaces(matrix, space_score):
    """Returns an extended substitution matrix representing a linear gap penalty function."""
    extended_matrix = matrix.copy()
    chars = {a for (a, b) in matrix}
    for a in chars:
        extended_matrix[a, '-'] = space_score
        extended_matrix['-', a] = space_score
    extended_matrix['-', '-'] = 0
    return extended_matrix

def print_matrix(m, width=4):
    """Prints the dict-based matrix m with the specified width for each column."""
    def print_row(fields):
        print("".join(["{:>{width}}".format(field, width=width) for field in fields]))
    labels = sorted({c for pair in m for c in pair})
    print_row([""] + labels)
    for a in labels:
        print_row([a] + [m.get((a, b), "") for b in labels])
