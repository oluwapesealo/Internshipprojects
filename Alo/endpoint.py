import json
from types import SimpleNamespace
import re
from sqlalchemy import create_engine
from sqlite3 import Cursor
from flask import Flask, request, redirect,jsonify
from flask_restful import Resource, Api
from flask_cors import CORS 
import pypyodbc as odbc 
import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os
import jwt
import datetime
# 'Driver={SQL Server};'
# 'Server=PESES-LAPTOP;'
# 'Database=wemabank;'
# 'Trusted_Connection=yes;'

app = Flask(__name__)
api = Api(app)
def tokenauthent(email,key):
        if 'tokenauth' in request.headers:
                token = request.headers['tokenauth']
                tokget=cursor.execute(os.getenv("tokenselect"),email)
                for ai in tokget:
                    pass
                if(bool(ai[0])==True):
                    try:
                        decodedtoken=jwt.decode(ai[0], key=key, algorithms=['HS256', ])
                        if(decodedtoken['expiration']<str(datetime.utcnow())):
                            return{"message":"token expired"}
                        else:
                            return {"token":ai[0],"message":"token is valid"}
                    except:
                        return{"message":"token verification failed"}
        else:
            return{"message":"token not included"}

SERVER='PESES-LAPTOP'
DATABASE='wemabank'
DRIVER='SQL Server Native Client 11.0'
USERNAME='sa'
PASSWORD='sa'
connect = pyodbc.connect('Driver={SQL Server};'
            'Server=PESES-LAPTOP;'
            'Database=wemabank;'
            'Trusted_Connection=yes;')
connection_string=f'mssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}'
# connection_string=f'mssql://{str(os.getenv("USERNAME"))}:{str(os.getenv("PASSWORD"))}@{str(os.getenv("SERVER"))}/{str(os.getenv("DATABASE"))}?driver={str(os.getenv("DRIVER"))}'
cursor = connect.cursor()

class units(Resource): 
    def get(self):
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
            drivername='SQL SERVER'
            servername='PESES-LAPTOP'
            database='wemabank'
            connection_string=f"""
                DRIVER={{{drivername}}};
                SERVER={servername};
            DATABASE={database};
            Trust_Connection=yes;
                """ 
            readdata=odbc.connect(connection_string)
            SQL_Query=pd.read_sql_query('''Select Unit FROM Unit''', readdata)
            unit= SQL_Query.to_dict('records')
            
            units = (unit)
            return jsonify(units)


        # Parse JSON into an object with attributes corresponding to dict keys.
        

api.add_resource(units,"/units")

class departments(Resource):
    def get(self):
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
            drivername='SQL SERVER'
            servername='PESES-LAPTOP'
            database='wemabank'
            connection_string=f"""
                DRIVER={{{drivername}}};
                SERVER={servername};
            DATABASE={database};
            Trust_Connection=yes;
                """ 
            readdata=odbc.connect(connection_string)
            SQL_Query=pd.read_sql_query('''Select Department FROM Department''', readdata)
            depart= SQL_Query.to_dict('records')
            
            departments =(depart)
            return jsonify(departments)
api.add_resource(departments,"/departments")

class newdepartments(Resource):

    def post(self):
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                json = request.get_json()
                print (json)
            else:
                return 'Error'
            connect = pyodbc.connect('Driver={SQL Server};'
            'Server=PESES-LAPTOP;'
            'Database=wemabank;'
            'Trusted_Connection=yes;')
            
        #        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', unhashedpassword):
            # Password=hash(unhashedpassword)
        #       else:
        #          return 'Invalid Password'

            cursor = connect.cursor()
            cursor.execute('''INSERT INTO Department VALUES (?,?)''',(json["Department_name"], json["Description"]))
            
            connect.commit()
            success='Department created successfully'
            return success
api.add_resource(newdepartments,"/departments/new")

class newunits(Resource):
    def post(self):
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                json = request.get_json()
                print (json)
            else:
                return 'Error'
            connect = pyodbc.connect('Driver={SQL Server};'
            'Server=PESES-LAPTOP;'
            'Database=wemabank;'
            'Trusted_Connection=yes;')
            
        #        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', unhashedpassword):
            # Password=hash(unhashedpassword)
        #       else:
        #          return 'Invalid Password'

            cursor = connect.cursor()
            cursor.execute('''INSERT INTO Unit VALUES (?,?,?)''',(json["Unit_name"], json["DepartmentID"], json["Description"]))
            
            connect.commit()
            success='Unit created successfully'
            return success

api.add_resource(newunits,"/units/new")
if __name__ == '__main__':
    app.run(debug =True)

    # def donwload(url, filename=''):
    #     downloadurl = '/allrequests/viewrequest/<string:Email>/linemanagerapproval/download'
    #     if filename:
    #         pass
    #     else:
    #         filename = req.url[downloadurl.rfind('/')+1:]

    #     with requests.get(url) as req:
    #         with open(filename, 'wb') as f:
    #             for chunk in req.iter_content(chunk_size =8192):
    #                 if chunk:
    #                     f.write(chunk)
    #         return filename