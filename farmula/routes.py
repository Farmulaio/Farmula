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
    try:
        PredictionItems = db.session.query(Prediction).all()
        PriceItems = db.session.query(Price).filter_by(CreatedAt = datetime.date(datetime.now())).all()
    
    except:
        print(" Cant connect to database ")

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
        except KeyError :
            print('Cant get response ')
        return render_template('price.html', form = form, PredictionItems = PredictionItems, PriceItems = PriceItems)
    return render_template('price.html', form = form, PredictionItems = PredictionItems, PriceItems = PriceItems)



# order route
@app.route('/order', methods=['GET','POST'])
def order():   
    CropItems = db.session.query(Crop).filter_by(Enabled = 1).all()
    QuantityItems = db.session.query(Quantity).filter_by(Enabled = 1).all()
    MarketItems = db.session.query(Market).filter_by(Enabled = 1).all()
    return render_template('order.html' , CropItems = CropItems, QuantityItems = QuantityItems, MarketItems = MarketItems)


@app.route('/order/new', methods=['POST', 'GET'])
def add_order():
        if request.method == 'POST':
            try :
                NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = request.form['BusinesName'], PhoneNumber = request.form['PhoneNumber'], Address = request.form['Address'], IdCrop = request.form['Crop'], IdMarket = request.form['Market'],  IdQty = request.form['Qty'], IdOrderStatus = 1, Price = 20192.0)
                db.session.add(NewOrder)
                db.session.commit()

                NewSales = Sales(IdOrder = NewOrder.IdOrder, Price = NewOrder.Price, Paid = 0.0)
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


