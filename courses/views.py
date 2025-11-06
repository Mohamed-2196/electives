from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Case, When, IntegerField
from .models import ElectiveType, Course, StudentSelection


def home(request):
    """Home page showing elective types"""
    elective_types = ElectiveType.objects.all()
    return render(request, 'courses/home.html', {'elective_types': elective_types})


def browse_courses(request, elective_type_id):
    """Browse courses for a specific elective type"""
    elective_type = get_object_or_404(ElectiveType, id=elective_type_id)
    courses = Course.objects.filter(elective_types=elective_type).annotate(
        total_points=Sum(
            Case(
                When(selections__interest='not_willing', then=0),
                When(selections__interest='willing', then=1),
                When(selections__interest='prefer', then=2),
                default=0,
                output_field=IntegerField()
            )
        )
    ).order_by('-total_points', 'code')

    return render(request, 'courses/browse.html', {
        'elective_type': elective_type,
        'courses': courses,
        'mode': 'browse'
    })


def select_elective_type(request):
    """Choose elective type for selection"""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        if student_id:
            request.session['student_id'] = student_id
            elective_types = ElectiveType.objects.all()
            return render(request, 'courses/select_elective_type.html', {
                'elective_types': elective_types,
                'student_id': student_id
            })
        else:
            messages.error(request, 'Please enter your student ID')
            return redirect('home')
    return redirect('home')


def select_courses(request, elective_type_id):
    """Select courses for a specific elective type"""
    student_id = request.session.get('student_id')
    if not student_id:
        messages.error(request, 'Please enter your student ID first')
        return redirect('home')

    elective_type = get_object_or_404(ElectiveType, id=elective_type_id)
    courses = Course.objects.filter(elective_types=elective_type).annotate(
        total_points=Sum(
            Case(
                When(selections__interest='not_willing', then=0),
                When(selections__interest='willing', then=1),
                When(selections__interest='prefer', then=2),
                default=0,
                output_field=IntegerField()
            )
        )
    ).order_by('-total_points', 'code')

    # Get existing selections for this student
    existing_selections = StudentSelection.objects.filter(
        student_id=student_id,
        elective_type=elective_type
    ).values_list('course_id', 'interest')

    selections_dict = {course_id: interest for course_id, interest in existing_selections}

    return render(request, 'courses/select.html', {
        'elective_type': elective_type,
        'courses': courses,
        'student_id': student_id,
        'selections': selections_dict,
        'mode': 'select'
    })


def submit_selection(request, elective_type_id):
    """Submit course selection"""
    if request.method != 'POST':
        return redirect('home')

    student_id = request.session.get('student_id')
    if not student_id:
        messages.error(request, 'Session expired. Please enter your student ID again')
        return redirect('home')

    elective_type = get_object_or_404(ElectiveType, id=elective_type_id)

    # Clear existing selections for this elective type
    StudentSelection.objects.filter(
        student_id=student_id,
        elective_type=elective_type
    ).delete()

    # Save new selections
    courses = Course.objects.filter(elective_types=elective_type)
    selections_made = 0

    for course in courses:
        interest = request.POST.get(f'course_{course.id}')
        if interest in ['willing', 'not_willing', 'prefer']:
            StudentSelection.objects.create(
                student_id=student_id,
                course=course,
                elective_type=elective_type,
                interest=interest
            )
            selections_made += 1

    messages.success(request, f'Successfully submitted {selections_made} selections for {elective_type.name}')
    return redirect('home')
