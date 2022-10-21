
from datetime import datetime,timedelta
from flask import Flask, request, redirect, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS 
import pypyodbc as odbc 
import pandas as pd
import pyodbc
import os
from hashlib import sha256
import datetime
import jwt
import re


app = Flask(__name__)
api = Api(app)
CORS(app)
cors = CORS(app, resources={
    r"/*":{
        "origins": "*"
    }
})

app.config['SECRET_KEY'] = 'oluwapesealo'

def tokenauthent(Email,key):
        if 'tokenauth' in request.headers:
                token = request.headers['tokenauth']
                tokget=cursor.execute(str(os.getenv("tokenselect")), Email)
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

def validemail(Email):
   pat = "^[a-zA-Z0-9-.]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
   if re.match(pat,Email):
      return True
   return False

def hash(data):
        hash_var=sha256((data).encode())
        finalhash=hash_var.hexdigest()
        return finalhash

SERVER='PESES-LAPTOP'
DATABASE='wemabank'
DRIVER='SQL Server Native Client 11.0'
USERNAME='sa'
PASSWORD='sa'
drivername='SQL SERVER'
servername='PESES-LAPTOP'
database='wemabank'
connection_string=f"""
DRIVER={{{drivername}}};
SERVER={servername};
DATABASE={database};
Trust_Connection=yes;
    """ 
connect = pyodbc.connect('Driver={SQL Server};'
            'Server=PESES-LAPTOP;'
            'Database=wemabank;'
            'Trusted_Connection=yes;')
connection_string1=f'mssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}'
# connection_string=f'mssql://{str(os.getenv("USERNAME"))}:{str(os.getenv("PASSWORD"))}@{str(os.getenv("SERVER"))}/{str(os.getenv("DATABASE"))}?driver={str(os.getenv("DRIVER"))}'
cursor = connect.cursor()

class employees(Resource):

    def post( Email=''):
        content_type = request.headers.get('Content-Type')
        json = request.get_json()
        
        emailcheck = validemail(json['Email'])
        if emailcheck == True :
            names = json['Email']
            fnames, _, _ =names.partition("@") 
            name = fnames.split(".")
            fullname = ' '.join(name)
            Fullname = fullname
            success = "Successfully"
            readdata=odbc.connect(connection_string)
            SQL_Query=pd.read_sql_query('''select Email from AllStaff''',readdata)
            emailtable= pd.DataFrame(SQL_Query)
            
            readdata=odbc.connect(connection_string)
            SQL_Query1=pd.read_sql_query('''select StaffID from AllStaff''',readdata)
            staffidtable= pd.DataFrame(SQL_Query1)


            Password=hash(json['unhashedpassword'])
            print(Password)
            cursor = connect.cursor()
            emailexist=(json["Email"] in emailtable['email'].unique())
            staffidexist=(json["StaffID"] in staffidtable['staffid'].unique())
            if (staffidexist == True):
                return "StaffID already exist"
            else:
                if (emailexist==True):
                        return "Email already exists "
                else:
                        cursor.execute('''INSERT INTO AllStaff VALUES (?,?,?,?,?, NULL,NULL, ? )''',(json["StaffID"], json["Email"],Password, Fullname , json["UnitID"],  json["DesignationID"]))
                        connect.commit()
                        success='sign up was successful'
                        return success
        else:
            return {"message":"Email does not match supported format"}

api.add_resource(employees,'/newuser')

class login(Resource):
    def post(self):
        email_pass=request.get_json()
        cursor = connect.cursor()
        self.email=email_pass['Email']
        password=hash(email_pass['Password'])
        readdata=odbc.connect(connection_string)
        sqltable=pd.read_sql_query(str(os.getenv("selectall")),readdata)
        finaltable1=pd.DataFrame(sqltable)
        emailauthentication=(self.email in finaltable1['Email'].unique())
        if (emailauthentication==True):
            # passwordauthentication=(password in finaltable1['password'].unique())
            passwordauthentication=cursor.execute(os.getenv("accpassword"),self.email)
            for passw in passwordauthentication:
                pass
            pass_word=passw[0]

            if (pass_word==password):
                sqlroleid=cursor.execute(os.getenv("roleid"),self.email)
                for  d in sqlroleid:
                    pass
                roleid=d[0]
                sqlrole=cursor.execute(os.getenv("role"),roleid)
                for b in sqlrole:
                    pass
                role=b[0]
                sqlunitid=cursor.execute  (os.getenv("unitid"),self.email)
                for unid in sqlunitid:
                    pass
                unitid=unid[0]
                sqlunit=cursor.execute(str(os.getenv("unitname")),unitid)
                for unidd in sqlunit:
                    pass
                unit=unidd[0]
                key=str(os.getenv("key"))
                encodedtoken = jwt.encode({
                    'email': self.email,
                    "unit":unit,
                    "role":role,
                    "message":"you are connected",
                'expiration': str(datetime.utcnow() + timedelta(seconds=999))
                },key)
                cursor.execute(str(os.getenv("updatetoken")),str(encodedtoken),self.email)
                connect.commit()
            else:
                
                return {"message":"incorrect password"}
        else:
            
            return {"message":"user does not exist"}
        return  jwt.decode(encodedtoken, key=str(os.getenv("key")), algorithms=['HS256', ])

