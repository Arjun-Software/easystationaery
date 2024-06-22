from django.db import models
import uuid
from django.utils.timezone import now
from datetime import datetime
# Create your models here.


class School(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4,
                          editable=False, max_length=255)
    school_name = models.CharField(max_length=500, null=True, blank=True)
    school_discription = models.CharField(
        max_length=500, null=True, blank=True)
    school_logo = models.ImageField(upload_to='school')

    class Meta:
        db_table = 'School'

    def __str__(self):
        return self.school_name

    @staticmethod
    def get_all_school():
        return School.objects.all()

    @staticmethod
    def get_school_by_id(id):
        if id:
            return School.objects.filter(id=id).first()
        else:
            return School.get_all_school()


class ClassModel(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4,
                          editable=False, max_length=255)
    class_name = models.CharField(max_length=500, null=True, blank=True)
    school_id = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True, blank=True, related_name='school_id')

    def __str__(self):
        return self.class_name

    class Meta:
        db_table = 'ClassModel'

    @staticmethod
    def get_all_class():
        return ClassModel.objects.all().order_by('class_name')

    @staticmethod
    def get_class_by_id(id):
        if id:
            return ClassModel.objects.filter(id=id).first()
        else:
            return ClassModel.get_all_class()


class Student(models.Model):
    scolar_no = models.CharField(
        primary_key=True, editable=False, max_length=500)
    student_name = models.CharField(max_length=500, null=True, blank=True)
    father_name = models.CharField(max_length=500, null=True, blank=True)
    mother_name = models.CharField(max_length=500, null=True, blank=True)
    class_id = models.ForeignKey(
        ClassModel, on_delete=models.CASCADE, null=True, blank=True, related_name='classId')
    RTE = models.BooleanField(default=False)
    Full_paid = models.BooleanField(default=False)

    class Meta:
        db_table = 'Student'

    def __str__(self):
        return self.scolar_no

    @staticmethod
    def get_all_student():
        print("---===ppp--=-==l")
        return Student.objects.all()

    @staticmethod
    def get_student_by_scholar_no(id):
        if id:
            print("ididididiiidididd", id)
            return Student.objects.filter(scolar_no=id).first()
        else:
            return Student.get_all_student()


class StudentFees(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4,
                          editable=False, max_length=255)
    student_id = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=True, blank=True, related_name='student_id')
    installment1 = models.FloatField(null=True, blank=True,)
    installment2 = models.FloatField(null=True, blank=True,)
    installment3 = models.FloatField(null=True, blank=True,)

    # paidamount = models.FloatField(null=True, blank=True,)
    # totalamount = models.FloatField(null=True, blank=True,)

    class Meta:
        db_table = 'StudentFees'

    @staticmethod
    def get_all_student_fees():
        return StudentFees.objects.all()

    @staticmethod
    def get_student_fees_by_id(id):
        if id:
            return StudentFees.objects.filter(id=id).first()
        else:
            return StudentFees.get_all_student_fees()

    @staticmethod
    def get_student_remaining_month_by_stuid(id):
        if id:
            return StudentFees.objects.filter(student_id=id).first()
        else:
            return StudentFees.get_all_student_fees()


class FeesStructure(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4,
                          editable=False, max_length=255)
    class_id = models.ForeignKey(ClassModel, on_delete=models.CASCADE,
                                 null=True, blank=True, related_name='feestr_class_id')
    installment1 = models.FloatField(null=True, blank=True,)
    installment2 = models.FloatField(null=True, blank=True,)
    installment3 = models.FloatField(null=True, blank=True,)
    # totalamount = models.FloatField(null=True, blank=True,)

    class Meta:
        db_table = 'FeesStructure'

    @staticmethod
    def get_all_fees_structure():
        return FeesStructure.objects.all()

    @staticmethod
    def get_fees_structure_by_class_id(id):
        if id:
            return FeesStructure.objects.filter(class_id=id).first()
        else:
            return FeesStructure.get_all_fees_structure()

# class PaymentsStatus(models.Model):
#     id = models.CharField(primary_key=True , default=uuid.uuid4 , editable= False, max_length=255)
#     mid = models.CharField(max_length=500,null=True, blank=True)
#     txnToken = models.CharField(max_length=500,null=True, blank=True)
#     orderId = models.CharField(max_length=500,null=True, blank=True)
#     customerId = models.CharField(max_length=500,null=True, blank=True)
#     studentName = models.CharField(max_length=500,null=True, blank=True)
#     fatherName = models.CharField(max_length=500,null=True, blank=True)
#     motherName = models.CharField(max_length=500,null=True, blank=True)
#     className = models.CharField(max_length=500,null=True, blank=True)
#     scholar = models.CharField(max_length=500,null=True, blank=True)
#     amount = models.CharField(max_length=500,null=True, blank=True)
#     month = models.CharField(max_length=500,null=True, blank=True)
#     MercUnqRef = models.CharField(max_length=500,null=True, blank=True)
#     paymentStatus = models.BooleanField(default=False)
#     payment = models.CharField(max_length=500,null=True, blank=True, default="Unpaid")
#     createdOn = models.DateTimeField(default=datetime.now().timestamp())

#     class Meta:
#         db_table = 'payments'


class AdminUser(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4,
                          editable=False, max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField()
    password = models.CharField(max_length=500)
    admin = models.BooleanField(default=False)

    def register(self):
        self.save()

    @staticmethod
    def get_admin_user_by_email(email):
        try:
            return AdminUser.objects.get(email=email)
        except:
            return False

    def isExists(self):
        if AdminUser.objects.filter(email=self.email):
            return True

        return False

    class Meta:
        db_table = 'AdminUser'


class LateFees(models.Model):
    TYPE = (
        ('perday', 'perday',),
        ('percentage', 'percentage',),
        ('fixamount', 'fixamount',),
    )
    id = models.CharField(primary_key=True, default=uuid.uuid4,
                          editable=False, max_length=255)
    type = models.CharField(
        max_length=100, choices=TYPE, null=True, blank=True)
    fees = models.FloatField(max_length=15, null=True, blank=True)
    lastdate = models.DateField()
    installment = models.CharField(max_length=50, null=True, blank=True)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'LateFees'


class PaymentMethod(models.Model):
    TYPE = (
        ('cheque', 'cheque',),
        ('DD', 'DD',),
        ('cash', 'cash',),
    )
    id = models.CharField(primary_key=True, default=uuid.uuid4,
                          editable=False, max_length=255)
    scolarno = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=True, blank=True, related_name='scolarno')
    amount = models.FloatField(null=True, blank=True, default=False)
    type = models.CharField(
        max_length=100, choices=TYPE, null=True, blank=True)
    discription = models.CharField(max_length=255, null=True, blank=True)
    createdOn = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'PaymentMethod'
