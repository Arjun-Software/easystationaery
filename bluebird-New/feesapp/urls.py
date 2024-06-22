from django.urls import path
from . import views
from . admin_view import *

urlpatterns = [
    path('paytm_success/',views.paytm_success,name='paytm_success'),
    path('paymentfail/<str:context>',views.paymentfail,name='paymentfail'),
    path('paymentsuccess/<str:context>',views.paymentsuccess,name='paymentsuccess'),
    path('',views.Enroll.as_view(),name='Index'),
    path('studentregistration/',views.StudentRegistration.as_view(),name='studentregistration'),
    path('paymentsuccess/<str:context>/<str:order>',views.paymentsuccess,name='paymentsuccess'),
    path("paymentpdf/<str:order>", views.paymentpdf, name="paymentpdf"),
    path("getpayment/<str:order>",views.getpayment, name= "getpayment"),
    path("downloadreceipt/",views.downloadreceipt, name= "downloadreceipt"), 
    # admin urls
    path('panel/',IndexPage.as_view(),name = 'indexpage'),    
    path('panel/student/',StudentView.as_view(),name = 'studentview'),
    path('panel/student/<str:scholar>',StudentView.as_view(),name = 'studentscolar'),

    path('panel/feestructure/',FeesStructureView.as_view(),name = 'feestructure'),
    path('panel/feestructure/<str:class_id>',FeesStructureView.as_view(),name = 'feestructureclass'),

    path('panel/class/',ClassView.as_view(),name = 'class'),
    path('panel/class/<str:class_id>',ClassView.as_view(),name = 'class-class'),

    path('panel/school/',SchoolView.as_view(),name = 'school'),
    path('panel/school/<str:school_id>',SchoolView.as_view(),name = 'school-school'),
    path('panel/latefee/',LateFeeView.as_view(),name = 'latefee'),
    path('panel/latefee/<str:id>',LateFeeView.as_view(),name = 'latefee'),
    path('panel/data_upload/<str:sheet>',data_upload, name = 'dataupload'),
    path('panel/download_sample/<str:sheet>',download_sample,name = 'downloadsample'),
    path('panel/login/',LoginView.as_view(),name='login'),
    path('logout/', logout, name='logout'),
    path("checkgetpayment/",views.checkgetpayment),
    path("updatepaymentstatus/<str:scholar>",views.update_payment_status, name= "updatepaymentstatus"),

    path("CheckEnroll/",views.CheckEnroll.as_view(),name='CheckEnroll'),
    path("trAPI/",views.trAPI.as_view(),name='trAPI'),

    path("checkTwoMonthFee/", views.checkTwoMonthFee, name = "checkTwoMonthFee"),
]