api.add_resource(login,'/login')

class scheduledays(Resource):
    def post(self):
        data=request.get_json()
        self.email=data['email']
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
                data=request.get_json()
                self.email=data['email']
                x=0
                self.Monday=data['Monday']
                self.Tuesday=data['Tuesday']
                self.Wednesday=data['Wednesday']
                self.Thursday=data['Thursday']
                self.Friday=data['Friday']
                body=data['Body']
                days=[self.Monday,self.Tuesday,self.Wednesday,self.Thursday,self.Friday]
                for i in days:
                    if(i==1):
                        x=x+1
                if (self.Monday==1 and self.Tuesday==1):
                    return "you cannot pick consecutive days that follow monday and friday"
                elif (self.Monday==1 and self.Friday==1):
                    return "you cannot pick consecutive days that follow monday and friday"
                elif (self.Thursday==1 and self.Friday==1):
                    return "you cannot pick consecutive days that follow monday and friday"           
                elif(x>2):
                    return("Error you chose more than the required amount of days required to work remotely please select only two days ")
                else:
                    # try:
                    cursor.execute(os.getenv("monday"),(self.Monday,self.email))
                    cursor.execute(os.getenv("tuesday"),(self.Tuesday,self.email))
                    cursor.execute(os.getenv("wednesday"),(self.Wednesday,self.email))
                    cursor.execute(os.getenv("thursday"),(self.Thursday,self.email))
                    cursor.execute(os.getenv("friday"),(self.Friday,self.email))
                    cursor.execute(os.getenv("body"),(str(body),self.email))
                    cursor.execute(os.getenv("datesent"),(str(datetime.utcnow()),self.email))
                    connect.commit()
                    return{"message":"token is valid and scheduleddays assinged succefully",'Monday':bool(self.Monday),'Tuesday':bool(self.Tuesday),'Wednesday':bool(self.Wednesday),'Thursday':bool(self.Thursday),'Friday':bool(self.Friday)}
                    # except:
                    #     return{"message":("could not update scheduled days")}
        else :
            return{"message":tokenfunc['message']}
      
    def patch(self):
        data=request.get_json()
        self.email=data['email']
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
                x=0
                data=request.get_json()
                self.email=data['email']
                self.Monday=data['Monday']
                self.Tuesday=data['Tuesday']
                self.Wednesday=data['Wednesday']
                self.Thursday=data['Thursday']
                self.Friday=data['Friday']
                days=[self.Monday,self.Tuesday,self.Wednesday,self.Thursday,self.Friday]
                for i in days:
                    if(i==1):
                        x=x+1
                if (self.Monday==1 and self.Tuesday==1):
                    return "you cannot pick consecutive days that follow monday and friday"
                elif (self.Monday==1 and self.Friday==1):
                    return "you cannot pick consecutive days that follow monday and friday"
                elif (self.Thursday==1 and self.Friday==1):
                    return "you cannot pick consecutive days that follow monday and friday"           
                elif(x>2):
                    return("Error you chose more than the required amount of days required to work remotely please select only two days ")
                else:
                    try:
                        cursor.execute(os.getenv("monday"),(self.Monday,self.email))
                        cursor.execute(os.getenv("tuesday"),(self.Tuesday,self.email))
                        cursor.execute(os.getenv("wednesday"),(self.Wednesday,self.email))
                        cursor.execute(os.getenv("thursday"),(self.Thursday,self.email))
                        cursor.execute(os.getenv("friday"),(self.Friday,self.email))
                        cursor.execute(os.getenv("datesent"),(str(datetime.utcnow()),self.email))
                        connect.commit()
                        return{"message":"token is valid and scheduleddays assinged succefully",'Monday':bool(self.Monday),'Tuesday':bool(self.Tuesday),'Wednesday':bool(self.Wednesday),'Thursday':bool(self.Thursday),'Friday':bool(self.Friday)}
                    except:
                        return{"message":("could not update scheduled days")}

        else :
            return{"message":tokenfunc['message']}

