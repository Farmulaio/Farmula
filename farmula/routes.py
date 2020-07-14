from farmula import app, db
from farmula.forms import PredicitForm , OrderForm
from flask import redirect, url_for, render_template, request, make_response
import urllib3, json, requests, calendar, random, string
from datetime import datetime
from farmula.models import Crop, Quantity, Market, Price, Orders, Prediction, Pricechecksession, Farmer, Sales, Conditions, Blog, BlogType
from farmula import config
from datetime import timedelta
import os

response = ""

def random_string_generator(size=5,  chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# index route 
@app.route('/', methods=['GET','POST'])
def index():
    BlogTypeItems = db.session.query(BlogType).all()
    BlogItems = db.session.query(Blog).all() 
    for item in BlogItems :
        print(item.ImageUrl)
    return render_template('index.html', BlogItems = BlogItems)


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
        # response_scoring = requests.post('https://eu-gb.ml.cloud.ibm.com/v3/wml_instances/6a216236-adcc-48b5-901f-41e4cafbf033/deployments/2736cd44-a971-40d8-ba07-f8014ab77d44/online', json=payload_scoring, headers= config.header)
        response_scoring = requests.post('https://eu-gb.ml.cloud.ibm.com/v3/wml_instances/6a216236-adcc-48b5-901f-41e4cafbf033/deployments/d8067440-47a9-443a-b3a8-25fea1151c6b/online', json=payload_scoring, headers=config.header)
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
            NewOrder = Orders(OrderNumber = "O"+random_string_generator(), BusinesName = request.form['BusinesName'], PhoneNumber = request.form['PhoneNumber'], Address = request.form['Address'] , IdBusines = 0, IdCrop = request.form['Crop'], IdQty = request.form['Qty'], Amount = request.form['amount'], IdOrderStatus = 1, Price = 20192.0 , Logistic = 0.0, Ordertime = str(datetime.date(datetime.now())))
            try :
                db.session.add(NewOrder)
                db.session.commit()
    
                NewSale = Sales(DocumentNumber = NewOrder.OrderNumber, IdBusines = NewOrder.IdBusines, Price = NewOrder.Price, Amount = NewOrder.Amount, PhoneNumber = '' , PaidAmount = 0.0, PaymentDate = '')
                db.session.add(NewSale)
                db.session.commit()

            except :
                return redirect(url_for('index'))

        return redirect(url_for('index'))

# farmer route 
@app.route('/partner', methods=['GET','POST'])
def partner():
    FarmerItems = db.session.query(Farmer).all()
    CropItems = db.session.query(Crop).filter_by(Enabled = 1).all()
    if request.method == 'POST':
        NewFarmer = Farmer(FirstName = request.form['FirstName'], LastName = request.form['LastName'], PhoneNumber = request.form['PhoneNumber'], Address = request.form['Address'], Crop = request.form['Crop'], Partner = request.form['Partner'])
        try :
            db.session.add(NewFarmer)
            db.session.commit()
            return redirect(url_for('index'))
        except :          
            return redirect(url_for('index'))

    return render_template('farmer.html', FarmerItems = FarmerItems, CropItems = CropItems)

# @app.route('/robots.txt')
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    try:
      """Generate sitemap.xml. Makes a list of urls and date modified."""
      pages=[]
      ten_days_ago=(datetime.now() - timedelta(days=7)).date().isoformat()
      # static pages
      for rule in app.url_map.iter_rules():
          if "GET" in rule.methods and len(rule.arguments)==0:
              pages.append(
                           ["https://farmula.io"+str(rule.rule),ten_days_ago]
                           )

      sitemap_xml = render_template('sitemap_template.xml', pages=pages)
      response= make_response(sitemap_xml)
      response.headers["Content-Type"] = "application/xml"    
    
      return response
    except Exception as e:
        return(str(e))	 

@app.route('/blog/<int:IdBlog>/view', methods=['POST', 'GET'])
def view_blog(IdBlog):
    if request.method == 'GET' :
        ViewBlog = db.session.query(Blog).filter_by(IdBlog = IdBlog).one()
        return render_template('blog.html',ViewBlog = ViewBlog)
    else :
        return redirect(url_for('index'))


@app.route('/blogs', methods=['POST', 'GET'])
def view_blogs():
    if request.method == 'GET':
        BlogItems = db.session.query(Blog).all()
        return render_template('blogs.html',BlogItems = BlogItems)
    else :
        return redirect(url_for('index')) 