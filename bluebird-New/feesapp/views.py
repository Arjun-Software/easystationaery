from django.http import HttpResponse
from bson.objectid import ObjectId
from django.shortcuts import render, redirect
from django.views import View
from .models import *
from bluebird.settings import PAYTM_MID, PAYTM_MKEY, userdb, admindb
from datetime import datetime
from django.conf import settings
import random
from django.views.decorators.csrf import csrf_exempt
from . import PaytmChecksum
import json
import requests
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView

BaseUrl = "https://bluebird.feeszone.com/"
BASE_URL = "https://bluebird.feeszone.com/"
marchant_prod_url = "https://securegw.paytm.in/theia/api/v1/initiateTransaction?mid={0}&orderId={1}"
marchant_stag_url = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid={0}&orderId={1}"
IS_AUTH_SERVER = "1"
AUTH_SERVER = "http://testingservers.ddns.net:8000/"


@csrf_exempt
def paytm_success(request):
    form = request.POST
    para_dict = {}
    orderId = request.POST.get('ORDERID')
    payment_mode = request.POST.get('PAYMENTMODE')
    transaction_id = request.POST.get('TXNID')
    Bank_transaction_id = request.POST.get('BANKTXNID')
    transaction_date = request.POST.get('TXNDATE')
    sellcourse_obj = request.POST.get('ORDERID')
    res_msg = request.POST.get('RESPMSG')
    print('-----------', res_msg, '------------------', form)
    context = {'resmsg': res_msg}

    print("****   hello")
    if res_msg != 'Txn Success':
        print("****   4444")
        return redirect('paymentfail', context=res_msg)

    for i in form:
        para_dict[i] = form[i]

    checksum = request.POST.get('CHECKSUMHASH')
    isValidChecksum = PaytmChecksum.verifySignature(
        para_dict, PAYTM_MKEY, checksum)
    print('--------', isValidChecksum)
    if isValidChecksum:
        print("Checksum Matched")
    else:
        return redirect('paymentfail')

    # # update payment month status in StudentFees
    studata = {}
    pdData = userdb.bluebirdpayments.find({'orderId': orderId})
    for i in pdData:
        studata['months'] = i['month']
        studata['custId'] = i['customerId']
    class_id = Student.get_student_by_scholar_no(studata['custId']).class_id
    feesStruct = FeesStructure.get_fees_structure_by_class_id(
        class_id).__dict__
    month = studata['months'].replace(' ', '').replace(
        '-2022', '').replace('-2023', '').split(',')
    fees = []
    for mon in month:
        if mon in feesStruct:
            fees.append(feesStruct[mon])
    update = {month[mon]: fees[mon] for mon in range(len(month))}
    userdb.StudentFees.update_one(
        {'student_id_id': studata['custId']}, {"$set": update})
    userdb.bluebirdpayments.update_one({'orderId': orderId}, {"$set": {"paymentStatus": True,
                                                                       "payment": "Paid",
                                                                       "createdOn": datetime.now().timestamp()}})

    return redirect('paymentsuccess', context=res_msg, order=orderId)


def paymentfail(request, context):
    return render(request, "bluebird/paymentfail.html", {"context": context})


def paymentsuccess(request, context, order):

    return render(request, "bluebird/paymentsuccess.html", {"context": context, 'order': order})


class Enroll(View):
    def get(self, request):
        if type(request.GET.get('id')) == type("454"):
            return render(request, 'bluebird/home.html', {"message": "Pay Earlier Month Fees First"})
        else:
            return render(request, 'bluebird/home.html')

    def post(self, request):
        enrollment = request.POST.get('enrollmentNo')
        if enrollment:
            # requests.get(f"https://bluebird.feeszone.com/updatepaymentstatus/{enrollment}")
            studata = Student.get_student_by_scholar_no(enrollment)
            if studata and int(studata.RTE) != True:
                stufeesStru = FeesStructure.get_fees_structure_by_class_id(
                    uuid.UUID(studata.class_id_id))
                remaining_month = StudentFees.get_student_remaining_month_by_stuid(
                    studata.scolar_no)
                latefees = LateFees.objects.all()
                latefee = {}
                for late in latefees:
                    print("NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN")
                    if late.status == True:
                        latefee = late
                        break
                return render(request, 'bluebird/testform.html', {"student": studata, "feesStruct": stufeesStru, "remMon": remaining_month, 'latefee': latefee})
            elif studata and int(studata.RTE) == True:
                return render(request, 'bluebird/testform.html', {"student": studata})
            else:
                return render(request, 'bluebird/home.html', {'message': "Scholar No. doesn't exists"})
        else:
            return render(request, 'bluebird/home.html', {'message': "Enter your Scholar Number"})


