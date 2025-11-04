from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('browse/<int:elective_type_id>/', views.browse_courses, name='browse_courses'),
    path('select/', views.select_elective_type, name='select_elective_type'),
    path('select/<int:elective_type_id>/', views.select_courses, name='select_courses'),
    path('submit/<int:elective_type_id>/', views.submit_selection, name='submit_selection'),
]
