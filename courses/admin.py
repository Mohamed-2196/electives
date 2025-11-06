from django.contrib import admin
from django.db.models import Count, Sum, Case, When, IntegerField
from .models import ElectiveType, Course, StudentSelection


@admin.register(ElectiveType)
class ElectiveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'level', 'total_preference_points', 'selection_count']
    list_filter = ['elective_types', 'level', 'credits']
    search_fields = ['code', 'name', 'description']
    filter_horizontal = ['elective_types']
    actions = ['export_courses_with_points']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _total_points=Sum(
                Case(
                    When(selections__interest='not_willing', then=0),
                    When(selections__interest='willing', then=1),
                    When(selections__interest='prefer', then=2),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            _selection_count=Count('selections')
        )

    def total_preference_points(self, obj):
        return obj._total_points or 0
    total_preference_points.short_description = 'Total Points'
    total_preference_points.admin_order_field = '_total_points'

    def selection_count(self, obj):
        return obj._selection_count or 0
    selection_count.short_description = 'Total Selections'
    selection_count.admin_order_field = '_selection_count'

    def export_courses_with_points(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="courses_with_points.csv"'

        writer = csv.writer(response)
        writer.writerow(['Course Code', 'Course Name', 'Credits', 'Level', 'Total Points', 'Total Selections'])

        # Sort by total points (descending)
        sorted_queryset = sorted(queryset, key=lambda x: x._total_points or 0, reverse=True)

        for course in sorted_queryset:
            writer.writerow([
                course.code,
                course.name,
                course.credits,
                course.level,
                course._total_points or 0,
                course._selection_count or 0,
            ])

        return response

    export_courses_with_points.short_description = "Export courses with point totals (sorted by points)"


@admin.register(StudentSelection)
class StudentSelectionAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'course', 'elective_type', 'interest', 'preference_points', 'created_at']
    list_filter = ['elective_type', 'interest', 'created_at']
    search_fields = ['student_id', 'course__code', 'course__name']
    readonly_fields = ['created_at', 'updated_at']

    def preference_points(self, obj):
        return obj.points
    preference_points.short_description = 'Points'

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
        writer.writerow(['Student ID', 'Course Code', 'Course Name', 'Elective Type', 'Interest', 'Points', 'Date'])

        for selection in queryset:
            writer.writerow([
                selection.student_id,
                selection.course.code,
                selection.course.name,
                selection.elective_type.name,
                selection.get_interest_display(),
                selection.points,
                selection.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response

    export_as_csv.short_description = "Export selected as CSV"