def checkTwoMonthFee(request):
    rmlist = []
    a = userdb.Student.find({'RTE': False})
    for i in a:
        rM = StudentFees.get_student_remaining_month_by_stuid(i['scolar_no'])
        if (rM.Feb == "nan" or rM.Feb is None) and (rM.Mar == "nan" or rM.Mar is None):
            rmlist.append((i['scolar_no']+"  "))
    return HttpResponse(rmlist)


# class Downloadreceipt(View):
def downloadreceipt(request):

    if request.method == 'POST':
        enrollment = request.POST.get('enrollmentNo')
        studata = Student.get_student_by_scholar_no(enrollment)
        if studata:
            try:
                a = requests.get(
                    f"https://bluebird.feeszone.com/updatepaymentstatus/{enrollment}")
                a = a.json()
                # AllPaymentLink.html
                return render(request, 'bluebird/AllPaymentLink.html', {'message': a['receipts']})
                # return HttpResponse(a['receipts'])
            except Exception as e:
                return redirect(BaseUrl+"downloadreceipt/", {'message': "Scholar No. doesn't exists"})
        else:
            return redirect(BaseUrl+"downloadreceipt/", {'message': "Scholar No. doesn't exists"})

    else:
        return render(request, 'bluebird/downloadreceipt.html')


class StudentRegistration(View):
    def post(self, request):
        scholar = request.POST.get('scholar')
        name = request.POST.get('name')
        father_name = request.POST.get('Father Name')
        mother_name = request.POST.get('Mother Name')
        class_ = request.POST.get('class')
        amount = request.POST.get('total')
        remMonth = request.POST.get('month').split(',')
        print(remMonth)
        month = []

        # Developed By DJTechnologies(Shantanu)
        rmlist = []
        studata = Student.get_student_by_scholar_no(scholar)
        if studata and int(studata.RTE) != True:
            rM = StudentFees.get_student_remaining_month_by_stuid(
                studata.scolar_no)
        if rM.installment1 == "nan" or rM.installment1 is None:
            rmlist.append('installment1')
        if rM.installment2 == "nan" or rM.installment2 is None:
            rmlist.append('installment2')
        if rM.installment3 == "nan" or rM.installment3 is None:
            rmlist.append("installment3")

        for i in range(0, len(remMonth)):
            if remMonth[i] == rmlist[i]:
                print("hahhahahhahahahhahahahah")
                print("ok")
            else:
                return redirect(BaseUrl+f"?id={scholar}", {'message': "Scholar No. doesn't exists"})

        year_2022 = ('installment1', 'installment2')
        year_2023 = ('installment3',)

        for m in remMonth:
            if m in year_2022:
                month.append(f"{m}-2022")
            elif m in year_2023:
                month.append(f"{m}-2023")
        Data = {
            'studentName': name,
            'fatherName': father_name,
            'motherName': mother_name,
            'className': class_,
            'scholar': scholar,
            'amount': amount,
            'month': month
        }
        orderId = Data['studentName'].strip()+"_" + str(Data['scholar']
                                                        ).replace('/', '_')+"_"+str(random.randint(1000, 9999))
        orderId = orderId.replace(" ", "")
        orderId = orderId.replace(".", "")
        cust_id = Data['scholar']
        Data['createdOn'] = datetime.now().timestamp()
        custName = Data['studentName']
        paytmParams = dict()
        createdOn = Data['createdOn']
        MercUnqRef = custName+"_"+Data['scholar']+"_"+Data['className']
        MercUnqRef = MercUnqRef.replace(" ", "").replace(".", "")
        paytmParams["body"] = {
            "requestType": "Payment",
            "mid": PAYTM_MID,
            "websiteName": "WEBSTAGING",
            "orderId": orderId,

            "callbackUrl": BaseUrl+"paytm_success/",
            "txnAmount": {
                "value": amount,
                "currency": "INR",
            },
            "userInfo": {
                "custId": Data['scholar'],

            },
            "extendInfo": {"mercUnqRef": MercUnqRef}
        }

        # Generate checksum by parameters we have in body
        # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
        checksum = PaytmChecksum.generateSignature(
            json.dumps(paytmParams["body"]), PAYTM_MKEY)

        paytmParams["head"] = {
            "signature":  checksum
        }

        post_data = json.dumps(paytmParams)
        print('-------^^^--------', post_data)
        # for Staging
        #url = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid={0}&orderId={1}".format(PAYTM_MID,orderId)

        # for Production
        print("ffff")
        url = "https://securegw.paytm.in/theia/api/v1/initiateTransaction?mid={0}&orderId={1}".format(
            PAYTM_MID, orderId)

        response = requests.post(url, data=post_data, headers={
                                 "Content-type": "application/json"}).json()
        print('------', response)

        admindb.bluebirdstudent.insert_one(Data)

        payment_page = {'mid': PAYTM_MID,
                        'txnToken': response['body']['txnToken'],
                        'orderId': orderId,
                        'customerId': Data['scholar'],
                        # 'feesType':feeDetail,
                        'studentName': name,
                        'fatherName': father_name,
                        'motherName': mother_name,
                        'className': class_,
                        'scholar': scholar,
                        'amount': amount,
                        'month': ', '.join(month),
                        'MercUnqRef': MercUnqRef,
                        'latefee': request.POST.get('latefee'),
                        'totalamount': request.POST.get('totalamount')
                        }
        userdb.bluebirdpayments.insert_one(payment_page)
        print('---^^^^^----', payment_page)

        return render(request, 'bluebird/recipt.html', payment_page)


