import re

'''
    This piece of python code is used to read
    a Linear Problem of LP-1 format from a text file,
    convert it to LP-2 format, and save it into an
    output text file.
'''
########### ASSISTIVE VARIABLES BEGIN ###########

A = []
b = []
c = []
Eqin = []
x = []

# The two types of Linear Problem Optimizations, min (minimize) or max (maximize)
lp_type_arr = ['min', 'max']

subject_to_arr = ['st ', 's.t. ', 'subject to']
signs_arr = ['+', '-']

# Compiled regular expressions
obj_fn_regex = re.compile('([\+]|[\-])(\d*[x]\d*)|(\d*[x]\d*)|(?:[x]\d*)|^[\+\-]')
minmax_regex = re.compile('(min)[\ ]*|([\+]|[\-])(\d*[x]\d*)|(max)[\ ]*|([\+]|[\-])(\d*[x]\d*)')
subject_to_regex = re.compile('(((subject\ to)|(s{1}\.t{1}\.)|(st))\ *((\-|\+|)(\ *\d*x\d+\ *)|((>=)|(<=)|(=))\ *\d*)|((\-|\+)(\ *\d*x\d+\ *)|((>=)|(<=)|(=))\ *\d*)){1,}')
constraints_regex = re.compile('(\ *((\-|\+|)(\ *\d*x\d+\ *)|((>=)|(<=)|(=))\ *\d*)|((\-|\+)(\ *\d*x\d+\ *)|((>=)|(<=)|(=))\ *\d*)){1,}')
extract_constraints_regex_1 = re.compile('(\ *((\-|\+|)(\ *\d*x\d+\ *))|((\-|\+)(\ *\d*x\d+\ *))){1,}')
signs_regex = re.compile('(((>=)|(<=)|(=)){1})')
rhs_regex = re.compile('(((>=)|(<=)|(=)))(\ *\d*){1}')


# Identify the type of the Linear Problem. min -> -1, max -> 1
MinMax = 0 # Initialize MinMax to neutral zero (0)

########### ASSISTIVE VARIABLES END ###########

########### ASSISTIVE FUNCTIONS BEGIN ###########

# Return -1 (negative one) if LP is of type 'min' or 1 (positive one) if LP is of type 'max'
def identify_lp_type(line_1):
    # Check if the first line starts with a 'min' or a 'max' using regular expression
    if re.match(minmax_regex, line_1) != None:
        lp_type = str(re.match(minmax_regex, line_1)[0]).strip()
        if lp_type == 'min':
                # The LP is of type 'min'
            return -1
        elif lp_type == 'max':
                # The LP is of type 'max'
            return 1
    else:
        raise Exception('The objective function is not in a correct format.')

# Strip empty elements from a given objective function's array
def strip_empty_elems(obj_fn):
    # Initialize an array to store the non-empty elements of the objective function
    clean_obj_fn_arr = []
    # Iterate through all of the elements of the given objective function's array
    for element in obj_fn:
        # If the current element is not an empty one, strip any spaces that it might contain and append it to the array
        if element != None:
            clean_obj_fn_arr.append(element.strip())
    # After done removing any empty elements return the new and clean objective function's array, i.e clean_obj_fn
    return clean_obj_fn_arr

# Parse the first line of the text file and return an array containing the objective function
def parse_obj_fn(line_1, MinMax):
    # Strip the 'min ' or 'max ' and newline characters.
    # Keep everything else including the constants by using regular expressions.
    if MinMax == -1:
        temp_obj_fn = re.split(obj_fn_regex, line_1.lstrip('min ').rstrip('\n'))
    elif MinMax == 1:
        temp_obj_fn = re.split(obj_fn_regex, line_1.lstrip('max ').rstrip('\n'))
    else:
        raise Exception('There was an error with MinMax')

    # Remove the empty elements and return the array
    return list(filter(None, strip_empty_elems(temp_obj_fn)))

def calc_total_constants(line):
    total_constants = 0
    for element in line:
        if element not in signs_arr:
            total_constants += 1
    return total_constants

def calc_total_signs(line):
    total_signs = 0
    for element in line:
        if element in signs_arr:
            total_signs += 1
    return total_signs

# Validate the format of the objective function
# Perform checks on whether there are signs in between the variables
def validate_obj_fn(obj_fn):
    # If the total number of signs (either + or -) is not equal to the total number of constants minus 1,
    # then there is a missing sign somwehere on the objective function.
    if calc_total_signs(obj_fn) != calc_total_constants(obj_fn) - 1:
        # check if for example the objective functions starts with '-15x'
        if calc_total_signs(obj_fn) - 1 != calc_total_constants(obj_fn) - 1:
            raise Exception('There was an error validating the objective function.')

