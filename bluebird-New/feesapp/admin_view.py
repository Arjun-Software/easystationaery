from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views import View
import uuid
import json
from feesapp import views
from .models import *
from bluebird.settings import userdb
from django.http import HttpResponse, JsonResponse
import pandas as pd
from django.core.paginator import Paginator
from django.http import FileResponse
import os
import pymongo
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


class LoginView(View):
    return_url = None

    def get(self, request):
        LoginView.return_url = request.GET.get('return_url')
        return render(request, 'admintemp/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = AdminUser.get_admin_user_by_email(email)
        error_message = None
        if user:
            flag = True if password == user.password else False
            if flag:
                request.session['user'] = user.id
                request.session['admin'] = user.admin

                if LoginView.return_url:
                    return HttpResponseRedirect(LoginView.return_url)
                else:
                    LoginView.return_url = None
                    if user.admin:
                        return redirect('indexpage')
                    else:
                        error_message = 'Not an Admin user'
            else:
                error_message = 'Email or Password invalid !!'
        else:
            error_message = 'Email or Password invalid !!'

        print(email, password)
        return render(request, 'admintemp/login.html', {'error': error_message})


def logout(request):
    request.session.clear()
    return redirect('login')


def data_upload(request, sheet):
    if request.session.get('admin'):
        file = request.FILES['file']
        path = default_storage.save(
            f'templates/{file.name}', ContentFile(file.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        if sheet == "Student":
            data = pd.read_excel(tmp_file)
            student = data[['Scholar No', 'Student Name', 'Father Name',
                            'Mother Name', 'Class', 'RTE', 'Full Paid']]
            student.rename(columns={'Scholar No': 'scolar_no', 'Student Name': 'student_name', 'Father Name': 'father_name',
                                    'Mother Name': 'mother_name', 'Class': 'class_id_id', 'RTE': 'RTE', 'Full Paid': 'Full_paid'}, inplace=True)
            class_ = ClassModel.get_all_class()
            name = []
            id = []
            for i in class_:
                name.append(i.class_name)
                id.append(i.id)

            student.replace(to_replace=['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'KG IInd', 'KG Ist', 'Nursery'],
                            value=['Class I', 'Class II', 'Class III', 'Class IV', 'Class V', 'Class VI', 'Class VII', 'Class VIII', 'Class IX', 'Class X', 'Sr KG', 'Jr KG', 'Nursery'], inplace=True)
            student.replace(to_replace=name,
                            value=id, inplace=True)

            student.replace(to_replace=['NO', 'YES', 'no', 'yes', 'No', 'Yes'],
                            value=[False, True, False, True, False, True], inplace=True)

            student['scolar_no'] = student['scolar_no'].astype(str)
            student['RTE'] = student['RTE'].astype(bool)
            student['Full_paid'] = student['Full_paid'].astype(bool)
            student_json = student.to_dict(orient="records")

            studentfee = data[['Scholar No', 'installment1',
                               'installment2', 'installment3']]
            studentfee.rename(
                columns={"Scholar No": "student_id_id"}, inplace=True)
            # studentfee.replace(to_replace =['PAID','UNPAID'],value=[True,False],inplace = True)
            # studentfee.fillna(value=None,inplace = True)
            ids = []
            for i in range(0, len(studentfee.index)):
                ids.append(str(uuid.uuid4()))
            studentfee['id'] = ids
            # change studentfee type of columns
            months = ('installment1', 'installment2', 'installment3')
            for month in months:
                studentfee[month] = studentfee[month].astype(str)
            studentfee['student_id_id'] = studentfee['student_id_id'].astype(
                str)
            studentfee_json = studentfee.to_dict(orient="records")
            os.remove(tmp_file)

            userdb.Student.insert(student_json)
            userdb.StudentFees.insert(studentfee_json)

            # client = pymongo.MongoClient()
            # db = client[ "testdb2" ]
            # db1 = client['testdb2']
            # Student = db[ "Student" ]
            # StudentFee = db1['StudentFees']
            # for i in student_json:
            #   Student.insert_one(i)
            # for i in studentfee_json:
            #     StudentFee.insert_one(i)
            return redirect('studentview')
    return redirect('login')


def response_messages(response_message, response_data, response_status):

    final_response_message = {
        "status": response_status,
        "message": response_message,
        "result": response_data,

    }
    return final_response_message


def download_sample(request, sheet):
    if request.session.get('admin'):
        if sheet == "Student":
            return FileResponse(open(fr"media/sample_templates/BlueBird_sample_data.xlsx", 'rb'), content_type='application/xlsx')
    return redirect('login')


class IndexPage(View):
    def get(self, request):
        if request.session.get('admin'):
            return render(request, 'admintemp/index.html')
        return redirect('login')


# class StudentView(View):

#     def get(self, request):
#         try:
#             #token = request.META['HTTP_AUTHORIZATION']
#             #userId = dectoken(token)
#             userId = "123"
#             if userId:
#                 data = []
#                 get_data = userdb.Student.find()
#                 total = get_data.count()
#                 for i in get_data:
#                     print("scolar_no", i['scolar_no'])
#                     i['id'] = str(i['_id'])
#                     del i['_id']
#                     data.append(i)

#                 return JsonResponse({"total": total, "message": "success", "result": data, "status": 200})
#         except Exception as e:
#             print(e)
#             message = {
#                 "message": "Internal server error {}".format(e)
#             }
#             error_message = response_messages('failed', message, 500)
#             return JsonResponse(error_message, safe=False, status=500)


class StudentView(View):
    def get(self, request, scholar=None, view=None):
        if request.session.get('admin'):
            if scholar and view:
                student = Student.get_student_by_scholar_no(scholar)
                studentfee = StudentFees.get_student_remaining_month_by_stuid(
                    scholar)
                class_ = ClassModel.get_all_class()
                return render(request, 'admintemp/student_details.html', {'student': student, 'classes': class_, "studentfee": studentfee})
            elif scholar:
                student = Student.get_student_by_scholar_no(scholar)
                studentfee = StudentFees.get_student_remaining_month_by_stuid(
                    scholar)
                class_ = ClassModel.get_all_class()
                return render(request, 'admintemp/student_update.html', {'student': student, 'classes': class_, "studentfee": studentfee})
            else:
                student = Student.get_all_student()
                paginator = Paginator(student, 50)  # Show 50 student per page.
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                class_ = ClassModel.get_all_class()
                return render(request, 'admintemp/student.html', {'students': page_obj, 'classes': class_})
        return redirect('login')

    def post(self, request):
        if request.session.get('admin'):
            scholar_no = request.POST.get('scholar_no')
            student_name = request.POST.get('student_name')
            father_name = request.POST.get('father_name')
            mother_name = request.POST.get('mother_name')
            class_id = request.POST.get('class')
            class_id = ClassModel.objects.filter(id=class_id).first()
            RTE = True if request.POST.get('RTE') else False
            full_paid = True if request.POST.get('full_paid') else False
            amount = request.POST.get('amount')
            if full_paid:
                stufeesStru = FeesStructure.get_fees_structure_by_class_id(
                    class_id)
                installment1 = stufeesStru.installment1
                installment2 = stufeesStru.installment2
                installment3 = stufeesStru.installment3
            else:
                installment1 = float(request.POST.get(
                    'installment1')) if request.POST.get('installment1') else None
                installment2 = float(request.POST.get(
                    'installment2')) if request.POST.get('installment2') else None
                installment3 = float(request.POST.get(
                    'installment3')) if request.POST.get('installment3') else None

            if request.POST.get('btn') == "post":
                student = Student(
                    scolar_no=scholar_no,
                    student_name=student_name,
                    father_name=father_name,
                    mother_name=mother_name,
                    class_id=class_id,
                    RTE=RTE,
                    Full_paid=full_paid
                )
                student.save()

                student = Student.objects.get(scolar_no=scholar_no)
                studentfee = StudentFees(
                    student_id=student, installment1=installment1, installment2=installment2, installment3=installment3,
                )
                studentfee.save()

                return redirect('studentview')

            elif request.POST.get('btn') == 'put':
                student = Student.objects.get(scolar_no=scholar_no)
                student.student_name = student_name
                student.father_name = father_name
                student.mother_name = mother_name
                student.class_id = class_id
                student.RTE = RTE
                student.Full_paid = full_paid
                student.save()
                studentfee = StudentFees.objects.get(student_id=scholar_no)
                studentfee.installment1 = installment1
                studentfee.installment2 = installment2
                studentfee.installment3 = installment3
                studentfee.save()
                if amount != "0":
                    type = request.POST.get('type')
                    if type == "cheque":
                        discription = request.POST.get('cheque_no')
                    elif type == "DD":
                        discription = request.POST.get('DD_no')
                    elif type == "cash":
                        discription = {
                            "100": request.POST.get('100_cash_no'),
                            "200": request.POST.get('200_cash_no'),
                            "500": request.POST.get('500_cash_no'),
                            "2000": request.POST.get('2000_cash_no')}
                    elif type == "Online":
                        discription = request.POST.get('Online_no')
                    pay = PaymentMethod(
                        scolarno=student,
                        amount=amount,
                        type=type,
                        discription=discription
                    )
                    pay.save()
                return redirect('studentview')
            elif request.POST.get('btn') == 'search':
                student = Student.objects.filter(scolar_no=scholar_no)
                class_ = ClassModel.get_all_class()
                return render(request, 'admintemp/student.html', {'students': student, 'classes': class_})
            elif request.POST.get('btn') == 'delete':
                # delete student
                student = Student.objects.get(scolar_no=scholar_no)
                student.delete()
                return redirect('studentview')
        return redirect('login')


class FeesStructureView(View):

    def get(self, request, class_id=None):
        if request.session.get('admin'):
            if class_id:
                feestruct = FeesStructure.get_fees_structure_by_class_id(
                    class_id)
                class_ = ClassModel.get_all_class()
                return render(request, 'admintemp/feestructure_update.html', {'feestructure': feestruct, "classes": class_})
            else:
                feestruct = FeesStructure.get_all_fees_structure()
                class_ = ClassModel.get_all_class()
                return render(request, 'admintemp/feestructure.html', {'feestructure': feestruct, "classes": class_})
        return redirect('login')

    def post(self, request):
        if request.session.get('admin'):
            class_id = request.POST.get('class')
            class_id = ClassModel.objects.filter(id=class_id).first()
            installment1 = float(request.POST.get('installment1')) if request.POST.get(
                'installment1') != '' else None
            installment2 = float(request.POST.get('installment2')) if request.POST.get(
                'installment2') != '' else None
            installment3 = float(request.POST.get('installment3')) if request.POST.get(
                'installment3') != '' else None
            totalamount = float(request.POST.get('totalamount')) if request.POST.get(
                'totalamount') != '' else None
            if request.POST.get('btn') == "post":
                feestruct = FeesStructure(
                    class_id=class_id, installment1=installment1, installment2=installment2, installment3=installment3,
                )
                feestruct.save()
            elif request.POST.get('btn') == 'put':
                feestruct = FeesStructure.objects.get(class_id=class_id)
                feestruct.class_id = class_id
                feestruct.installment1 = installment1
                feestruct.installment2 = installment2
                feestruct.installment3 = installment3
                feestruct.save()
            elif request.POST.get('btn') == 'delete':
                feestruct = FeesStructure.objects.get(class_id=class_id)
                feestruct.delete()

            return redirect('feestructure')
        return redirect('login')


class SchoolView(View):
    def get(self, request, school_id=None):
        if request.session.get('admin'):
            if school_id:
                school = School.get_school_by_id(school_id)
                return render(request, 'admintemp/school_update.html', {'school': school})
            else:
                school = School.get_all_school()
                return render(request, 'admintemp/school.html', {'school': school})
        return redirect('login')

    def post(self, request):
        if request.session.get('admin'):
            school_name = request.POST.get('school_name')
            school_discription = request.POST.get('school_discription')

            # school_logo,image_public_id = services.cloudinary_upload_media(image = request.FILES.get('school_logo'),imageDir="media/bluebird/school")
            if request.POST.get('btn') == "post":
                school_logo = request.FILES['school_logo']
                school = School(
                    school_name=school_name,
                    school_discription=school_discription,
                    school_logo=school_logo,
                    # image_public_id = image_public_id
                )
                school.save()
            elif request.POST.get('btn') == 'put':
                school_logo = request.FILES['school_logo'] if request.FILES else None
                school_id = request.POST.get('school_id')
                school = School.objects.get(id=school_id)
                school.school_name = school_name
                school.school_discription = school_discription
                if school_logo:
                    school.school_logo = school_logo
                school.save()

            elif request.POST.get('btn') == 'delete':
                school_id = request.POST.get('school_id')
                school = School.objects.get(id=school_id)
                school.delete()
            return redirect('school')
        return redirect('login')


class ClassView(View):
    def get(self, request, class_id=None):
        if request.session.get('admin'):
            if class_id:
                class_ = ClassModel.objects.get(id=class_id)
                school = School.get_all_school()
                return render(request, 'admintemp/class_update.html', {'school': school, 'classes': class_})
            else:
                class_ = ClassModel.get_all_class()
                schools = School.get_all_school()
                return render(request, 'admintemp/class.html', {'classes': class_, "school": schools})
        return redirect('login')

    def post(self, request):
        if request.session.get('admin'):
            school_id, _ = request.POST.get('school').split(',')
            school_id = School.objects.filter(id=school_id).first()
            if request.POST.get('btn') == "post":
                class_name = request.POST.get('class_name')
                class_ = ClassModel(
                    class_name=class_name,
                    school_id=school_id
                )
                class_.save()
            elif request.POST.get('btn') == 'put':
                class_id = request.POST.get('class_id')
                class_name = request.POST.get('class_name')
                class_ = ClassModel.objects.get(id=class_id)
                class_.class_name = class_name
                class_.school_id = school_id
                class_.save()
            elif request.POST.get('btn') == 'delete':
                class_id = request.POST.get('class_id')
                class_ = ClassModel.objects.get(id=class_id)
                class_.delete()
            return redirect('class')
        return redirect('login')


class LateFeeView(View):
    def get(self, request, id=None):
        if request.session.get('admin'):
            if id:
                latefee = LateFees.objects.get(id=id)
                return render(request, 'admintemp/latefee_update.html', {'latefee': latefee})
            latefee = LateFees.objects.all()
            return render(request, 'admintemp/latefee.html', {'latefee': latefee})
        return redirect('login')

    def post(self, request):
        if request.session.get('admin'):
            type = request.POST.get('type')
            fees = request.POST.get('fees')
            status = request.POST.get('status')
            lastdate = request.POST.get('lastdate')
            installment = request.POST.get('installment')
            if request.POST.get('btn') == "post":
                latefee = LateFees(
                    type=type,
                    fees=fees,
                    status=status,
                    lastdate=lastdate,
                    installment=installment
                )
                latefee.save()
            elif request.POST.get('btn') == 'put':
                id = request.POST.get('id')
                latefee = LateFees.objects.get(id=id)
                latefee.type = type
                latefee.fees = fees
                latefee.status = status
                latefee.lastdate = lastdate
                latefee.installment = installment
                latefee.save()
            elif request.POST.get('btn') == 'delete':
                id = request.POST.get('id')
                latefee = LateFees.objects.get(id=id)
                latefee.delete()
            return redirect('latefee')
        return redirect('login')
