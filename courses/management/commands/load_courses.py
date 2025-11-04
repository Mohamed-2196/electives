import json
from django.core.management.base import BaseCommand
from courses.models import ElectiveType, Course


class Command(BaseCommand):
    help = 'Load courses from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to the JSON file containing course data'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Clear existing data
            self.stdout.write('Clearing existing data...')
            Course.objects.all().delete()
            ElectiveType.objects.all().delete()

            # Load data
            for elective_key, elective_data in data.items():
                self.stdout.write(f'Processing {elective_data["name"]}...')

                elective_type = ElectiveType.objects.create(
                    name=elective_data['name'],
                    description=elective_data['description']
                )

                for course_data in elective_data['courses']:
                    # Get or create course
                    course, created = Course.objects.get_or_create(
                        code=course_data['code'],
                        defaults={
                            'name': course_data['name'],
                            'credits': course_data['credits'],
                            'level': course_data['level'],
                            'prerequisites': course_data['prerequisites'],
                            'corequisites': course_data['corequisites'],
                            'exclusions': course_data['exclusions'],
                            'mode': course_data['mode'],
                            'assessment': course_data['assessment'],
                            'description': course_data['description'],
                            'study_guide_url': course_data['study_guide_url'],
                            'course_description_url': course_data['course_description_url'],
                        }
                    )
                    # Add the elective type to this course
                    course.elective_types.add(elective_type)

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully loaded {len(elective_data["courses"])} courses for {elective_data["name"]}'
                    )
                )

            self.stdout.write(self.style.SUCCESS('All courses loaded successfully!'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Invalid JSON in file: {json_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
