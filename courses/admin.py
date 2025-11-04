from django.contrib import admin
from django.db.models import Count
from .models import ElectiveType, Course, StudentSelection


@admin.register(ElectiveType)
class ElectiveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'level']
    list_filter = ['elective_types', 'level', 'credits']
    search_fields = ['code', 'name', 'description']
    filter_horizontal = ['elective_types']


@admin.register(StudentSelection)
class StudentSelectionAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'course', 'elective_type', 'interest', 'created_at']
    list_filter = ['elective_type', 'interest', 'created_at']
    search_fields = ['student_id', 'course__code', 'course__name']
    readonly_fields = ['created_at', 'updated_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('course', 'elective_type')

    # Add custom action to export selections
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="student_selections.csv"'

        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Course Code', 'Course Name', 'Elective Type', 'Interest', 'Date'])

        for selection in queryset:
            writer.writerow([
                selection.student_id,
                selection.course.code,
                selection.course.name,
                selection.elective_type.name,
                selection.get_interest_display(),
                selection.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response

    export_as_csv.short_description = "Export selected as CSV"
