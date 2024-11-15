import pdfplumber
import re

def extract_completed_courses(pdf_file):
    """
    Extracts completed course codes and names from the PDF using regex.

    Parameters:
    pdf_file (fitz.open): Opened PDF document object.

    Returns:
    tuple: (completed_courses, course_code_list)
    """
    completed_courses = []  # List to store course codes and names as tuples
    course_code_list = []

# Loop through all the pages of the PDF
    for page in pdf_file.pages:
        text = page.extract_text()

        # Regex to capture course codes with spaces, hyphenated codes, and course names
        course_matches = re.findall(r"\b([A-Z]+(?:[ -][A-Z]+)*)(\s?\d{3})\s+\d+\.\d+\s+[A-Z]+\s+(.+)", text)

        # Loop through matches and add course code and name to the list
        for match in course_matches:
            # Combine the alphabetic part and numeric part of the course code (preserving spaces)
            course_code = match[0] + match[1]  # Keep spaces between course code parts
            course_name = match[2]  # The course name

            # Store the course code and name as a tuple in the list
            completed_courses.append((course_code, course_name))

    # Print only the course codes (with spaces preserved) and their names
    for course_code in completed_courses:
        course_code_list.append(course_code[0])

    # Return the list of completed courses and the unique course codes
    return set(course_code_list)

def parse_dars_pdf(pdf_path):
    """
    Combines the extraction of completed courses and section processing.

    Parameters:
    pdf_path (str): Path to the DARS PDF file.

    Returns:
    tuple: (sections_data, completed_courses)
    """
    # Open the PDF file
    pdf_file = pdfplumber.open(pdf_path)

    # Extract completed courses
    
    ##completed_courses is a set of courses
    completed_courses = extract_completed_courses(pdf_file) 

#     # Extract text from PDF for section data
#     pdf_text = extract_text_from_pdf(pdf_path)

#     # Process the PDF text and return sections data along with completed courses
#     sections_data, completed_courses = process_pdf_data(pdf_text, completed_courses)

    # Return both sections and completed courses data
#     return sections_data, completed_courses
    return completed_courses
