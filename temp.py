import json

if __name__ == '__main__':
    courses = {}
    with open('courses.json') as f:
        courses = json.load(f)
    for course, val in courses.items():
        if "Course Designation: " in val:
            if 'Breadth' in val["Course Designation: "]:
                print(val["Course Designation: "])

# Biological Sci
# Humanities
# Social Science
# Literature
# Ethnic Studies
# Communication Part B
# Phsyical Sci
# Natural Science
# Quantitative Reasoning Part B
# Natural Sci