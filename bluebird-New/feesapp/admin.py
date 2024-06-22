from django.contrib import admin
from django.db import models
from . import models
from django.db.models.functions import Lower


@admin.register(models.School)
class School(admin.ModelAdmin):
    list_display = ("school_name", "school_discription", 'school_logo')
    search_fields = ['school_name']

    def get_ordering(self, request):
        return [Lower('school_name')]


@admin.register(models.ClassModel)
class ClassModel(admin.ModelAdmin):
    list_display = ("id", "class_name", "school_id")
    search_fields = ['-class_name']
    ordering = ('class_name',)


@admin.register(models.Student)
class Student(admin.ModelAdmin):
    list_display = ("scolar_no", "student_name", "class_id", "RTE")
    ordering = ('class_id',)


@admin.register(models.StudentFees)
class StudentFees(admin.ModelAdmin):
    list_display = ("student_id",)
    ordering = ('student_id',)


@admin.register(models.FeesStructure)
class FeesStructure(admin.ModelAdmin):
    list_display = ("class_id", 'installment1', 'installment2', 'installment3')
    ordering = ('class_id',)


@admin.register(models.AdminUser)
class AdminUser(admin.ModelAdmin):
    list_display = ("name", "phone",)
    ordering = ('name',)


@admin.register(models.LateFees)
class AdminUser(admin.ModelAdmin):
    list_display = ['id', 'type', 'fees']