api.add_resource(scheduledays,"/scheduleddays")

class alltasks(Resource):

    def get(self,Email='', UnitID = ''):
        self.Email=Email
        self.UnitID=UnitID
        readdata=odbc.connect(connection_string)
        SQL_Query=pd.read_sql_query('''select *from Alltasks

                                        ''', readdata,)
        vrequests= SQL_Query.to_dict('records')
        return(vrequests)

api.add_resource(alltasks,'/alltasks')

class viewtask(Resource):
    def get(Email):
        Email = request.args['Email']
        
        readdata=odbc.connect(connection_string)
        SQL_Query=pd.read_sql_query('''select *from Alltasks where Email = ''' +Email, readdata)
        vtask= SQL_Query.to_dict('records')
        return(vtask)

api.add_resource(viewtask,'/alltasks/viewtask')

class teamapproval(Resource):

    def patch( self, Email=''):
            self.Email = Email
            Email = request.args['Email']
            content_type = request.headers.get('Content-Type')
            json = request.get_json()
            if json["TeamLead_Approval"] == 'True':
                
                cursor.execute('''update AllScheduleDays set TeamLead_Approval = 1 where Email ='''+Email)
                cursor.execute('''update AllScheduleDays set Reason_for_TeamLead_Decline = NULL where Email ='''+Email )
                connect.commit()
                success = "True Update was successful"
                return success
            if json["TeamLead_Approval"] == 'False':
                
                cursor.execute('''update AllScheduleDays set TeamLead_Approval = 0 where Email = '''+Email) 
                cursor.execute('''update AllScheduleDays set Reason_for_TeamLead_Decline = ? where Email =?''',(json["Reason_for_Teamlead_Decline"], json["Email"]) )
                connect.commit()
                success = "False Update was successful"
                return self.Email
            else:
                failure = "Could not update"
                return failure

api.add_resource(teamapproval,'/alltasks/viewtask/teamleadapproval')

class linemanager(Resource):
    
        def patch( self, Email='', Reason_for_Linemanager_Decline=''):
            self.Email = Email
            self.Reason_for_Linemanager_Decline = Reason_for_Linemanager_Decline
            Email = request.args['Email']
            content_type = request.headers.get('Content-Type')
            json = request.get_json()
            if json["LineManager_Approval"] == 'True':
                
                cursor.execute('''update AllScheduleDays set LineManager_Approval = 1 where Email ='''+Email)
                connect.commit()
                success = "True Update was successful"
                return success
            if json["LineManager_Approval"] == 'False':
                
                cursor.execute('''update AllScheduleDays set LineManager_Approval = 0 where Email = '''+Email) 
                cursor.execute('''update AllScheduleDays set Reason_for_Linemanager_Decline = ? where Email =?''',(json["Reason_for_Linemanager_Decline"], json["Email"]) )
                connect.commit()
                success = "False Update was successful"
                return success
            else:
                failure = "Could not update"
                return failure

api.add_resource(linemanager,'/alltasks/viewtask/linemanagerapproval')

class downloadreq(Resource):
    def get(Email):
        Email = request.args['Email']
        readdata=odbc.connect(connection_string)
        SQL_Query=pd.read_sql_query('''select *from AllScheduleDays where Email ='''+Email, readdata,)
        df = pd.DataFrame(SQL_Query)
        down = df.to_csv(Email+".csv")
        success = 'Download was successful'
        return down

api.add_resource(downloadreq, '/alltasks/viewtask/linemanagerapproval/download')

