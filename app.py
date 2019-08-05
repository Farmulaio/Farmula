from flask import Flask, render_template, url_for, request, jsonify, flash
from wtforms import Form, StringField, IntegerField, validators, SelectField
import urllib3, json, requests, calendar
import pymysql
from flaskext.mysql import MySQL
import datetime
import os


app = Flask(__name__)

# #IBM Watson Credenials 
# wml_credentials={
#     "url":'https://eu-gb.ml.cloud.ibm.com',
#     "username": '461336f2-8984-492a-b72a-9376b8e9d1c2',
#     "password": 'de3136e2-2a65-48cd-85f7-77dd03715ba3'
#     }

# #init header and request and getting response 
# headers = urllib3.util.make_headers(basic_auth='{username}:{password}'.format(username=wml_credentials['username'], password=wml_credentials['password']))
# url = '{}/v3/identity/token'.format(wml_credentials['url'])
# response = requests.get(url, headers=headers)
# mltoken = json.loads(response.text).get('token')


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

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')


@app.route('/price', methods=['GET','POST'])
def price():
    try:
        db = pymysql.connect("localhost","root","ahmed@12345","farmula_dashboard")
        # db = pymysql.connect("localhost","root","","farmula_dashboard")
        predicition = db.cursor()
        price = db.cursor()
        predicition.execute("SELECT  * FROM  prediction ")
        print(today)
        # price.execute("SELECT  * FROM  market_price where statu = 'PUBLISHED' && DATE(create_date) = %s",(today))
        price.execute("SELECT  * FROM  market_price where statu = 'PUBLISHED' ")
        pred_data = predicition.fetchall()
        price_data = price.fetchall()
        print(price_data)
        predicition.close()
        price.close()
    except:
        print('Cant connect to database ')

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


@app.route('/get_price', methods=['GET','POST'])
def get_price():
    try:
        db = pymysql.connect("localhost","root","ahmed@12345","farmula_dashboard")
        # db = pymysql.connect("localhost","root","","farmula_dashboard")
        predicition = db.cursor()
        price = db.cursor()
        price.execute("SELECT  * FROM  market_price where statu = 'PUBLISHED' && DATE(create_date) = %s",(today))
        price_data = price.fetchall()
        print(price_data)
        price.close()
    except:
        print('Cant connect to database ')
    return jsonify(price_data)



if __name__ == '__main__':
    app.secret_key = 'farmula'
    app.run(debug=True)