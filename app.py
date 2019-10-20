from flask import Flask, render_template, url_for, request, jsonify, flash, redirect
from wtforms import Form, StringField, IntegerField, validators, SelectField, DateField
import urllib3, json, requests, calendar
import pymysql
from flaskext.mysql import MySQL
import datetime
import os


app = Flask(__name__)
db = pymysql.connect("localhost","root","ahmed@12345","farmula_dashboard")

response = ""
apikey = "1R4mWJ92xj2R37hvydNj8qvNREL_au-0NQfhOK35O6uS"

# Get an IAM token from IBM Cloud
url     = "https://iam.bluemix.net/oidc/token"
headers = { "Content-Type" : "application/x-www-form-urlencoded" }
data    = "apikey=" + apikey + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
IBM_cloud_IAM_uid = "bx"
IBM_cloud_IAM_pwd = "bx"
response  = requests.post( url, headers=headers, data=data, auth=( IBM_cloud_IAM_uid, IBM_cloud_IAM_pwd ) )
iam_token = response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + iam_token, 'ML-Instance-ID': "6a216236-adcc-48b5-901f-41e4cafbf033"}

today = datetime.date.today()

class PredicitForm(Form):
    crop = SelectField(u'Pick a Crop', choices=[('1', 'Red Irish Patoto'), ('2', 'White Irish Patoto')])
    month = SelectField(u'Pick a Month', choices=[('1', 'January'), ('2', 'February'), ('3', 'March'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'Novmber'), ('12', 'December')])
    day = IntegerField(u'Enter a Day', [validators.NumberRange(min=1, max=31)])
    year = IntegerField(u'Enter a Year', [validators.NumberRange(min=1970, max=2050)])


class OrderForm(Form):
    produce = SelectField(u'Pick a Crop', choices=[('Red Irish Patoto', 'Red Irish Patoto'), ('White Irish Patoto', 'White Irish Patoto')])
    qty = SelectField(u'Pick a Quantity', choices=[('50kg', '50kg Bag'), ('90kg', '90kg Bag')])
    customer_name = StringField(u'Enter your name', [validators.required()])
    phone_number = StringField(u'Enter your phone number', [validators.Length(min=10)])
    customer_address = StringField(u'Enter your address', [validators.required()])


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')


@app.route('/price', methods=['GET','POST'])
def price():
    try:
        predicition = db.cursor()
        price = db.cursor()
        predicition.execute("SELECT  * FROM  prediction ")
        print(today)
        price.execute("SELECT  * FROM  market_price where statu = 'PUBLISHED'")
        pred_data = predicition.fetchall()
        price_data = price.fetchall()
        print(price_data)
        predicition.close()
        price.close()
    except:
        print(" Cant connect to database ")

    form = PredicitForm(request.form)
    if request.method == 'POST' and form.validate():
        crop = form.crop.data
        month = form.month.data
        year = form.year.data
        day = form.day.data

        payload_scoring = {"fields":["Year", "Month", "Day", "Type"],"values":[[year,int(month),day,int(crop)]]}
        response_scoring = requests.post('https://eu-gb.ml.cloud.ibm.com/v3/wml_instances/6a216236-adcc-48b5-901f-41e4cafbf033/deployments/09f168fd-9867-476b-a943-bb4d92acb1fd/online', json=payload_scoring, headers=header)
        print("Scoring response")
        print(json.loads(response_scoring.text)) 
        print(month)
        response = json.loads(response_scoring.text)

        #get result from the response 
        month_num = int(response['values'][0][1])
        month_i = "Month : " + calendar.month_name[month_num]
        year =  "Year : " + str(response['values'][0][0])
        day =  "Day : " + str(response['values'][0][2])
        crop = int(response['values'][0][3])
        if crop == 1 :
            crop_txt = 'Red Irish Potato'
        else :
            crop_txt = 'White Irish Potato'
        crop_txt_temp = "Crop : " + crop_txt
        pre_prams = str(response['values'][0][4])
        price_round = ("%.2f" % round(response['values'][0][5],2))
        price = str("Predict Price :  "+ price_round + " KSH (50KG)")
        return render_template('price.html', form=form, month_i=month_i, day=day, year=year, price=price, crop_txt_temp=crop_txt_temp, pred_data=pred_data, price_data=price_data)

    
    
    return render_template('price.html', form=form, pred_data=pred_data, price_data=price_data)