def paymentpdf(request, order):
    # print(order)
    pdData = userdb.bluebirdpayments.find({'orderId': order})

    for i in pdData:
        print(i)
        payDate = i['createdOn']
        custId = i['customerId']
        orderId = i['orderId']
        months = i['month']
        b = i["amount"]
        i['payDate'] = datetime.fromtimestamp(payDate)
        i['payDate'] = datetime.strftime(i['payDate'], "%d-%m-%Y")
    #class_id = Student.get_student_by_scholar_no(custId).class_id
    #feesStruct = FeesStructure.get_fees_structure_by_class_id(class_id).__dict__
    #month = months.replace('-2022','').replace('-2023','').replace(" ", "").split(',')
    #fees = []
    # for mon in month:
    #    if mon in feesStruct:
    #        fees.append(feesStruct[mon])
    #update = {month[mon]: fees[mon] for mon in range(len(month))}
    # userdb.StudentFees.update_one({'student_id_id':custId},{"$set":update})
    customer = admindb.bluebirdstudent.find({"enrollmentNo": custId})

    for i in customer:
        print(i)
        del i['_id']
        i['custId'] = custId
        i["amount"] = b
        i["month"] = months

    i['transactionId'] = orderId
    print(i)
    return render(request, "bluebird/pdf.html", i)


def paymentpdf1(request, order):
    # print(order)
    pdData = userdb.bluebirdpayments.find({'orderId': order})

    for i in pdData:
        print(i)
        payDate = i['createdOn']
        custId = i['customerId']
        orderId = i['orderId']
        months = i['month']
        b = i["amount"]
        i['payDate'] = datetime.fromtimestamp(payDate)
        i['payDate'] = datetime.strftime(i['payDate'], "%d-%m-%Y")
    a = userdb.StudentFees.count({'student_id_id': custId})
    print(a, "le chala count", custId)
    userdb.StudentFees.update_one({'student_id_id': custId}, {"$set": dict.fromkeys(
        months.replace('-2022', '').replace('-2023', '').split(','), 1)})
    customer = admindb.bluebirdstudent.find({"enrollmentNo": custId})

    for i in customer:
        print(i)
        del i['_id']
    i['custId'] = custId
    i["amount"] = b
    i["month"] = months

    i['transactionId'] = orderId
    print(i)
    return render(request, "bluebird/pdf.html", i)