class logout(Resource):
    def post(self):
            data=request.get_json()
            self.email=data['email']
            loggedout=cursor.execute(os.getenv("tokenselect"),(self.email))
            for i in loggedout:
                pass
            token=i[0]
            decodedtoken=jwt.decode(token,key=str(os.getenv("key")), algorithms=['HS256'])
            decodedtoken['expiration']=str(datetime.utcnow() - timedelta(seconds=999))
            loggedouttoken=jwt.encode((decodedtoken),key=str(os.getenv("key")))
            try:
                cursor.execute(str(os.getenv("updatetoken")),str(loggedouttoken),self.email)
                connect.commit()
                return{"message":"you have been logged out succefully"}
            except:
                return{"message":"error login you out"}
            
api.add_resource(logout,'/logout')

#IDENTITY MANAGEMENT 

class units(Resource): 
    def get(Email=''):
            readdata=odbc.connect(connection_string)
            SQL_Query=pd.read_sql_query('''Select Unit FROM Unit''', readdata)
            unit= SQL_Query.to_dict('records')
            
            units = (unit)
            return jsonify(units)

api.add_resource(units,"/units")

class departments(Resource):
    def get(Email=''):
            readdata=odbc.connect(connection_string)
            SQL_Query=pd.read_sql_query('''Select Department_name FROM Department''', readdata)
            depart= SQL_Query.to_dict('records')
            
            departments =(depart)
            return jsonify(departments)

api.add_resource(departments,"/departments")

class roles(Resource):
    def get(self):
        data=request.get_json()
        self.email=data['email']
        tokenfunc=tokenauthent(self.email,"f9bb43fda47e9f127dee774b5f424a1b24b354bace8566e236770c70c3eabfed")
        if (tokenfunc['message']=="token is valid"):
            # to return available roles
            x=cursor.execute("Select [roles] , [Description_] FROM [employeedb].[dbo].[Roles] ")
            roles=[]
            for row in x:
                roles.append({"role" :row[0],"Description":row[1]})
            return jsonify(roles)
        else :
            return{"message":tokenfunc['message']}

api.add_resource(roles,"/roles")

class designations(Resource):
    def get(self):
        # to get available designations
        data=request.get_json()
        self.email=data['email']
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
            # to return available roles
            x=cursor.execute(os.getenv("designationcreate"))
            roles=[]
            for row in x:
                roles.append({"Description":row[1],"Designation":row[0]})
            return jsonify(roles)
        else :
            return{"message":tokenfunc['message']}

api.add_resource(designations,"/designation")

class newdesignation(Resource):
    def post(self):
        # to add new designation
        data=request.get_json()
        self.email=data['email']
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
            try:
                cursor.execute(os.getenv("designationinsert"),(data['Designation'],data['Description']))
                connect.commit()
                return{"message":"desingtion added succesfully"}
            except:
                return {"message":"failed to add destination"}
        else :
            return{"message":tokenfunc['message']}

api.add_resource(newdesignation,"/designation")

class newrole(Resource):    
    def post(self):
        # To add new roles

        data=request.get_json()
        self.email=data['email']
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
            try:
                cursor.execute(os.getenv("rolesinsert"),(data['Role'],data['DesignationID'],data['Description']))
                connect.commit()
                return{"message":"role added succesfully"}
            except:
                return {"message":"failed to add role"}
        else :
            return{"message":tokenfunc['message']}

api.add_resource(newrole,"/newroles")

class newdepartments(Resource):

    def post(self,Email=''):
        self.Email=Email
        # tokenfunc=tokenauthent(self.Email,str(os.getenv("key")))
        # if (tokenfunc['message']=="token is valid"):
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            json = request.get_json()
            print (json)
        else:
            return 'Error'

        cursor = connect.cursor()
        cursor.execute('''INSERT INTO Department VALUES (?,?)''',(json["Department_name"], json["Description"]))
        
        connect.commit()
        success='Department created successfully'
        return success

api.add_resource(newdepartments,"/departments/new")

class newunits(Resource):
    def post(self,Email=''):
        self.Email=Email
        # tokenfunc=tokenauthent(self.Email,str(os.getenv("key")))
        # if (tokenfunc['message']=="token is valid"):
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            json = request.get_json()
            print (json)
        else:
            return 'Error'
        
        cursor = connect.cursor()
        cursor.execute('''INSERT INTO Unit VALUES (?,?,?,?)''',(json["Unit_name"], json["DepartmentID"], json["Description"], json["Line_Manager"]))
        
        connect.commit()
        success='Unit created successfully'
        return success

api.add_resource(newunits,"/units/new")

if __name__ =="__main__":
    app.run(debug=True)
    
