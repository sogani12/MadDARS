import os
import json

# Load the courses details file
with open("courses.json") as f:
    courses_info = json.load(f)

# helper fuction
# example:
# input: 'CS/MATH/STAT420'
#output: ['420', 'CS', 'MATH', 'STAT']
def parse_course_string(course_str):
    course_code, course_num = course_str[:-3], course_str[-3:]
    codes = sorted(course_code.split('/')) if course_code else []
    return [course_num] + codes 

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

def extract_breadth(designation):
    """
    Extracts Breadth information from the course designation string.
    Looks for "Breadth - " and takes the text until "Level" or "Credit".
    Returns a list with the extracted breadth, or an empty list.
    """
    all_breadths = ['Biological Sci', 'Humanities', 'Social Science', 'Literature',
        'Ethnic Studies', 'Communication Part B', 'Phsyical Sci', 'Natural Science',
        'Quantitative Reasoning Part B', 'Natural Sci', 'Communication Part A',
        'Quantitative Reasoning Part A']
    
    breadths = []
    for breadth in all_breadths:
        if breadth in designation:
            breadths.append(breadth)
    return breadths

def transform_course_entry(entry):
    """
    Transforms a course entry into the target dictionary format.
    If the entry is a list, the second element is used as req_credits.
    If it's a plain string, use the course's credits from courses_info.
    Skip any course codes containing "=" or "+".
    """
    # Determine course code and if there's a req_credits override.
    if isinstance(entry, list):
        course_code = entry[0]
        req_credits = entry[1]
    else:
        course_code = entry
        req_credits = None

    # Skip if course code contains "=" or "+"
    if "=" in course_code or "+" in course_code:
        return entry

    course_data = None
    # Look up the course in courses_info
    for course in courses_info:
        if course_equality(course, course_code):
            course_data = courses_info.get(course)
    if course_data is None:
        print("Course from file did not have a match in courses.json: " + course_code)
        return entry

    # Build the new dictionary entry
    new_entry = {}
    designation = course_data.get("Course Designation: ", "")
    breadth_list = extract_breadth(designation)

    if req_credits is not None:
        new_entry["req_credits"] = req_credits
    else:
        # Attempt to convert the credits from courses_info to an integer.
        credits_str = course_data.get("credits", "")
        try:
            new_entry["credits"] = int(credits_str)
        except ValueError:
            # If conversion fails (e.g. a range like "1-3"), you might skip or handle it differently.
            new_entry["credits"] = credits_str

    new_entry["breadth"] = breadth_list

    return {course_code: new_entry}

def process_courses_in_list(course_list):
    """
    Processes a list of course entries.
    Each entry is transformed if it's a string or a list.
    """
    new_list = []
    for entry in course_list:
        new_list.append(transform_course_entry(entry))
    return new_list

def process_data_structure(data):
    """
    Recursively processes the data structure.
    When a list is found under keys "1", "2", "3", or "4", process it as a course list.
    Otherwise, recursively process dictionaries and lists.
    """
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if isinstance(value, list) and key == '1':
                new_data[key] = process_courses_in_list(value)
            else:
                new_data[key] = process_data_structure(value)
        return new_data
    elif isinstance(data, list):
        return [process_data_structure(item) for item in data]
    else:
        return data

def main():
    base_dir = "data"
    new_base_dir = "transformed_data"  # New directory for transformed files
    
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json"):
                filepath = os.path.join(root, file)
                print("Processing:", filepath)
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    print("Error decoding", filepath)
                    continue

                # Process the data recursively (using your transformation function)
                new_data = process_data_structure(data)

                # Compute the relative path from base_dir, and build a new filepath under new_base_dir.
                rel_path = os.path.relpath(filepath, base_dir)
                new_filepath = os.path.join(new_base_dir, rel_path)

                # Ensure that the target directory exists
                os.makedirs(os.path.dirname(new_filepath), exist_ok=True)

                # Write the transformed data to the new file
                with open(new_filepath, "w") as f:
                    json.dump(new_data, f, indent=2)
    print("Dataset transformation complete.")

if __name__ == "__main__":
    main()