@csrf_exempt
def getpayment(request, order):
    #order = request.GET['order']
    paytmParams = dict()

    # body parameters
    paytmParams["body"] = {

        # Find your MID in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
        "mid": PAYTM_MID,

        # Enter your order id which needs to be check status for
        "orderId": order,
    }

    # Generate checksum by parameters we have in body
    # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
    checksum = PaytmChecksum.generateSignature(
        json.dumps(paytmParams["body"]), PAYTM_MKEY)

    # head parameters
    paytmParams["head"] = {

        # put generated checksum value here
        "signature": checksum
    }

    # prepare JSON string for request
    post_data = json.dumps(paytmParams)

    # for Staging
    # url = "https://securegw-stage.paytm.in/v3/order/status"
    url = "https://securegw.paytm.in/v3/order/status"

    # for Production
    # url = "https://securegw.paytm.in/v3/order/status"

    response = requests.post(url, data=post_data, headers={
                             "Content-type": "application/json"}).json()
    return JsonResponse(response, safe=False, status=200)


@csrf_exempt
def update_payment_status(request, scholar):
    import time
    import datetime
    payments = list(userdb.bluebirdpayments.find({'scholar': scholar}))
    order_ids = {}
    if len(payments) > 0:
        for data in payments:
            response = requests.post(
                f"https://bluebird.feeszone.com/getpayment/{data['orderId']}")
            print("111111111111111111111111111111", response,
                  f"https://bluebird.feeszone.com/getpayment/{data['orderId']}")
            response = eval(response.text)
            print("SSSSSSSSSSSSSSSSSSSSS", response)
            try:
                if response["body"]["resultInfo"]["resultStatus"] == "TXN_SUCCESS":
                    date = response["body"]["txnDate"].split(".")[0]
                    order_ids[data['orderId']] = datetime.datetime.timestamp(
                        datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S'))
            except:
                continue
        try:
            receipt = []
            for order_id, timestamp in order_ids.items():
                studata = {}
                pdData = userdb.bluebirdpayments.find({'orderId': order_id})
                for i in pdData:
                    studata['months'] = i['month']
                    studata['custId'] = i['customerId']
                class_id = Student.get_student_by_scholar_no(
                    studata['custId']).class_id
                feesStruct = FeesStructure.get_fees_structure_by_class_id(
                    class_id).__dict__
                month = studata['months'].replace(' ', '').replace(
                    '-2022', '').replace('-2023', '').split(',')
                fees = []
                for mon in month:
                    if mon in feesStruct:
                        fees.append(feesStruct[mon])
                update = {month[mon]: fees[mon] for mon in range(len(month))}
                userdb.StudentFees.update_one(
                    {'student_id_id': studata['custId']}, {"$set": update})

                userdb.bluebirdpayments.update_one({'orderId': order_id}, {"$set": {"paymentStatus": True,
                                                                                    "payment": "Paid",
                                                                                    "createdOn": timestamp}})
                receipt.append(
                    f"https://bluebird.feeszone.com/paymentpdf/{order_id}")

            return JsonResponse({"receipts": receipt}, safe=False, status=200)
        except:
            print("no order id")
            return JsonResponse({"status": "no order id found"}, safe=False, status=200)
    return JsonResponse({"status": "scholar no not fount in online payments"}, safe=False, status=200)


@csrf_exempt
def checkgetpayment(request):
    order = request.GET['order']
    paytmParams = dict()

    # body parameters
    paytmParams["body"] = {

        # Find your MID in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
        "mid": PAYTM_MID,

        # Enter your order id which needs to be check status for
        "orderId": order,
    }

    # Generate checksum by parameters we have in body
    # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
    checksum = PaytmChecksum.generateSignature(
        json.dumps(paytmParams["body"]), PAYTM_MKEY)

    # head parameters
    paytmParams["head"] = {

        # put generated checksum value here
        "signature": checksum
    }

    # prepare JSON string for request
    post_data = json.dumps(paytmParams)

    # for Staging
    # url = "https://securegw-stage.paytm.in/v3/order/status"
    url = "https://securegw.paytm.in/v3/order/status"

    # for Production
    # url = "https://securegw.paytm.in/v3/order/status"

    response = requests.post(url, data=post_data, headers={
                             "Content-type": "application/json"}).json()
    return JsonResponse(response, safe=False, status=200)


class CheckEnroll(APIView):

    def get(self, request):
        enrollment = request.GET.get('enrollmentNo')
        if enrollment:
            print("NNNNNNNNNNNNNNNNNNNNNNNNNNNn")
            # requests.get(f"https://bluebird.feeszone.com/updatepaymentstatus/{enrollment}")
            studata = Student.get_student_by_scholar_no(enrollment)
            if studata and int(studata.RTE) != True:
                stufeesStru = FeesStructure.get_fees_structure_by_class_id(
                    uuid.UUID(studata.class_id_id))
                remaining_month = StudentFees.get_student_remaining_month_by_stuid(
                    studata.scolar_no)
                latefees = LateFees.objects.all()
                latefee = {}
                for late in latefees:
                    if late.status == True:
                        latefee = late
                        break
                data = {"installment1": remaining_month.installment1, "installment2": remaining_month.installment2,
                        "installment3": remaining_month.installment3, }
                return JsonResponse(data, safe=False, status=200)
            elif studata and int(studata.RTE) == True:
                return JsonResponse({"student": studata}, safe=False, status=200)
            else:
                return JsonResponse({'message': "Scholar No. doesn't exists"}, safe=False, status=200)
        else:
            return JsonResponse({'message': "Enter your Scholar Number"}, safe=False, status=200)



class trAPI1(APIView):
    def get(self,request):

        data = userdb.Student.find()
        
        sl=[]
        day=[]
        count=0
        for i in data:
            if i['Full_paid'] == False:
                get_fee= userdb.bluebirdpayments.find({"customerId":i['scolar_no']})
                import datetime

                for j in get_fee:
                    sl.append(j)
                    # print("all data getting =========",j)
                    if 'paymentStatus' in j:
                        dt= datetime.date.fromtimestamp(j['createdOn'])
                        j['createdOn']=datetime.date.fromtimestamp(j['createdOn'])
                        if dt.year == 2023 and dt.month == 10 and dt.day > 10 :
                            # print("year =========",dt.year)
                            if j['paymentStatus'] == True:
                                
                                if j['customerId'] not in day:
                                    print("*******",dt.day ,dt.month,dt.year ,j['customerId'])
                                    day.append(j['customerId'])
                                # i['nid'] = str(['_id'])
                                # del j['_id']
                                # sl.append(j)
                                # print(".")
                                # if j['month'] == "installment1-2023, installment2-2023":
                                    # print("*****-----*****",j['createdOn'])
                                    # count+=1
                                    # get_fees= userdb.StudentFees.find({"student_id_id":j['customerId']})
                                    # for k in get_fees:
                                        
                                    #     print("---------all data getted-----------------",k)
                                        
                                    #     sl.append(k)
                                        
                                        # if k['installment1'] == "nan" or k['installment1'] == None:
                                        # h=userdb.StudentFees.find({"installment1":k['installment1']})
                                        # for l in h:
                                        #     print("llllllllllllll",l['installment1'],l['student_id_id'])
                                        # # userdb.StudentFees.update({"installment1":k['installment1']},{"$set":{"test":"yes"}})
                                        # # print("------------kkk----" , k['student_id_id'],k['installment1'])
                                        # # k['vid'] =  str(k['_id'])
                                        # # del k['_id']
                                        # # k['studentName']=j['studentName']
                                        # k['amount']=j['amount']
                                        # k['month']=j['month']
                                        # print("------",k)
                                        # # sl.append(k)

                    # return JsonResponse({"result":sl})    
        print("***********--------",day)
        return JsonResponse({'students': day})



class trAPI(APIView):
    def get(self,request):
        day=[]
        data=['3655', '3676', '3718', '3651', '3664', '3621', '3624', '3626', '3632', '3643', '3667', '3615', '3139', '3220', '3196', '3160', '3562', '3311', '3199', '3206', '3185', '3414', '3453', '3277', '3130', '3188', '3526', '3470', '3173', '3149', '3491', '3147', '3417', '3226', '3450', '3415', '3434', '3175', '3449', '3444', '3183', '3485', '3194', '3174', '3210', '3204', '3489', '3156', '3555', '3472', '3312', '3168', '3255', '3104', '2933', '3126', '2926', '3239', '2942', '3524', '3235', '2956', '2987', '2954', '2918', '3304', '2973', '3240', '2947', '2960', '2951', '2949', '2943', '2978', '2945', '2924', '3550', '2929', '2953', '3044', '3243', '3500', '3254', '3037', '3569', '3420', '3098', '2715', '2829', '3021', '3253', '2780', '2720', '2723', '2747', '3297', '2792', '2777', '2812', '2764', '3289', '2778', '2907', '2798', '2837', '2803', '2779', '2824', '3001', '2820', '3537', '3521', '3298', '2742', '3295', '2838', '3322', '2446', '2489', '3462', '2459', '3333', '2443', '2449', '3424', '2434', '3338', '2425', '2381', '3336', '2382', '2625', '2478', '3038', '2391', '2524', '2467', '2466', '3411', '2860', '2422', '3463', '2854', '2495', '2405', '2499', '2397', '3024', '2432', '2512', '2438', '2510', '2396', '2209', '2190', '2102', '2204', '2531', '2193', '2192', '2189', '2226', '2145', '2232', '2593', '2188', '2222', '2236', '2120', '2151', '2162', '2225', '2144', '2133', '3008', '3423', '2229', '3358', '2178', '2179', '2154', '2119', '2228', '2113', '3348', '2167', '3031', '3361', '3438', '3546', '2186', '2338', '1813', '2250', '1835', '1872', '2030', '1790', '1826', '1766', '3369', '1854', '2252', '1780', '1777', '1840', '3389', '2539', '1903', '1768', '3367', '2870', '2039', '2347', '3374', '1839', '1775', '3442', '3495', '3441', '2871', '3443', '1652', '2291', '1717', '1665', '1678', '1913', '2257', '1594', '1615', '1657', '1621', '1589', '1578', '2290', '1625', '1610', '1932', '1622', '1611', '1644', '2253', '2258', '1613', '2259', '1595', '1635', '1633', '1658', '1596', '1669', '2254', '1631', '2879', '1563', '1936', '3393', '3397', '1406', '1383', '1475', '2284', '1938', '1390', '2264', '2706', '2261', '2622', '1450', '1384', '1404', '1393', '1467', '1459', '1544', '3045', '2638', '1289', '2567', '2561', '3399', '2560', '1223', '1291', '1943', '2275', '1359', '1248', '1270', '1239', '2563', '1326', '1296', '1256', '1249', '1273', '1231', '1364', '1247', '1234', '1957', '1288', '1215', '1956', '1292', '3015', '2589', '3568', '1125', '1103', '1537', '1203', '1110', '3492', '3432', '1121', '1127', '1073', '2704', '1113', '1689', '1981', '2888', '1973', '1703', '1131', '1087', '1138', '1075', '1204', '1195', '2633', '870', '945', '922', '865', '1985', '950', '952', '998', '2651', '916', '936', '1564', '944', '955', '967', '896', '890', '817', '3468', '3478', '2285', '2623', '2703', '755', '845', '796', '838', '833', '2268', '825', '821', '2276', '2892', '2463', '3752', '3686', '3744', '3719', '3730', '3735', '3753', '3106', '1863']
        for i in data:
            get_data=userdb.StudentFees.find({"student_id_id":i})
            if get_data.count()>1:
                print("_____if___",i)
            else:
                day.append(i)
                print("---",i) 
                
                
        return JsonResponse({'students': day})             
                      
                
    

