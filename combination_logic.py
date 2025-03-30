import os
import json
# TODO: Make sure to implement the includion of college requirements json file depending on major
# TODO: Check college checking
# If concurrent_no key section isn't satisfied, total_min_sems must be considered
# not considering concurrent_ keys and breadth requirements for now

# example element:
# {1: ['interior-architecture-bs', 'textiles-design-certificate', 
#     'material-culture-studies-certificate'], 
#  2: [one possible choice of suggested courses]}
combinations = []
programs = []
courses = {}
# will put any courses here that have an 'or' relationship given a key
# essentially, if a course is present in this dictionary given a key,
# that course won't be able to fulfill that sections requiremenets
# eg: {'h1': [['CS200', 'CS202'], ['CS420', 'CS424']]}
course_or_applicability = {}

# Helper function to load JSON files from subdirectories
# each output element is a list of json data of all programs
def load_json_files(DATA_DIR):
    global programs
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".json"):
                filepath = os.path.join(root, file)
                with open(filepath) as f:
                    data = json.load(f)
                    data['college'] = root
                    programs.append(data)
    return programs


# Helper function to load ongoing degree program JSON files
def load_ongoing_degree_files(DATA_DIR, ongoing_degrees):
    ongoing_degree_files = []
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            for degree in ongoing_degrees:
                if file[:-5] == degree: # -5 to avoid .json
                    filepath = os.path.join(root, file)
                    with open(filepath) as f:
                        data = json.load(f)
                        data['college'] = root
                        ongoing_degree_files.append(data)
            
    return ongoing_degree_files

# helper fuction
# example:
# input: 'CS/MATH/STAT420'
#output: ['420', 'CS', 'MATH', 'STAT']
def parse_course_string(course_str):
    course_code, course_num = course_str[:-3], course_str[-3:]
    codes = sorted(course_code.split('/')) if course_code else []
    return [course_num] + codes 

# checks if two colleges can have cross degrees
def college_compatible(user_college, program_college):
    if user_college == 'l&s' or program_college == 'l&s' or user_college == program_college:
        return True

# checks if two courses are equal
def course_equality(course_from_list, given_course):
    if '=' in course_from_list: # range case. eg: CS200=CS570
        lower_range_course, upper_range_course = course_from_list.split('=')
        lower_range_course = parse_course_string(lower_range_course)
        upper_range_course = parse_course_string(upper_range_course)
        given_course = parse_course_string(given_course)
        if int(lower_range_course[0]) <= int(given_course[0]) and int(given_course[0]) <= int(upper_range_course[0]):
            for code in given_course[1:]:
                if code in lower_range_course[1:]:
                    return True
            return False
        return False
    
    elif '+' in course_from_list: # any course of code type case. eg: CS+ (any CS course)
        codes = course_from_list[:-1]
        codes = codes + "420" # appending a random number to make use of parse_course_string function
        codes = parse_course_string(codes)
        given_course = parse_course_string(given_course)
        for code in given_course[1:]:
            if code in codes[1:]:
                return True
        return False

    # Normal case comparng two course codes
    given_course = parse_course_string(given_course)
    course_from_list = parse_course_string(course_from_list)
    if given_course[0] != course_from_list[0]:
        return False
    for code in given_course[1:]:
        if code in course_from_list[1:]:
            return True
    return False
    
# checks given a list of courses, does the given course satisfy any one according to schema
# courses: ['CS200', 'CS300', ['CS400', 3]]
def key1_check(courses, course):
    for c in courses:
        # if course has a specific credits requirement
        code = c
        if isinstance(c, list):
            if c[1] == course[1]: # satisfies credit requirement
                code = c[0] # just change it to the course code as a string

        if course_equality(code, course[0]):
            return c
    return False
        
# checks if a course has an or/and relationship in the section
# courses: [['CS200', 'CS202'], ['CS400', 'CS402']]
def or_and_check(courses, course):
    for comb in courses:
        for c in comb:
            if course_equality(c, course[0]):
                return (comb, c)
    return (False, 'womp_womp')
        
# checks if course was covered outside, and whether its applicable to this section
# on those grounds
def covered_outside_check(val, course):
    if len(course) > 2: # course has been used somewhere else
        if 'covered_outside' not in val:
            if 'outside_credit' not in val:
                return False
            else:
                for section in val['outside_credit']:
                    if section[0] in course[2:]: # valid from/ used by same section
                        if section[1] <= 0: # credits from that section have already been fulfilled
                            return False
                        else:
                            return True
    return True