@app.route('/order', methods=['GET','POST'])
def order():
    form = OrderForm(request.form)
    if request.method == 'POST' and form.validate():
        produce = form.produce.data
        qty = form.qty.data
        customer_name = form.customer_name.data
        phone_number = form.phone_number.data
        customer_address = form.customer_address.data
        try :
            insert_order = db.cursor()
            insert_order.execute("INSERT INTO customer_order (product, customer_name, c_phone, addrees, price, delivery_date, qty, grade, statu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" , (produce, customer_name, phone_number, customer_address, "", "", qty, "", ""))
            db.commit()
            return redirect(url_for('index'))
        except :
            print ("cant insert into database ")

      
    return render_template('order.html', form=form)

@app.route('/get_price', methods=['GET','POST'])
def get_price():
    try:
        predicition = db.cursor()
        price = db.cursor()
        price.execute("SELECT  * FROM  market_price where statu = 'PUBLISHED' && DATE(create_date) = %s",(today))
        price_data = price.fetchall()
        print(price_data)
        price.close()
    except:
        print('Cant connect to database ')
    return jsonify(price_data)

@app.route('/ussd', methods=['GET','POST'])
def ussd_callback():
    global response
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text =  request.values.get("text", "default")


    price_qury_w50 = db.cursor()
    price_qury_w50.execute("SELECT * FROM market_price where product = 'White Irish Potatoes' and qty = '50kg' order by create_date ")
    price_w50 = price_qury_w50.fetchall()
    price_qury_w50.close()

    price_qury_w90 = db.cursor()
    price_qury_w90.execute("SELECT * FROM market_price where product = 'White Irish Potatoes' and qty = '90kg' order by create_date ")
    price_w90 = price_qury_w90.fetchall()
    price_qury_w90.close()

    price_qury_r50 = db.cursor()
    price_qury_r50.execute("SELECT * FROM market_price where product = 'Red Irish Potatoes' and qty = '50kg' order by create_date ")
    price_r50 = price_qury_r50.fetchall()
    price_qury_r50.close()

    price_qury_r90 = db.cursor()
    price_qury_r90.execute("SELECT * FROM market_price where product = 'Red Irish Potatoes' and qty = '90kg' order by create_date ")
    price_r90 = price_qury_r90.fetchall()
    price_qury_r90.close()

  # market price for white 50kg
    price_w50_dict = dict()
    for i in price_w50 :
        market = i[2]
        price = i[3]
        price_w50_dict[market] = price 
    print(price_w50_dict)

    if 'Farmula' in price_w50_dict: farmula_w50 = "\n  Farmula = Sh" + price_w50_dict['Farmula']; farmula_w50_p = price_w50_dict['Farmula']
    else : farmula_w50 = ""

    if 'Nairobi' in price_w50_dict : nairobi_w50 = "\n  Nairobi = Sh" + price_w50_dict['Nairobi'] 
    else : nairobi_w50 = ""

    if 'Marikiti' in price_w50_dict : marikiti_w50 = "\n  Marikiti = Sh" + price_w50_dict['Marikiti']
    else : marikiti_w50 = ""

    if 'Soweto' in price_w50_dict : soweto_w50 = "\n  Soweto = Sh" + price_w50_dict['Soweto']
    else : soweto_w50 = ""

    if 'Donholm' in price_w50_dict : donholm_w50 = "\n  Donholm = Sh" + price_w50_dict['Donholm']
    else : donholm_w50 = ""

    if 'Molo' in price_w50_dict : molo_w50 = "\n  Molo = Sh" + price_w50_dict['Molo']
    else : molo_w50 = ""

    # market price for white 90kg
    price_w90_dict = dict()
    for i in price_w90 :
        market = i[2]
        price = i[3]
        price_w90_dict[market] = price 
    print(price_w90_dict)

    if 'Farmula' in price_w90_dict: farmula_w90 = "\n  Farmula = Sh" + price_w90_dict['Farmula']; farmula_w90_p = price_w90_dict['Farmula']
    else : farmula_w90 = ""

    if 'Nairobi' in price_w90_dict : nairobi_w90 = "\n  Nairobi = Sh" + price_w90_dict['Nairobi'] 
    else : nairobi_w90 = ""

    if 'Marikiti' in price_w90_dict : marikiti_w90 = "\n  Marikiti = Sh" + price_w90_dict['Marikiti']
    else : marikiti_w90 = ""

    if 'Soweto' in price_w90_dict : soweto_w90 = "\n  Soweto = Sh" + price_w90_dict['Soweto']
    else : soweto_w90 = ""

    if 'Donholm' in price_w90_dict : donholm_w90 = "\n  Donholm = Sh" + price_w90_dict['Donholm']
    else : donholm_w50 = ""

    if 'Molo' in price_w90_dict : molo_w90 = "\n  Molo = Sh" + price_w90_dict['Molo']
    else : molo_w90 = ""

    # makert price for red 50 kg
    price_r50_dict = dict()
    for i in price_r50 :
        market = i[2]
        price = i[3]
        price_r50_dict[market] = price 
    print(price_r50_dict)

    if 'Farmula' in price_r50_dict: farmula_r50 = "\n  Farmula = Sh" + price_r50_dict['Farmula']; farmula_r50_p = price_r50_dict['Farmula']
    else : farmula_r50 = ""

    if 'Nairobi' in price_r50_dict : nairobi_r50 = "\n  Nairobi = Sh" + price_r50_dict['Nairobi'] 
    else : nairobi_r50 = ""

    if 'Marikiti' in price_r50_dict : marikiti_r50 = "\n  Marikiti = Sh" + price_r50_dict['Marikiti']
    else : marikiti_r50 = ""

    if 'Soweto' in price_r50_dict : soweto_r50 = "\n  Soweto = Sh" + price_r50_dict['Soweto']
    else : soweto_r50 = ""

    if 'Donholm' in price_r50_dict : donholm_r50 = "\n  Donholm = Sh" + price_r50_dict['Donholm']
    else : donholm_w50 = ""

    if 'Molo' in price_r50_dict : molo_r50 = "\n  Molo = Sh" + price_r50_dict['Molo']
    else : molo_r50 = ""

    # market price for red 90 kg
    price_r90_dict = dict()
    for i in price_r90 :
        market = i[2]
        price = i[3]
        price_r90_dict[market] = price 
    print(price_r90_dict)

    if 'Farmula' in price_r90_dict: farmula_r90 = "\n  Farmula = Sh" + price_r90_dict['Farmula']; farmula_r90_p = price_r90_dict['Farmula'] 
    else : farmula_r90 = ""

    if 'Nairobi' in price_r90_dict : nairobi_r90 = "\n  Nairobi = Sh" + price_r90_dict['Nairobi'] 
    else : nairobi_r90 = ""

    if 'Marikiti' in price_r90_dict : marikiti_r90 = "\n  Marikiti = Sh" + price_r90_dict['Marikiti']
    else : marikiti_r90 = ""

    if 'Soweto' in price_r90_dict : soweto_r90 = "\n  Soweto = Sh" + price_r90_dict['Soweto']
    else : soweto_r90 = ""

    if 'Donholm' in price_r90_dict : donholm_r90 = "\n  Donholm = Sh" + price_r90_dict['Donholm']
    else : donholm_w90 = ""

    if 'Molo' in price_r90_dict : molo_r90 = "\n  Molo = Sh" + price_r90_dict['Molo']
    else : molo_r90 = ""


    if text == '':
        response = "CON Welcome to Farmula pricing platform \n "
        response += "1. Check prices \n"
        response += "2. Order \n"
        response += "3. Price produce \n" 
    
    # check price 
    elif text == '1' :
        response  = "CON Pick produce \n"
        response += "1. Red Irish Potatoes \n"
        response += "2. White Irish Potatoes \n"                                              
        response += "3. Cowpeas \n"               
        response += "4. Carrots \n"
    
    # red Irish
    elif text == '1*1' :
        response = "CON Check Red Irish potato price for \n"
        response += "1. 50kg Bag \n"
        response += "2. 90kg Bag \n"
    
    # red irsih 50kg
    elif text == '1*1*1' :
        response = "CON Red Irish Potato (50kg)" + farmula_r50 + nairobi_r50 + marikiti_r50 + soweto_r50 + donholm_r50 + molo_r50 
        response += "\n 1. Accept \n"
        response += "2. Decline "
        # insert session into database
        try :
            insert_price_sess = db.cursor()
            insert_price_sess.execute("INSERT INTO session (phonenumber,session_id,service_code,hops) VALUES (%s, %s, %s, %s)" , (phone_number,session_id,service_code,text))
            db.commit()
        except :
            print ("can't insert to database")

    elif text == '1*1*1*1' :
        try :
            insert_order = db.cursor()
            insert_order.execute("INSERT INTO customer_order (product, customer_name, c_phone, addrees, price, delivery_date, qty, grade, statu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" , ("Red Irish Potato", "USSD", phone_number, "", farmula_r50_p, "", "50kg", "", ""))
            db.commit()
            response = "END You have Successfully Orderd 50kg bag at Sh" + farmula_r50_p + " \n Thanks for using Farmula Services"
        except :
            response = "END Sorry your Order hasn't been Posted , Please try Again"

    elif text == '1*1*1*2' :
        response = "END Thanks for using Farmula Services \n"
    
     # red irsih 90kg
    elif text == '1*1*2' :
        response = "CON Red Irish Potato (90kg)" + farmula_r90 + nairobi_r90 + marikiti_r90 + soweto_r90 + donholm_r90 + molo_r90 
        response += "\n 1. Accept \n"
        response += "2. Decline "
        # insert session into database
        try :
            insert_price_sess = db.cursor()
            insert_price_sess.execute("INSERT INTO session (phonenumber,session_id,service_code,hops) VALUES (%s, %s, %s, %s)" , (phone_number,session_id,service_code,text))
            db.commit()
        except :
            print ("can't insert to database")

    elif text == '1*1*2*1' :
        try :
            insert_order = db.cursor()
            insert_order.execute("INSERT INTO customer_order (product, customer_name, c_phone, addrees, price, delivery_date, qty, grade, statu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" , ("Red Irish Potato", "USSD", phone_number, "", farmula_r90_p, "", "90kg", "", ""))
            db.commit()
            response = "END You have Successfully Orderd 90kg bag at Sh" + farmula_r90_p + " \n Thanks for using Farmula Services"
        except :
            response = "END Sorry your Order hasn't been Posted , Please try Again"

    elif text == '1*1*2*2' :
        response = "END Thanks for using Farmula Services \n"


 # white Irish
    elif text == '1*2' :
        response = "CON Check White Irish potato price for \n"
        response += "1. 50kg Bag \n"
        response += "2. 90kg Bag \n"
    
    # white irsih 50kg
    elif text == '1*2*1' :
        response = "CON White Irish Potato (50kg)" + farmula_w50 + nairobi_w50 + marikiti_w50 + soweto_w50 + donholm_w50 + molo_w50 
        response += "\n 1. Accept \n"
        response += "2. Decline "
        # insert session into database
        try :
            insert_price_sess = db.cursor()
            insert_price_sess.execute("INSERT INTO session (phonenumber,session_id,service_code,hops) VALUES (%s, %s, %s, %s)" , (phone_number,session_id,service_code,text))
            db.commit()
        except :
            print ("can't insert to database")

    elif text == '1*2*1*1' :
        try :
            insert_order = db.cursor()
            insert_order.execute("INSERT INTO customer_order (product, customer_name, c_phone, addrees, price, delivery_date, qty, grade, statu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" , ("White Irish Potato", "USSD", phone_number, "", farmula_w50_p, "", "50kg", "", ""))
            db.commit()
            response = "END You have Successfully Orderd 50kg bag at Sh" + farmula_w50_p + " \n Thanks for using Farmula Services"
        except :
            response = "END Sorry your Order hasn't been Posted , Please try Again"

    elif text == '1*2*1*2' :
        response = "END Thanks for using Farmula Services \n"
    
     # white irsih 90kg
    elif text == '1*2*2' :
        response = "CON White Irish Potato (90kg)" + farmula_w90 + nairobi_w90 + marikiti_w90 + soweto_w90 + donholm_w90 + molo_w90 
        response += "\n 1. Accept \n"
        response += "2. Decline "
        # insert session into database
        try :
            insert_price_sess = db.cursor()
            insert_price_sess.execute("INSERT INTO session (phonenumber,session_id,service_code,hops) VALUES (%s, %s, %s, %s)" , (phone_number,session_id,service_code,text))
            db.commit()
        except :
            print ("can't insert to database")

    elif text == '1*2*2*1' :
        try :
            insert_order = db.cursor()
            insert_order.execute("INSERT INTO customer_order (product, customer_name, c_phone, addrees, price, delivery_date, qty, grade, statu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" , ("White Irish Potato", "USSD", phone_number, "", farmula_w90_p, "", "90kg", "", ""))
            db.commit()
            response = "END You have Successfully Orderd 50kg bag at Sh" + farmula_w90_p + " \n Thanks for using Farmula Services"
        except :
            response = "END Sorry your Order hasn't been Posted , Please try Again"

    elif text == '1*2*2*2' :
        response = "END Thanks for using Farmula Services \n"

    # Cowpeas
    elif text == '1*3' :
        response = "END Cowpeas not availabe for now"

    # Carrots
    elif text == '1*4' :
        response = "END Carrots not availabe for now"   


    # order
    elif text == '2' :
        response  = "CON "
        response += "1. Red Irish Potatoes \n"
        response += "2. White Irish Potatoes \n"                                              
        response += "3. Cowpeas \n"               
        response += "4. Carrots \n"

      # Cowpeas
    elif text == '2*3' :
        response = "END Cowpeas not availabe for now"

    # Carrots
    elif text == '2*4' :
        response = "END Carrots not availabe for now"   
    
    # order red irish potatoes
    elif text == '2*1' :
        response  = "CON Order Red Irish Potatoes \n"
        response += "1. 50kg Bag \n"
        response += "2. 90kg Bag \n"

    # order red irish 50kg
    elif text == "2*1*1":
        response = "CON Red Irish Potato (50kg)" + farmula_r50 
        response += "\n 1. Accept \n"
        response += "2. Decline "
        # insert session into database
        try :
            insert_price_sess = db.cursor()
            insert_price_sess.execute("INSERT INTO session (phonenumber,session_id,service_code,hops) VALUES (%s, %s, %s, %s)" , (phone_number,session_id,service_code,text))
            db.commit()
        except :
            print ("can't insert to database")
        
    elif text == "2*1*1*1" :
        try :
            insert_order = db.cursor()
            insert_order.execute("INSERT INTO customer_order (product, customer_name, c_phone, addrees, price, delivery_date, qty, grade, statu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" , ("Red Irish Potato", "USSD", phone_number, "", farmula_r50_p, "", "50kg", "", ""))
            db.commit()
            response = "END You have Successfully Orderd 50kg bag at Sh" + farmula_r50_p + " \n Thanks for using Farmula Services"
        except :
            response = "END Sorry your Order hasn't been Posted , Please try Again"

    elif text == '2*1*1*2' :
        response = "END Thanks for using Farmula Services \n"


    # order red irish 90kg
    elif text == "2*1*2":
        response = "CON Red Irish Potato (90kg)" + farmula_r90 
        response += "\n 1. Accept \n"
        response += "2. Decline "
        # insert session into database
        try :
            insert_price_sess = db.cursor()
            insert_price_sess.execute("INSERT INTO session (phonenumber,session_id,service_code,hops) VALUES (%s, %s, %s, %s)" , (phone_number,session_id,service_code,text))
            db.commit()
        except :
            print ("can't insert to database")
        
    elif text == "2*1*2*1" :
        try :
            insert_order = db.cursor()
            insert_order.execute("INSERT INTO customer_order (product, customer_name, c_phone, addrees, price, delivery_date, qty, grade, statu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" , ("Red Irish Potato", "USSD", phone_number, "", farmula_r90_p, "", "90kg", "", ""))
            db.commit()
            response = "END You have Successfully Orderd 90kg bag at Sh" + farmula_r90_p + " \n Thanks for using Farmula Services"
        except :
            response = "END Sorry your Order hasn't been Posted , Please try Again"

    elif text == '2*1*2*2' :
        response = "END Thanks for using Farmula Services \n"





 # order white irish potatoes
    elif text == '2*2' :
        response  = "CON Order White Irish Potatoes \n"
        response += "1. 50kg Bag \n"
        response += "2. 90kg Bag \n"

    # order white irish 50kg
    elif text == "2*2*1":
        response = "CON White Irish Potato (50kg)" + farmula_w50 
        response += "\n 1. Accept \n"
        response += "2. Decline "
        # insert session into database
        try :
            insert_price_sess = db.cursor()
            insert_price_sess.execute("INSERT INTO session (phonenumber,session_id,service_code,hops) VALUES (%s, %s, %s, %s)" , (phone_number,session_id,service_code,text))
            db.commit()
        except :
            print ("can't insert to database")
        
    elif text == "2*2*1*1" :
        try :
            insert_order = db.cursor()
            insert_order.execute("INSERT INTO customer_order (product, customer_name, c_phone, addrees, price, delivery_date, qty, grade, statu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" , ("White Irish Potato", "USSD", phone_number, "", farmula_w50_p, "", "50kg", "", ""))
            db.commit()
            response = "END You have Successfully Orderd 50kg bag at Sh" + farmula_w50_p + " \n Thanks for using Farmula Services"
        except :
            response = "END Sorry your Order hasn't been Posted , Please try Again"

    elif text == '2*2*1*2' :
        response = "END Thanks for using Farmula Services \n"


    # order White irish 90kg
    elif text == "2*2*2":
        response = "CON White Irish Potato (90kg)" + farmula_w90 
        response += "\n 1. Accept \n"
        response += "2. Decline "
        # insert session into database
        try :
            insert_price_sess = db.cursor()
            insert_price_sess.execute("INSERT INTO session (phonenumber,session_id,service_code,hops) VALUES (%s, %s, %s, %s)" , (phone_number,session_id,service_code,text))
            db.commit()
        except :
            print ("can't insert to database")
        
    elif text == "2*2*2*1" :
        try :
            insert_order = db.cursor()
            insert_order.execute("INSERT INTO customer_order (product, customer_name, c_phone, addrees, price, delivery_date, qty, grade, statu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" , ("White Irish Potato", "USSD", phone_number, "", farmula_w90_p, "", "90kg", "", ""))
            db.commit()
            response = "END You have Successfully Orderd 90kg bag at Sh" + farmula_w90_p + " \n Thanks for using Farmula Services"
        except :
            response = "END Sorry your Order hasn't been Posted , Please try Again"

    elif text == '2*2*2*2' :
        response = "END Thanks for using Farmula Services \n"
    
    # price mechanism
    elif text == '3' :
        response  = "CON "
        response += "1. Red Irish Potatoes \n"
        response += "2. White Irish Potatoes \n"                                              
        response += "3. Cowpeas \n"               
        response += "4. Carrots \n"

# price mechanism for Red Irish
    elif text == "3*1" :
        response  = "CON Source of seeds : \n"
        response += "1. Government \n"
        response += "2. Agrovet \n"  

    elif text == "3*1*1" or text == "3*1*2":
        response  = "CON Tractor : \n"
        response += "1. Own \n"
        response += "2. Hired \n"


    elif text == "3*1*1*1" or text == "3*1*1*2" or text == "3*1*2*1" or text == "3*1*2*1" or text == "3*1*2*2":
        response  = "CON Source of fertilizer : \n"
        response += "1. Government \n"
        response += "2. Agrovet \n"   
    
    elif text == "3*1*1*1*1" or text == "3*1*1*1*2" or text == "3*1*1*2*1" or text == "3*1*1*2*1" or text == "3*1*2*1*1" or text == "3*1*2*1*2"  or text == "3*1*2*2*1" or text == "3*1*2*2*2":
        response  = "CON Pesticide : \n"
        response += "1.Yes \n"
        response += "2. No \n"

    # elif text != '1' or text != '2' or text != '3' :
    #     response = "END Please enter valid option  \n "
                                           
    return response

if __name__ == '__main__':
    app.secret_key = 'farmula'
    app.run(debug=True)