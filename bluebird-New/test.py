import pandas as pd
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bluebird.settings")
from bluebird.settings import DATABASES
import django
django.setup()
from feesapp.models import *
import sqlite3
con = sqlite3.connect('db.sqlite3')
cur = con.cursor()
from feesapp.models import *

df = pd.read_excel(r"/home/djtechnologies/DJ_DRF/feeszone22Dec/bluebird/feesstructure.xls")
# df.to_sql(tablename, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None)
df.to_sql(FeesStructure,cur , if_exists='fail')

# df = pd.read_excel(r"/home/djtechnologies/DJ_DRF/feeszone22Dec/bluebird/feesstructure.ods")
# # df.to_sql(tablename, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None)
# df.to_sql(FeesStructure,DATABASES)