# handles h1 key related stuff
# question: does it modify dictionary as intended
def h1_handler(h1_val, course):
    match_found = False
    or_found = False
    satisfied = False

    # if this course has been used in some other section, is it still applicable to this section
    if not covered_outside_check(h1_val, course):
        return (match_found, or_found, satisfied)
    
    if '1' in h1_val:
        # no matches in h1 header
        matching_course = key1_check(h1_val['1'], course)
        if not matching_course:
            return (match_found, or_found, satisfied)
        match_found = True
        h1_val['1'].remove(matching_course) # modifying h1 dict
        if len(h1_val['1']) == 0:
            satisfied = True
    if '2' in h1_val:
        or_found, _ = or_and_check(h1_val['2'], course)
        if or_found:
            h1_val['2'].remove(or_found) # modifying h1 dict
    return (match_found, or_found, satisfied)

# handles the nested key within an h2 key
# some code is sorta similar to the main cross_course_logic function
def nested_handler(nested_val, course):
    num_credits_satisfied = 0
    num_options_satisfied = 0
    global course_or_applicability
    for key in nested_val: # going over h2_x_y type keys
        curr_key_satisfied = 0
        num_inner_keys = 0
        for inner_key, inner_val in nested_val[key]:
            # use h1_handler for h1 key
            # modify total_min_credits appropriately and change the 
            # course_or_applicability variable if needed
            if inner_key == 'h1':
                num_inner_keys += 1
                h1_match, h1_or, h1_satisfied = h1_handler(inner_val, course)
                if h1_match:
                    num_credits_satisfied += course[1]
                    course.append(inner_key) # marking this course used as a course being used for multiple 
                    # sections varies program to program. No need to check if course was used for h1 key
                if h1_or:
                    if key in course_or_applicability:
                        course_or_applicability[inner_key].append(h1_or)
                    else:
                        course_or_applicability[inner_key] = []
                        course_or_applicability[inner_key].append(h1_or)
                if h1_satisfied:
                    curr_key_satisfied += 1
                continue
            
            elif inner_key.startswith('h2'):
                num_inner_keys += 1
                h2_credits_satisfied, h2_or, course, h2_satisfied = h2_handler(val, course)
                if h2_credits_satisfied > 0:
                    num_credits_satisfied += h2_credits_satisfied
                    course.append(key)
                if h2_or:
                    if key in course_or_applicability:
                        course_or_applicability[key].append(h1_or)
                    else:
                        course_or_applicability[key] = []
                        course_or_applicability[key].append(h1_or)
                if h2_satisfied:
                    curr_key_satisfied += 1

        # if the whole h2_x_y type key is satisfied, only then is an option satisfied for nested
        if curr_key_satisfied == num_inner_keys:
            num_options_satisfied += 1
    
    return (num_credits_satisfied, num_options_satisfied, course)
# handles h2 keys including all its sub keys
# same question as h1_handler
def h2_handler(h2_val, course):
    num_credits_satisfied = 0
    or_found = False
    satisfied = False

    # checking if this section has already been fulfilled
    if 'num_options' in h2_val:
        if h2_val['num_options'] == 0:
            return (num_credits_satisfied, or_found, course, satisfied)
    elif 'num_credits' in h2_val:
        if h2_val['num_credits'] <= 0:
            return (num_credits_satisfied, or_found, course, satisfied)
    
    # if this course has been used in some other section, is it still applicable to this section
    if not covered_outside_check(h2_val, course):
        return (num_credits_satisfied, or_found, course, satisfied)

    options_satisfied = None
    if 'nested' in h2_val:
        num_credits_satisfied, options_satisfied, course = nested_handler(h2_val['nested'])

    if '1' in h2_val:
        # no matches in h2 header
        matching_course = key1_check(h2_val['1'], course)
        if not matching_course:
            return (num_credits_satisfied, or_found, course, satisfied)
        num_credits_satisfied += course[1]

        h2_val['1'].remove(matching_course) # modifying h2 dict
        
    if 'num_credits' in h2_val:
        h2_val['num_credits'] -= num_credits_satisfied
        if h2_val['num_credits'] <= 0:
            satisfied = True

    option_completed = True
    if '2' in h2_val:
        and_found, course_to_remove = or_and_check(h2_val['2'], course)
        
        if and_found:
            idx = h2_val['2'].index(and_found)
            h2_val['2'][idx].remove(course_to_remove) # modifying h2 dict
            # to decrement the num_options key (if present), the course must not have 
            # any unsatisfied and relationshipped courses
            if len(h2_val['2'][idx]) != 0:
                option_completed = False
        
    if 'num_options' in h2_val and option_completed:
        # if a nested key is present, then keys 1, 2, 3 wont be present
        if options_satisfied is None:
            h2_val['num_options'] -= 1
        else:
            h2_val['num_options'] -= options_satisfied
        if h2_val['num_options'] == 0:
            satisfied = True

    if '3' in h2_val:
        or_found, _ = or_and_check(h2_val['3'], course)
        if or_found:
            h2_val['3'].remove(or_found) # modifying h2 dict    

    return (num_credits_satisfied, or_found, course, satisfied)

# checks if a given course isnt applicable to satisfy a section as its 'or' relationship
# equivalent has already fulfilled it      
def course_applicability_check(course_or_applicability, course, key):
    for or_comb in course_or_applicability[key]:
        for or_course in or_comb:
            if course_equality(or_course, course[0]):
                return True
    return False