# ussd route
@app.route('/ussd', methods=['POST', 'GET'])
def ussd_callback():
    global respsone 
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text =  request.values.get("text", "default")

    PriceAll = []
    PriceFarmula = []
    PriceFarmula10 = []

    AllMarketPrice = db.session.query(Price).filter_by(CreatedAt = datetime.date(datetime.now())).all()
    FarmulaMarketPrice = db.session.query(Price).filter_by(CreatedAt = datetime.date(datetime.now())).all()

    FarmulaPrice10 = db.session.query(Price).join(Market).join(Quantity).filter(Market.Name=='Farmula', Quantity.Qty=="10kg", Price.CreatedAt == datetime.date(datetime.now()) ).first()
    FarmulaPrice10P = db.session.query(Price).join(Market).join(Quantity).filter(Market.Name=='Farmula', Quantity.Qty=="10kg peeled", Price.CreatedAt == datetime.date(datetime.now()) ).first()
    FarmulaPrice20 = db.session.query(Price).join(Market).join(Quantity).filter(Market.Name=='Farmula', Quantity.Qty=="20kg", Price.CreatedAt == datetime.date(datetime.now()) ).first()
    FarmulaPrice20P = db.session.query(Price).join(Market).join(Quantity).filter(Market.Name=='Farmula', Quantity.Qty=="20kg peeled", Price.CreatedAt == datetime.date(datetime.now()) ).first()
    FarmulaPrice50 = db.session.query(Price).join(Market).join(Quantity).filter(Market.Name=='Farmula', Quantity.Qty=="50kg", Price.CreatedAt == datetime.date(datetime.now()) ).first()
    FarmulaPrice90 = db.session.query(Price).join(Market).join(Quantity).filter(Market.Name=='Farmula', Quantity.Qty=="90kg", Price.CreatedAt == datetime.date(datetime.now()) ).first()

    if FarmulaPrice10 :
        res_10 = " "+ FarmulaPrice10.qty.Qty + "(" + str(FarmulaPrice10.Price) + "Ksh)" + "\n"
    else :
       res_10 = "Sorry price is unavilable \n" 

    if FarmulaPrice10P :
        res_10P = " "+ FarmulaPrice10P.qty.Qty + "(" + str(FarmulaPrice10P.Price) + "Ksh)" + "\n"
    else :
       res_10P = "Sorry price is unavilable \n" 

    if FarmulaPrice20 :
        res_20 = " "+ FarmulaPrice20.qty.Qty + "(" + str(FarmulaPrice20.Price) + "Ksh)" + "\n"
    else :
       res_20 = "Sorry price is unavilablev \n" 

    if FarmulaPrice20P :
         res_20P = " "+ FarmulaPrice20P.qty.Qty + "(" + str(FarmulaPrice20P.Price) + "Ksh)" + "\n"
    else :
       res_20P = "Sorry price is unavilable \n" 

    if FarmulaPrice50 :
        res_50 = " "+ FarmulaPrice50.qty.Qty + "(" + str(FarmulaPrice50.Price) + "Ksh)" + "\n"
    else :
       res_50 = "Sorry price is unavilable \n" 

    if FarmulaPrice90 :
        res_90 = " "+ FarmulaPrice90.qty.Qty + "(" + str(FarmulaPrice90.Price) + "Ksh)" + "\n"
    else :
       res_90 = "Sorry price is unavilable \n" 
    
    if text == "":
        if not AllMarketPrice :
            respsone = "END Welcome to Farmula \n Sorry today prices are not availabe yet"
        else :
            respsone = "CON Welcome to Farmula , order for  \n"
            respsone += "1. "+ res_10
            respsone += "2. "+ res_10P
            respsone += "3. "+ res_20
            respsone += "4. "+ res_20P
            respsone += "5. "+ res_50
            respsone += "6. "+ res_90
            respsone += "7. Check other prices \n"
    
    elif text == '1':
        try :
            NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = '', PhoneNumber = phone_number, Address = '', IdCrop = FarmulaPrice10.crop.IdCrop, IdMarket = FarmulaPrice10.market.IdMarket, IdQty = FarmulaPrice10.qty.IdQty, IdOrderStatus = '1', Price = FarmulaPrice10.Price)
            db.session.add(NewOrder)
            db.session.commit()
            respsone = "END Thanks for using Farmula services to order " + FarmulaPrice10.crop.Name + " "+ FarmulaPrice10.qty.Qty + "@" + str(FarmulaPrice10.Price) + "Ksh" + "\n"
        except :
            respsone = "END Sorry an error occurred, please try again later "

    elif text == '2':
        try :
            NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = '', PhoneNumber = phone_number, Address = '', IdCrop = FarmulaPrice10P.crop.IdCrop, IdMarket = FarmulaPrice10P.market.IdMarket, IdQty = FarmulaPrice10P.qty.IdQty, IdOrderStatus = '1', Price = FarmulaPrice10P.Price)
            db.session.add(NewOrder)
            db.session.commit()
            respsone = "END Thanks for using Farmula services to order " + FarmulaPrice10P.crop.Name + " "+ FarmulaPrice10P.qty.Qty + "@" + str(FarmulaPrice10P.Price) + "Ksh" + "\n"
        except :
            respsone = "END Sorry an error occurred, please try again later "

    elif text == '3':
        try :
            NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = '', PhoneNumber = phone_number, Address = '', IdCrop = FarmulaPrice20.crop.IdCrop, IdMarket = FarmulaPrice20.market.IdMarket, IdQty = FarmulaPrice20.qty.IdQty, IdOrderStatus = '1', Price = FarmulaPrice20.Price)
            db.session.add(NewOrder)
            db.session.commit()
            respsone = "END Thanks for using Farmula services to order " + FarmulaPrice20.crop.Name + " "+ FarmulaPrice20.qty.Qty + "@" + str(FarmulaPrice20.Price) + "Ksh" + "\n"
        except :
            respsone = "END Sorry an error occurred, please try again later "

    elif text == '4':
        try :
            NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = '', PhoneNumber = phone_number, Address = '', IdCrop = FarmulaPrice20P.crop.IdCrop, IdMarket = FarmulaPrice20P.market.IdMarket, IdQty = FarmulaPrice20P.qty.IdQty, IdOrderStatus = '1', Price = FarmulaPrice20P.Price)
            db.session.add(NewOrder)
            db.session.commit()
            respsone = "END Thanks for using Farmula services to order " + FarmulaPrice20P.crop.Name + " "+ FarmulaPrice20P.qty.Qty + "@" + str(FarmulaPrice20P.Price) + "Ksh" + "\n"
        except :
            respsone = "END Sorry an error occurred, please try again later "

    elif text == '5':
        try :
            NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = '', PhoneNumber = phone_number, Address = '', IdCrop = FarmulaPrice50.crop.IdCrop, IdMarket = FarmulaPrice50.market.IdMarket, IdQty = FarmulaPrice50.qty.IdQty, IdOrderStatus = '1', Price = FarmulaPrice50.Price)
            db.session.add(NewOrder)
            db.session.commit()
            respsone = "END Thanks for using Farmula services to order " + FarmulaPrice50.crop.Name + " "+ FarmulaPrice50.qty.Qty + "@" + str(FarmulaPrice50.Price) + "Ksh" + "\n"
        except :
            respsone = "END Sorry an error occurred, please try again later "

    elif text == '6':
        try :
            NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = '', PhoneNumber = phone_number, Address = '', IdCrop = FarmulaPrice90.crop.IdCrop, IdMarket = FarmulaPrice90.market.IdMarket, IdQty = FarmulaPrice90.qty.IdQty, IdOrderStatus = '1', Price = FarmulaPrice90.Price)
            db.session.add(NewOrder)
            db.session.commit()
            respsone = "END Thanks for using Farmula services to order " + FarmulaPrice90.crop.Name + " "+ FarmulaPrice90.qty.Qty + "@" + str(FarmulaPrice90.Price) + "Ksh" + "\n"
        except :
            respsone = "END Sorry an error occurred, please try again later "


    elif text == "7":
        respsone = "CON "
        respsone += "1. 50Kg \n"
        respsone += "2. 90Kg \n"
        respsone += "3. 120Kg \n"

    elif text == "7*1":
        respsone = "END Price in different markets \n"
        for MarketPrice in AllMarketPrice:
            if '50' in MarketPrice.qty.Qty and MarketPrice.market.Name != 'Farmula':
                PriceAll.append([MarketPrice.market.Name, MarketPrice.crop.Name ,MarketPrice.qty.Qty, MarketPrice.Price])
                respsone += " " + MarketPrice.crop.Name + " "+ MarketPrice.qty.Qty + "@" + MarketPrice.market.Name + "=" + str(MarketPrice.Price) + "Ksh" + "\n"
        try :
            CheckSession = Pricechecksession(PhoneNumber = phone_number, Hooks = text)
            db.session.add(CheckSession)
            db.session.commit()
        except :
            respsone = "END Sorry an error occurred, please try again later "

    elif text == "7*2":
        respsone = "END Price in different markets \n"
        for MarketPrice in AllMarketPrice:
            if '90' in MarketPrice.qty.Qty and MarketPrice.market.Name != 'Farmula':
                PriceAll.append([MarketPrice.market.Name, MarketPrice.crop.Name ,MarketPrice.qty.Qty, MarketPrice.Price])
                respsone += " " + MarketPrice.crop.Name + " "+ MarketPrice.qty.Qty + "@" + MarketPrice.market.Name + "=" + str(MarketPrice.Price) + "Ksh" + "\n"
        try :
            CheckSession = Pricechecksession(PhoneNumber = phone_number, Hooks = text)
            db.session.add(CheckSession)
            db.session.commit() 
        except :
            respsone = "END Sorry an error occurred, please try again later "


    elif text == "7*3":
        respsone = "END Price in different markets \n"
        for MarketPrice in AllMarketPrice:
            if '120' in MarketPrice.qty.Qty and MarketPrice.market.Name != 'Farmula':
                PriceAll.append([MarketPrice.market.Name, MarketPrice.crop.Name ,MarketPrice.qty.Qty, MarketPrice.Price])
                respsone += " " + MarketPrice.crop.Name + " "+ MarketPrice.qty.Qty + "@" + MarketPrice.market.Name + "=" + str(MarketPrice.Price) + "Ksh" + "\n"
        try :
            CheckSession = Pricechecksession(PhoneNumber = phone_number, Hooks = text)
            db.session.add(CheckSession)
            db.session.commit()  
        except :
            respsone = "END Sorry an error occurred, please try again later "

    return respsone
