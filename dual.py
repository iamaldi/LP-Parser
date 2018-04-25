import re
import numpy as np

'''
This code's main functionality is to convert a given primal linear problem
into a dual and save it on a text file.
'''

# Compiled regular expressions

min_max_regex = re.compile('^((min\ *)|(max\ *))(\[(\ *\'(-*\+*)\d+\'\ *\,*\ *)*\]){1}\ *(\[(\ *\'x\d+\'\ *\,*\ *)*\]){1}')
extract_constants_regex = re.compile('((\+*\-*)\d)+')
subject_to_regex = re.compile('(\[((\[((\'(\+*\-*)\d+\')|(\,)\ *)*\ *\])|(\,)\ *)*\])')
extract_str_a_regex = re.compile('((\[((\'\ *(\+*\-*)\d+\ *\')|(\,)\ *)*\ *\])\ *)')
extract_str_eqin_regex = re.compile('(\[((\[(((\+*\-*)\d+)|(\,)\ *)*\ *\])|(\,)\ *)*\])')

# Open a file with read permissions given a filename
def open_textfile(filename):
    return open(filename, 'r')

# Identify the optimization type of the primal LP
def identify_primal(objective_function):
    if str(min_max_regex.match(objective_function)[1]).strip() == 'min':
        return 'max'
    elif str(min_max_regex.match(objective_function)[1]).strip() == 'max':
        return 'min'
    else:
        raise Exception('An error was encountered while parsing the objective function of the primal linear problem.')

# Extract string representation of vector 'c'
def extract_str_c(objective_function):
    return min_max_regex.match(objective_function)[4]

# Extract string representation of matrix 'A'
def extract_str_a(subject_to):
    return subject_to_regex.search(subject_to)[0]

def extract_str_b(subject_to):
    return subject_to_regex.findall(subject_to)[1][0]

# Extract numeric constants given a string representation of an array
def extract_constants(str_array):
    return extract_constants_regex.finditer(str_array)

# Extract numeric representation of matrix 'A'
def extract_matrix(str_matrix):
    temp_matrix = []
    for vector in extract_str_a_regex.finditer(str_matrix):
        temp_vector = []
        for constant in extract_constants(vector[0]):
            constant = int(constant[0])
            temp_vector.append(constant)
        temp_matrix.append(temp_vector)
    return temp_matrix


# Extract string representation of 'eqin' array
def extract_str_eqin(subject_to):
    return extract_str_eqin_regex.search(subject_to)[0]

# Calculate the number of columns of the matrix 'A' given one of its arrays
def calc_w_len(a_array):
    return len(a_array)

# Generate the required array of 'w' variables
def generate_w_arr(a_array):
    w = []
    for i in range(1, calc_w_len(a_array)+1):
        w.append('w' + str(i))
    return w


def calculate_eqin(MinMax, eqin_in, A_len):
    eqin_out = []
    # Primal is min
    if(MinMax == 'max'):
        for i in range(0, A_len):
            eqin_out.append([-1])
    elif(MinMax == 'min'):
        for i in range(0, A_len):
            eqin_out.append([1])
    return eqin_out


#--------- Read the primal linear problem ---------#

# Open the file
primal_lp = open_textfile('lp-2.txt')

# Read the objective function
objective_function = primal_lp.readline()

# Identify the optimization type
MinMax = identify_primal(objective_function)

print(MinMax)

# Extract the 'c' vector off of the objective function
c = extract_str_c(objective_function)

# Temporary c vector
temp_c = []

# Extract the numeric constants off of vector 'c'
for constant in extract_constants(c):
    constant = int(constant[0])
    temp_c.append([constant])

# Update the c vector to its final form
c = temp_c
print(c)
# Read subject_to line
subject_to = primal_lp.readline()

# Extract string representation of matrix 'A'
A = extract_str_a(subject_to)

# Extract numerical representation of matrix 'A'
temp_A = extract_matrix(A)

# Transpose matrix 'A'
A_transpose = np.transpose(temp_A).tolist()

print(A_transpose)
# Array containing 'w' variables
w = generate_w_arr(A_transpose[1])

# 'eqin' array, stores the types of the constraints
eqin = []

# Temporary array for 'eqin' constraint values
temp_eqin = extract_str_eqin(subject_to)

# Extract numerical values off the eqin string vector
for constraint in extract_constants(temp_eqin):
    eqin.append(int(constraint[0]))

# Calculate the final 'eqin' array
eqin = calculate_eqin(MinMax, eqin, len(A_transpose))
print(eqin)

# Extract temporary 'b' from the subject_to line
temp_b = extract_str_b(subject_to)

# The final 'b' transpose array
b_transpose = []

for constant in extract_constants(temp_b):
    b_transpose.append(int(constant[0]))

print(b_transpose)

# Close the text file of the primal problem
primal_lp.close()


# Write the dual problem to an output text file
# Open a new text file, 'dual.txt' with write permissions

dual_out = open('dual.txt', 'w')

# Min/Max according to the dual problem
dual_out.write(MinMax)

# Space
dual_out.write(' ')

# 'b' transpose
dual_out.write(str(b_transpose))

# Space
dual_out.write(' ')

# 'w' variables
dual_out.write(str(w))

# New line - Whole thing might show on a single line on Windows Notepad
dual_out.write('\n')

# subject to
dual_out.write('s.t.')

# Space
dual_out.write(' ')

# 'A' transpose
dual_out.write(str(A_transpose))

# Space
dual_out.write(' ')

# 'w' variables
dual_out.write(str(w))

# Space
dual_out.write(' ')

# 'Eqin' constraints
dual_out.write(str(eqin))

# Space
dual_out.write(' ')

# 'c' technological constraints
dual_out.write(str(c))
