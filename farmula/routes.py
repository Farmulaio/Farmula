from farmula import app, db
from farmula.forms import PredicitForm , OrderForm
from flask import redirect, url_for, render_template, request
import urllib3, json, requests, calendar, random, string
from datetime import datetime
from farmula.models import Crop, Quantity, Market, Price, Orders, Prediction, Pricechecksession, Farmer, Sales, Conditions
from farmula import config

response = ""

def random_string_generator(size=5,  chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# index route 
@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')


# getting daily price and predicted prices
@app.route('/price', methods=['GET','POST'])
def price():
    try :
        PredictionItems = db.session.query(Prediction).all()
        PriceItems = db.session.query(Price).join(Market).filter(Market.Name=='Farmula').order_by(Price.IdPrice.desc()).limit(4)
    except KeyError as error :
        print(error)
    form = PredicitForm(request.form)
    if request.method == 'POST' and form.validate():
     
        payload_scoring = {"fields":["Year", "Month", "Day", "Type"],"values":[[form.year.data,int(form.month.data),form.day.data,int(form.crop.data)]]}
        response_scoring = requests.post('https://eu-gb.ml.cloud.ibm.com/v3/wml_instances/6a216236-adcc-48b5-901f-41e4cafbf033/deployments/2736cd44-a971-40d8-ba07-f8014ab77d44/online', json=payload_scoring, headers= config.header)
        print(json.loads(response_scoring.text)) 
        response = json.loads(response_scoring.text)
    
        try :
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
            return render_template('price.html', form=form, month_i=month_i, day=day, year=year, price=price, crop_txt_temp=crop_txt_temp, PredictionItems = PredictionItems, PriceItems = PriceItems)
        except KeyError as error :
            print('error getting response from IBM watson')
        return render_template('price.html', form = form, PredictionItems = PredictionItems, PriceItems = PriceItems)
    return render_template('price.html', form = form, PredictionItems = PredictionItems, PriceItems = PriceItems)



# order route
@app.route('/order', methods=['GET','POST'])
def order():   
    CropItems = db.session.query(Crop).filter_by(Enabled = 1).all()
    QuantityItems = db.session.query(Quantity).filter_by(Enabled = 1).all()
    return render_template('order.html' , CropItems = CropItems, QuantityItems = QuantityItems)


@app.route('/order/new', methods=['POST', 'GET'])
def add_order():
        if request.method == 'POST':
            NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = request.form['BusinesName'], PhoneNumber = request.form['PhoneNumber'], Address = request.form['Address'] , IdBusines = 0, IdCrop = request.form['Crop'], IdQty = request.form['Qty'], IdOrderStatus = 1, Price = 20192.0 , Logistic = 0.0, Ordertime = str(datetime.date(datetime.now())))
            try :
                db.session.add(NewOrder)
                db.session.commit()
    
                NewSales = Sales(IdOrder = NewOrder.IdOrder, Price = NewOrder.Price, Paid = 0.0, IdBusines =  NewOrder.IdBusines )
                db.session.add(NewSales)
                db.session.commit()

            except :
                return redirect(url_for('index'))

        return redirect(url_for('index'))

# farmer route 
@app.route('/farmer', methods=['GET','POST'])
def farmer():
    FarmerItems = db.session.query(Farmer).all()
    CropItems = db.session.query(Crop).filter_by(Enabled = 1).all()
    if request.method == 'POST':
        NewFarmer = Farmer(FirstName = request.form['FirstName'], LastName = request.form['LastName'], PhoneNumber = request.form['PhoneNumber'], Address = request.form['Address'], IdCrop = request.form['Crop'], Harvestime = request.form['Harvestime'])
        try :
            db.session.add(NewFarmer)
            db.session.commit()
            return redirect(url_for('index'))
        except :          
            return redirect(url_for('index'))

    return render_template('farmer.html', FarmerItems = FarmerItems, CropItems = CropItems)

