from farmula import app, db
from farmula.forms import PredicitForm , OrderForm
from flask import redirect, url_for, render_template, request
import urllib3, json, requests, calendar, random, string
from datetime import datetime
from farmula.models import Crop, Quantity, Market, Price, Orders, Prediction, Pricechecksession, Farmer
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

    for PriceItem in AllMarketPrice:
        if PriceItem.market.Name == 'Farmula' and  PriceItem.qty.Qty == '10kg':
            PriceFarmula10.append([PriceItem.market.Name, PriceItem.crop.Name ,PriceItem.qty.Qty, PriceItem.Price])
            res_10 = " "+ PriceItem.qty.Qty + "(" + str(PriceItem.Price) + "Ksh)" + "\n"
        # else :
        #     res_10 = "Sorry 10k price is not available \n"

    for PriceItem in AllMarketPrice:
        if PriceItem.market.Name == 'Farmula' and PriceItem.qty.Qty == '10kg peeled':
            PriceFarmula10.append([PriceItem.market.Name, PriceItem.crop.Name ,PriceItem.qty.Qty, PriceItem.Price])
            res_10p = " "+ PriceItem.qty.Qty + "(" + str(PriceItem.Price) + "Ksh)" + "\n"
        else :
           res_10p = "Sorry 10k Peeled price is not available \n"

        # elif PriceItem.market.Name == 'Farmula' and PriceItem.qty.Qty == '20kg':
        #     PriceFarmula10.append([PriceItem.market.Name, PriceItem.crop.Name ,PriceItem.qty.Qty, PriceItem.Price])
        #     respsone += "3. "+ " "+ PriceItem.qty.Qty + "(" + str(PriceItem.Price) + "Ksh)" + "\n"
        
    for PriceItem in AllMarketPrice:
        if PriceItem.market.Name == 'Farmula' and  PriceItem.qty.Qty == '20kg peeled':
            PriceFarmula10.append([PriceItem.market.Name, PriceItem.crop.Name ,PriceItem.qty.Qty, PriceItem.Price])
            res_20p = " "+ PriceItem.qty.Qty + "(" + str(PriceItem.Price) + "Ksh)" + "\n"  
        else :
            res_20p = "Sorry 20k Peeled price is not available \n"

        # elif PriceItem.market.Name == 'Farmula' and '50'  in PriceItem.qty.Qty :
        #     if not PriceItem.Price :
        #         respsone += "5. 50kg price for today is unavilable"
        #     else:
        #         PriceFarmula10.append([PriceItem.market.Name, PriceItem.crop.Name ,PriceItem.qty.Qty, PriceItem.Price])
        #         respsone += "5. "+ " "+ PriceItem.qty.Qty + "(" + str(PriceItem.Price) + "Ksh)" + "\n"

        # elif PriceItem.market.Name == 'Farmula' and '90'  in PriceItem.qty.Qty :
        #     PriceFarmula10.append([PriceItem.market.Name, PriceItem.crop.Name ,PriceItem.qty.Qty, PriceItem.Price])
        #     respsone += "6. "+ " "+ PriceItem.qty.Qty + "(" + str(PriceItem.Price) + "Ksh)" + "\n"

    
    if text == "":
        if not AllMarketPrice :
            respsone = "END Welcome to Farmula \n Sorry today prices are not availabe yet"
        else :
            respsone = "CON Welcome to Farmula , order for  \n"
            respsone += "1. "+ res_10
            respsone += "2. "+ res_10
            respsone += "3. "+ res_10
            respsone += "4. "+ res_20p
            respsone += "5. "+ res_10
            respsone += "6. "+ res_10
            respsone += "7. Check other prices \n"
    
    # elif text == '1':
    #     for PriceItem in AllMarketPrice:
    #         if  PriceItem.market.Name == 'Farmula' and  PriceItem.qty.Qty == '10kg' :
    #             PriceFarmula10.append([PriceItem.market.Name, PriceItem.crop.Name ,PriceItem.qty.Qty, PriceItem.Price])
    #             try :
    #                 NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = '', PhoneNumber = phone_number, Address = '', IdCrop = PriceItem.crop.IdCrop, IdMarket = PriceItem.market.IdMarket, IdQty = PriceItem.qty.IdQty, IdOrderStatus = '1', Price = PriceItem.Price)
    #                 db.session.add(NewOrder)
    #                 db.session.commit()
    #                 respsone = "END Thanks for using Farmula services to order " + PriceItem.crop.Name + " "+ PriceItem.qty.Qty + "@" + str(PriceItem.Price) + "Ksh" + "\n"
    #             except :
    #                 respsone = "END Sorry an error occurred, please try again later "

    # elif text == '2':
    #     for PriceItem in AllMarketPrice:
    #         if  PriceItem.market.Name == 'Farmula' and PriceItem.qty.Qty == '10kg peeled' :
    #             PriceFarmula10.append([PriceItem.market.Name, PriceItem.crop.Name ,PriceItem.qty.Qty, PriceItem.Price])
    #             try :
    #                 NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = '', PhoneNumber = phone_number, Address = '', IdCrop = PriceItem.crop.IdCrop, IdMarket = PriceItem.market.IdMarket, IdQty = PriceItem.qty.IdQty, IdOrderStatus = '1', Price = PriceItem.Price)
    #                 db.session.add(NewOrder)
    #                 db.session.commit()
    #                 respsone = "END Thanks for using Farmula services to order " + PriceItem.crop.Name + " "+ PriceItem.qty.Qty + "@" + str(PriceItem.Price) + "Ksh" + "\n"
    #             except :
    #                 respsone = "END Sorry an error occurred, please try again later "

    # elif text == '3':
    #     for PriceItem in AllMarketPrice:
    #         if  PriceItem.market.Name == 'Farmula' and PriceItem.qty.Qty == '20kg' :
    #             PriceFarmula10.append([PriceItem.market.Name, PriceItem.crop.Name ,PriceItem.qty.Qty, PriceItem.Price])
    #             try :
    #                 NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = '', PhoneNumber = phone_number, Address = '', IdCrop = PriceItem.crop.IdCrop, IdMarket = PriceItem.market.IdMarket, IdQty = PriceItem.qty.IdQty, IdOrderStatus = '1', Price = PriceItem.Price)
    #                 db.session.add(NewOrder)
    #                 db.session.commit()
    #                 respsone = "END Thanks for using Farmula services to order " + PriceItem.crop.Name + " "+ PriceItem.qty.Qty + "@" + str(PriceItem.Price) + "Ksh" + "\n"
    #             except :
    #                 respsone = "END Sorry an error occurred, please try again later "

    # elif text == '4':
    #     for PriceItem in AllMarketPrice:
    #         if  PriceItem.market.Name == 'Farmula' and  PriceItem.qty.Qty == '20kg peeled' :
    #             PriceFarmula10.append([PriceItem.market.Name, PriceItem.crop.Name ,PriceItem.qty.Qty, PriceItem.Price])
    #             try :
    #                 NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = '', PhoneNumber = phone_number, Address = '', IdCrop = PriceItem.crop.IdCrop, IdMarket = PriceItem.market.IdMarket, IdQty = PriceItem.qty.IdQty, IdOrderStatus = '1', Price = PriceItem.Price)
    #                 db.session.add(NewOrder)
    #                 db.session.commit()
    #                 respsone = "END Thanks for using Farmula services to order " + PriceItem.crop.Name + " "+ PriceItem.qty.Qty + "@" + str(PriceItem.Price) + "Ksh" + "\n"
    #             except :
    #                 respsone = "END Sorry an error occurred, please try again later "

    # elif text == '5':
    #     for PriceItem in AllMarketPrice:
    #         if  PriceItem.market.Name == 'Farmula' and '50'  in PriceItem.qty.Qty :
    #             PriceFarmula10.append([PriceItem.market.Name, PriceItem.crop.Name ,PriceItem.qty.Qty, PriceItem.Price])
    #             try :
    #                 NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = '', PhoneNumber = phone_number, Address = '', IdCrop = PriceItem.crop.IdCrop, IdMarket = PriceItem.market.IdMarket, IdQty = PriceItem.qty.IdQty, IdOrderStatus = '1', Price = PriceItem.Price)
    #                 db.session.add(NewOrder)
    #                 db.session.commit()
    #                 respsone = "END Thanks for using Farmula services to order " + PriceItem.crop.Name + " "+ PriceItem.qty.Qty + "@" + str(PriceItem.Price) + "Ksh" + "\n"
    #             except :
    #                 respsone = "END Sorry an error occurred, please try again later "

    # elif text == '6':
    #     for PriceItem in AllMarketPrice:
    #         if  PriceItem.market.Name == 'Farmula' and '90'  in PriceItem.qty.Qty :
    #             PriceFarmula10.append([PriceItem.market.Name, PriceItem.crop.Name ,PriceItem.qty.Qty, PriceItem.Price])
    #             try :
    #                 NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = '', PhoneNumber = phone_number, Address = '', IdCrop = PriceItem.crop.IdCrop, IdMarket = PriceItem.market.IdMarket, IdQty = PriceItem.qty.IdQty, IdOrderStatus = '1', Price = PriceItem.Price)
    #                 db.session.add(NewOrder)
    #                 db.session.commit()
    #                 respsone = "END Thanks for using Farmula services to order " + PriceItem.crop.Name + " "+ PriceItem.qty.Qty + "@" + str(PriceItem.Price) + "Ksh" + "\n"
    #             except :
    #                 respsone = "END Sorry an error occurred, please try again later "


    # elif text == "7":
    #     respsone = "CON "
    #     respsone += "1. 50Kg \n"
    #     respsone += "2. 90Kg \n"
    #     respsone += "3. 120Kg \n"

    # elif text == "7*1":
    #     respsone = "END Price in different markets \n"
    #     for MarketPrice in AllMarketPrice:
    #         if '50' in MarketPrice.qty.Qty and MarketPrice.market.Name != 'Farmula':
    #             PriceAll.append([MarketPrice.market.Name, MarketPrice.crop.Name ,MarketPrice.qty.Qty, MarketPrice.Price])
    #             respsone += " " + MarketPrice.crop.Name + " "+ MarketPrice.qty.Qty + "@" + MarketPrice.market.Name + "=" + str(MarketPrice.Price) + "Ksh" + "\n"
    #     try :
    #         CheckSession = Pricechecksession(PhoneNumber = phone_number, Hooks = text)
    #         db.session.add(CheckSession)
    #         db.session.commit()
    #     except :
    #         respsone = "END Sorry an error occurred, please try again later "

    # elif text == "7*2":
    #     respsone = "END Price in different markets \n"
    #     for MarketPrice in AllMarketPrice:
    #         if '90' in MarketPrice.qty.Qty and MarketPrice.market.Name != 'Farmula':
    #             PriceAll.append([MarketPrice.market.Name, MarketPrice.crop.Name ,MarketPrice.qty.Qty, MarketPrice.Price])
    #             respsone += " " + MarketPrice.crop.Name + " "+ MarketPrice.qty.Qty + "@" + MarketPrice.market.Name + "=" + str(MarketPrice.Price) + "Ksh" + "\n"
    #     try :
    #         CheckSession = Pricechecksession(PhoneNumber = phone_number, Hooks = text)
    #         db.session.add(CheckSession)
    #         db.session.commit() 
    #     except :
    #         respsone = "END Sorry an error occurred, please try again later "


    # elif text == "7*3":
    #     respsone = "END Price in different markets \n"
    #     for MarketPrice in AllMarketPrice:
    #         if '120' in MarketPrice.qty.Qty and MarketPrice.market.Name != 'Farmula':
    #             PriceAll.append([MarketPrice.market.Name, MarketPrice.crop.Name ,MarketPrice.qty.Qty, MarketPrice.Price])
    #             respsone += " " + MarketPrice.crop.Name + " "+ MarketPrice.qty.Qty + "@" + MarketPrice.market.Name + "=" + str(MarketPrice.Price) + "Ksh" + "\n"
    #     try :
    #         CheckSession = Pricechecksession(PhoneNumber = phone_number, Hooks = text)
    #         db.session.add(CheckSession)
    #         db.session.commit()  
    #     except :
    #         respsone = "END Sorry an error occurred, please try again later "

    return respsone
