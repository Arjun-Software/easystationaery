# import pandas as pd
# import sqlite3

# db_conn = sqlite3.connect("/home/djtechnologies/DJ_DRF/feeszone22Dec/bluebird/db.sqlite3")
# c = db_conn.cursor()

# df = pd.read_excel(r"/home/djtechnologies/Downloads/Blue Bird Fee Data new.xlsx")
# # df.to_sql(tablename, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None)
# df.to_sql("FeesStructure",c)

# # df.rename(columns={'oldName1': 'newName1', 'oldName2': 'newName2'}, inplace=True)
# # change data type of columns
# # df[df.val > 0.5]
# # data[data.class_id == "Nursery"]
# # elif sheet == "StudentFees":
#     #     data=pd.read_excel(tmp_file,sheet_name="StudentFees")
#     #     # rename columns
#     #     data.rename(columns={"Scholar no":"student_id_id"},inplace = True)
#     #     data.replace(to_replace =['PAID','UNPAID'],value=[True,False])
#     #     data.fillna(value=True,inplace = True)
#     #     ids = []
#     #     for i in range(0,len(data.index)):
#     #         ids.append(str(uuid.uuid4()))
#     #     data['id']=ids
#     #     # change data type of columns
#     #     months = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')
#     #     for month in months:
#     #         data[month] = data[month].astype(bool)
#     #     data['student_id_id'] = data['student_id_id'].astype(str)
#     #     data1=data.to_dict(orient="records")
#     #     print(data)
#     #     # userdb.StudentFees.insert(data1)
#     #     return HttpResponse(data)
    
#     # elif sheet == "FeesStructure":
#     #     data=pd.read_excel(r"/home/djtechnologies/Downloads/Blue Bird Fee Data new.xlsx",sheet_name="FeesStructure")
#     #     # change data type of columns
#     #     data1=data.to_dict(orient="records")
#     #     print(data)
#     #     return HttpResponse(data)
    
#     # elif sheet == "ClassModel":
#     #     data=pd.read_excel(r"/home/djtechnologies/Downloads/Blue Bird Fee Data new.xlsx",sheet_name="FeesStructure")


#     # def assigndata1(request):
#     #     a = userdb.Student.find()
#     #     for i in a :
#     #         id = str(i['_id'])
#     #         userdb.Student.update({"_id":ObjectId(id)},{"$set":{"scholar_no":str(i['scholar_no'])}})
#     # from pymongo import MongoClient
#     # from bson import ObjectId

#     # client1 = MongoClient(
#     # "mongodb+srv://DJTech:admin123@cluster0.vzcsg.mongodb.net/userDB?retryWrites=true&w=majority")
#     # userdb = client1.userDB
#     # a = userdb.Student.find()
#     # for i in a :
#     #     print(i)
#     #     id = str(i['_id'])
#     #     userdb.Student.update({"_id":ObjectId(id)},{"$set":{"scholar_no":str(i['scholar_no'])}})


from datetime import date
today = date.today()
latefees = 0
lastdate = 10
total = 1000
lateperday =100
if today.day >=lastdate:
    for i in range(today.day-lastdate):
        latefees +=lateperday
        print(i ,"-----", latefees)

# if today.day >=lastdate:
#     latefees = total + (total*10)/100
# print(latefees)



