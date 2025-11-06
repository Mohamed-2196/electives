import json
import re

def extract_course_level(course_code):
    """Extract the level (100, 200, 300) from a course code."""
    match = re.search(r'(\d)', course_code)
    if match:
        level_digit = int(match.group(1))
        return level_digit * 100
    return 0

def parse_prerequisites_string(prereq_string):
    """Parse the prerequisites string and extract individual course codes."""
    if not prereq_string or prereq_string.strip() == "":
        return []

    # Remove parentheses and split by common separators
    # Handle patterns like "AC1025+ST104A", "EC2066 or MN2028", "(EC2066 or MN2028) + (EC2020 or FN2208)"
    prereq_string = prereq_string.replace("(", "").replace(")", "")

    # Extract all course codes (pattern: 2-3 letters followed by 3-4 digits and optional letter)
    course_codes = re.findall(r'[A-Z]{2,3}\d{3,4}[A-Z]?', prereq_string)

    return list(set(course_codes))  # Remove duplicates

def split_prerequisites_by_level(course_level, prereq_string):
    """
    Split prerequisites into actual prerequisites (lower level) and corequisites (same level).

    Args:
        course_level: The level of the current course (100, 200, 300)
        prereq_string: The original prerequisites string

    Returns:
        tuple: (prerequisites_list, corequisites_list)
    """
    if not prereq_string or prereq_string.strip() == "":
        return [], []

    course_codes = parse_prerequisites_string(prereq_string)

    prerequisites = []
    corequisites = []

    for code in course_codes:
        code_level = extract_course_level(code)
        if code_level < course_level:
            prerequisites.append(code)
        elif code_level == course_level:
            corequisites.append(code)
        # If code_level > course_level, it's an error but we'll ignore it

    return prerequisites, corequisites

def process_courses_json(input_file, output_file):
    """Process the courses JSON file and split prerequisites."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Process each elective type
    for elective_type_key in data:
        courses = data[elective_type_key].get('courses', [])

        for course in courses:
            course_level = course['level']
            original_prereqs = course.get('prerequisites', '')

            # Split prerequisites based on level
            prereqs_list, coreqs_list = split_prerequisites_by_level(course_level, original_prereqs)

            # Update the course data
            # Keep the original format but split properly
            if prereqs_list:
                course['prerequisites'] = '+'.join(sorted(prereqs_list))
            else:
                course['prerequisites'] = ''

            if coreqs_list:
                course['corequisites'] = '+'.join(sorted(coreqs_list))
            # If no corequisites found, keep existing value (might already have something)

    # Write the updated JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Processed courses saved to {output_file}")

if __name__ == "__main__":
    input_file = r"C:\Users\MY-PC\elective\courses_data.json"
    output_file = r"C:\Users\MY-PC\elective\courses_data_updated.json"

    process_courses_json(input_file, output_file)

    # Print some statistics
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_courses = 0
    courses_with_prereqs = 0
    courses_with_coreqs = 0

    print("\n=== Processing Summary ===")
    for elective_type_key in data:
        courses = data[elective_type_key].get('courses', [])
        total_courses += len(courses)

        for course in courses:
            if course.get('prerequisites', ''):
                courses_with_prereqs += 1
            if course.get('corequisites', ''):
                courses_with_coreqs += 1

    print(f"Total courses processed: {total_courses}")
    print(f"Courses with prerequisites: {courses_with_prereqs}")
    print(f"Courses with corequisites: {courses_with_coreqs}")