def h1_h2_common_courses_helper(val):
    if '1' in val:
        for course in val['1']:
            if not isinstance(course, list):

# returns a list of all common courses amongst degree programs as well a dictionary
# of a course with its primary degree program to avoid double counting
def get_common_courses(element):
    element_to_course = {}
    for degree in element:
        for key, val in degree.items():


# courses: [['CS200', 3], []]
def cross_course_logic(element, courses, course_element = None):
    suggested_courses = []
    global course_or_applicability
    # modifying programs in place
    for i in range(len(element)): 
        
        # for each program checking if each course completes some criteria
        for course in courses:
            # when we go over common courses in the second phase, we don't want to use a course
            # for a degree program from which we took it. For eg: a course is common between 
            # programs A & B, we don't want to use this program for both A & B, so 
            # course_element will have an entry like 'course_name': 'A'
            if course_element is not None:
                if course_element[course[0]] == element[i]['title']:
                    continue
            # going over each key, val pair based on schema
            for key, val in element[i].items():
                # checking if course is applicable for this key
                if course_applicability_check(course_or_applicability, course, key):
                    continue

                # use h1_handler for h1 key
                # modify total_min_credits appropriately and change the 
                # course_or_applicability variable if needed
                if key == 'h1':
                    h1_match, h1_or, _ = h1_handler(val, course)
                    if h1_match:
                        element[i]['total_min_credits'] -= course[1]
                        suggested_courses.append(course[0])
                        course.append(key) # marking this course used as a course being used for multiple 
                        # sections varies program to program. No need to check if course was used for h1 key
                    if h1_or:
                        if key in course_or_applicability:
                            course_or_applicability[key].append(h1_or)
                        else:
                            course_or_applicability[key] = []
                            course_or_applicability[key].append(h1_or)
                    continue

                if key.startswith('h2'):
                    h2_credits_satisfied, h2_or, course, _ = h2_handler(val, course)
                    if h2_credits_satisfied > 0:
                        element[i]['total_min_credits'] -= h2_credits_satisfied
                        suggested_courses.append(course[0])
                        course.append(key)
                    if h2_or:
                        if key in course_or_applicability:
                            course_or_applicability[key].append(h1_or)
                        else:
                            course_or_applicability[key] = []
                            course_or_applicability[key].append(h1_or)

    return (element, suggested_courses)

#primary function that gets combinations
# completed_courses: [['CS200', 3], ['ART102', 2]]
# ongoing degrees: ['interior-architecture-bs', 'textiles-design-certificate']
# primary_college: 'sohe' (School of Human Ecology) [Change depending on combination]
# remaining_sems: 5
# credits_per_sem: 16
# DATA_DIR: 'data'
# curr_element: ['interior-architecture-bs' json data, 'textiles-design-certificate' json data, 
#               'material-culture-studies-certificate' json data]
def get_combinations(completed_courses, primary_college, remaining_sems, credits_per_sem, curr_element):
    global programs
    global courses
    global combinations
    
    for program in programs:
        # dont analyse programs already in the element
        if program in curr_element: # does this work as intended?
            continue

        # checking if program is worth analyzing based on college
        if not program['title'].endswith('certificate'):
            if not college_compatible(primary_college, program['college']):
                continue

        # do cross courses logic where we take into account the user's completed courses
        # as well as common courses between the programs in the current element to figure 
        # the real total_min_credits required for the combination
        curr_element.append(program)
        curr_element, _ = cross_course_logic(curr_element, completed_courses)
        common_courses, course_element = get_common_courses(curr_element)
        curr_element, suggested_courses = cross_course_logic(curr_element, common_courses, course_element)

        # checking if with the updated total_min_credits, the combination is feasible or not
        if not combination_feasible(curr_element, remaining_sems, credits_per_sem):
            curr_element.remove(program)
            continue
        
        # append to combinations and then recurse to find a longer combination
        primary_college = combinations_append(curr_element, suggested_courses) # also updates primary college
        get_combinations(completed_courses, primary_college, remaining_sems, credits_per_sem, curr_element)
        curr_element.remove(program)




def start_get_combinations(completed_courses, ongoing_degrees, primary_college, remaining_sems, credits_per_sem, DATA_DIR):
    global programs
    global courses
    global combinations
    # loading all programs and courses
    programs = load_json_files(DATA_DIR)
    with open('courses.json') as f:
        courses = json.load(f)
    
    # loading each element with the ongoing_degrees
    curr_element = []
    ongoing_degree_files = load_ongoing_degree_files(DATA_DIR, ongoing_degrees)
    for degree in ongoing_degree_files:
        curr_element.append(degree)
    
    # modifies the combinations global variable
    get_combinations(completed_courses, primary_college, remaining_sems, credits_per_sem, curr_element)
    return combinations