# Extract constants from a given line
def extract_constants(line):
    # Store the variables of the line given, e.g x1, x2, x3,...,xn
    vars_arr = []
    # Store the constants of the objective function
    constants = []
    # Numeric counter to manipulate the elements of the 'for' loop below
    i = 0

    # If a number has a minus sign before it, then concatenate it to its constant to get a correct value
    # Iterate through all the elements of the objective function's array
    for element in line:
        # Process any element as long as it is not a plus or minus sign
        if element not in signs_arr:
                # If the element before the current is a minus sign,
                # then concatenate the sign with the current element and append it altoghether on the 'vars_arr'
                if line[i-1] == '-':
                    vars_arr.append(line[i-1] + element)
                else:
                    # If, on the other hand, the element before the current is a plus sign,
                    # then no need to modify it since we can represent positive values without prepending a plus sign.
                    vars_arr.append(element)
        # Increment the counter
        i += 1

    # Extract the constants from each variable (e.g. 5x1 should yield 5)
    for const in vars_arr:
        # If the current element on the 'vars_arr' array is for example,
        # an 'x1' then we can simply save it as a constant of '1' in the constants array.
        if const.partition('x')[0] == '':
            constants.append('1')
        elif const.partition('x')[0] == '-':
            constants.append('-1')
        # Else, if the current element on the 'vars_arr' array, after it -the array- being partitioned,
        # contains a numeric constant, then simply append that constant on the constants array.
        else:
            constants.append(const.partition('x')[0])

    # Filter the constants array for empty elements
    constants = list(filter(None, constants))
    # Return the constants array
    return constants

def validate_subject_to_line(line):
    # Apply the regex and extract only the part that matches & is relevant
    if subject_to_regex.match(line) is not None:
        subject_to_line = subject_to_regex.match(line)[0]
        for keyword in subject_to_arr:
            if keyword in subject_to_line:
                return subject_to_line.lstrip(keyword)
    else:
        raise Exception('There was an error parsing the \'subject to\' line of constraints.')

def parse_constraint_lines(line, line_counter):
    if line_counter == 2:
        return validate_subject_to_line(line)
    else:
        if constraints_regex.match(line):
            return (constraints_regex.match(line)[0]).lstrip()
        else:
            return -1

def extract_eqin_values(line, line_counter):
    eqin_sign = str(signs_regex.search(parse_constraint_lines(line, line_counter))[0])
    if eqin_sign == '<=':
        return -1
    elif eqin_sign == '>=':
        return 1
    elif eqin_sign == '=':
        return 0

def extract_contraints(line):
    constraint_line = list(filter(None, re.split(obj_fn_regex, line.rstrip(' \n'))))
    return extract_constants(strip_empty_elems(constraint_line))


########### ASSISTIVE FUNCTIONS END ###########

# Open the text file containing the Linear Problem
lp_in = open('lp.txt', 'r')

# Read the first line, i.e the objective function of the LP
line_1 = lp_in.readline()

# Check if the Linear Problem is either 'min' or 'max' and update 'MinMax' accordingly
MinMax = identify_lp_type(line_1)

# Parse the first line of the text file
objective_fn = parse_obj_fn(line_1, MinMax)
print(objective_fn)
# Find all the x variables and store them on the 'x' array
x = re.findall(r'([x]\d*)', str(objective_fn))

# Validate if the objective function remains in a correct format (it's okay if it's without 'min' or 'max' this time)
validate_obj_fn(objective_fn)

# Extract the constants from the objective function's variables and store to 'c' transpose
c = extract_constants(objective_fn)

# Parse the technological constraints of the LP
# Numerical counter indicating the second line of the text file
line_counter = 2

# Extract the constants off of the technological constraint lines
for line in lp_in.readlines():
    if parse_constraint_lines(line, line_counter) != -1:
        # Extract the techonological constraints
        constr_line = extract_constraints_regex_1.match(parse_constraint_lines(line, line_counter))
        print(constr_line)
        # Add the technological constraints on the A matrix
        A.append(extract_contraints(constr_line[0]))
        # Store the corresponding value of Eqin
        Eqin.append(extract_eqin_values(line, line_counter))
        # Extract the Right Hand Side of the technological constraints
        b.append(rhs_regex.search(parse_constraint_lines(line, line_counter))[6])
    line_counter += 1


# Close the input file
lp_in.close()

# Transform Eqin array into a column vector
temp_eqin = []
for eqin_value in Eqin:
    temp_eqin.append([eqin_value])
Eqin = temp_eqin

# Transform b array into a column vector
temp_b = []
for b_value in b:
    temp_b.append([b_value.strip()])
b = temp_b


# Open the output file to write the LP-2 problem
lp_out = open('lp-2.txt', 'w')

# Write min/max to the file
if MinMax == -1:
    lp_out.write(lp_type_arr[0])
elif MinMax == 1:
    lp_out.write(lp_type_arr[1])

# # Transform c array into column vector
#
# c_transpose = []
# for c_value in c:
#     c_transpose.append([c_value])

# Write c transpose
lp_out.write(' ' + str(c))

# Write x variables
lp_out.write(' ' + str(x) + '\n')

# Write A
lp_out.write('s.t. ')
lp_out.write(str(A))

# Transform initial 'x' array to column vector
x_constraints = []
for variable_x in x:
    x_constraints.append([variable_x])

# Write x variables
lp_out.write(' ' + str(x_constraints))

# Write Eqin
lp_out.write(' ' + str(Eqin))

# Write b
lp_out.write(str(b))

# Close the output file
lp_out.close()
