from django.db import models

class ElectiveType(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Elective Type"
        verbose_name_plural = "Elective Types"


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    credits = models.IntegerField()
    level = models.IntegerField()
    prerequisites = models.CharField(max_length=500, blank=True)
    corequisites = models.CharField(max_length=500, blank=True)
    exclusions = models.CharField(max_length=500, blank=True)
    mode = models.CharField(max_length=100)
    assessment = models.CharField(max_length=200)
    description = models.TextField()
    study_guide_url = models.URLField(blank=True)
    course_description_url = models.URLField(blank=True)
    elective_types = models.ManyToManyField(ElectiveType, related_name='courses')

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']
        verbose_name = "Course"
        verbose_name_plural = "Courses"


class StudentSelection(models.Model):
    INTEREST_CHOICES = [
        ('willing', 'Willing to Take'),
        ('not_willing', 'Not Willing to Take'),
    ]

    student_id = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='selections')
    elective_type = models.ForeignKey(ElectiveType, on_delete=models.CASCADE)
    interest = models.CharField(max_length=20, choices=INTEREST_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_id} - {self.course.code} ({self.interest})"

    class Meta:
        unique_together = ['student_id', 'course', 'elective_type']
        ordering = ['-created_at']
        verbose_name = "Student Selection"
        verbose_name_plural = "Student Selections"
