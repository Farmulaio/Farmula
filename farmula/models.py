from farmula import app, db

class Crop(db.Model):
    IdCrop = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(250), nullable=False)
    Enabled = db.Column(db.Integer, db.ForeignKey('situation.IdSituation'))
    CreatedAt = db.Column(db.DateTime, nullable=False)
    situation = db.relationship('Situation', backref='Crop')

    def __repr__(self) :
        return f"Crop('{self.IdCrop}','{self.Name},'{self.Enabled}','{self.CreatedAt}')"


class Market(db.Model):
    IdMarket = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(250), nullable=False)
    Enabled = db.Column(db.Integer, db.ForeignKey('situation.IdSituation'))
    CreatedAt = db.Column(db.DateTime, nullable=False) 
    situation = db.relationship('Situation', backref='Market')


    def __repr__(self) :
        return f"Market('{self.IdMarket}','{self.Name},'{self.Enabled}','{self.CreatedAt}')"



class Quantity(db.Model):
    IdQty = db.Column(db.Integer, primary_key=True)
    Qty = db.Column(db.String(250), nullable=False)
    Enabled = db.Column(db.Integer, db.ForeignKey('situation.IdSituation'))
    CreatedAt = db.Column(db.DateTime, nullable=False) 
    situation = db.relationship('Situation', backref='Quantity')


    def __repr__(self) :
        return f"Quantity('{self.IdQty}','{self.Qty},'{self.Enabled}','{self.CreatedAt}')"



class Farmer(db.Model):
    Idfarmer = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(250), nullable=True)
    LastName = db.Column(db.String(250), nullable=True)
    PhoneNumber = db.Column(db.String(250), nullable=True)
    Address = db.Column(db.String(250), nullable=True)
    IdCrop = db.Column(db.Integer , db.ForeignKey('crop.IdCrop'))
    Harvestime = db.Column(db.String(250), nullable=True)
    CreatedAt = db.Column(db.DateTime, nullable=False) 
    crop = db.relationship('Crop',  backref="Farmer")

    def __repr__(self) :
        return f"Farmer('{self.Idfarmer}',{self.FirstName}','{self.LastName}','{self.PhoneNumber}','{self.Address}','{self.IdCrop}','{self.Harvestime}','{self.CreatedAt}')"        

class Conditions(db.Model):
    IdCondition = db.Column(db.Integer, primary_key=True)
    ConditionName = db.Column(db.String(250), nullable=False)
    CreatedAt  = db.Column(db.DateTime, nullable=False) 

    def __repr__(self) :
        return f"Conditions('{self.IdCondition}','{self.ConditionName}','{self.CreatedAt}')"



class Business(db.Model):
    IdBusines = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(250), nullable=True)
    LastName = db.Column(db.String(250), nullable=True)
    Email = db.Column(db.String(250), nullable=True)
    PhoneNumber = db.Column(db.String(250), nullable=True)
    Address = db.Column(db.String(250), nullable=True)
    BusinesName = db.Column(db.String(250), nullable=True)
    CreatedAt = db.Column(db.DateTime, nullable=False) 

    def __repr__(self) :
        return f"Business('{self.IdBusines}',{self.FirstName}','{self.LastName}','{self.Email}','{self.PhoneNumber}','{self.Address}','{self.BusinesName}','{self.CreatedAt}')"        

class Price(db.Model):
    IdPrice = db.Column(db.Integer, primary_key=True)
    IdCrop = db.Column(db.Integer, db.ForeignKey('crop.IdCrop'))
    IdMarket = db.Column(db.Integer, db.ForeignKey('market.IdMarket'))
    IdQty = db.Column(db.Integer, db.ForeignKey('quantity.IdQty'))
    IdCondition = db.Column(db.Integer, db.ForeignKey('conditions.IdCondition'))
    IdUser  = db.Column(db.Integer, db.ForeignKey('users.IdUser'))
    Price  = db.Column(db.String(250), nullable=True)
    CreatedAt = db.Column(db.DateTime, nullable=False)
    crop = db.relationship("Crop", backref="Price") 
    market = db.relationship("Market", backref="Price")
    qty = db.relationship("Quantity", backref="Price")
    co = db.relationship("Conditions", backref="Price")

    def __repr__(self) :
        return f"Price('{self.IdPrice}',{self.IdCrop}','{self.IdMarket}','{self.IdQty}','{self.IdCondition}','{self.IdUser}','{self.Price}','{self.CreatedAt}')"        

class Pricechecksession(db.Model):
    IdSession = db.Column(db.Integer, primary_key=True)
    PhoneNumber = db.Column(db.String(250), db.ForeignKey('business.PhoneNumber'))
    Hooks = db.Column(db.String(250), nullable=False)
    CreatedAt = db.Column(db.DateTime, nullable=False) 
    business = db.relationship("Business", backref="Pricechecksession") 

    def __repr__(self) :
        return f"Pricechecksession('{self.IdSession}','{self.PhoneNumber}','{self.Hooks}','{self.CreatedAt}')"

class Pricemechsession(db.Model):
    IdSession = db.Column(db.Integer, primary_key=True)
    PhoneNumber = db.Column(db.String(250), nullable=False)
    Name = db.Column(db.String(250))
    Hooks = db.Column(db.Integer, nullable=False)
    CreatedAt = db.Column(db.DateTime, nullable=False) 

    def __repr__(self) :
        return f"Pricemechsession('{self.IdSession}','{self.PhoneNumber},'{self.Name}','{self.Hooks}','{self.CreatedAt}')"

class Situation(db.Model):
    IdSituation = db.Column(db.Integer, primary_key=True)
    Situation  = db.Column(db.String(250), nullable=False)
    CreatedAt  = db.Column(db.DateTime, nullable=False) 

    def __repr__(self) :
        return f"Situation('{self.IdSituation}','{self.Situation}','{self.CreatedAt}')"


class Orders(db.Model):
    IdOrder = db.Column(db.Integer, primary_key=True)
    OrderNumber = db.Column(db.String(250), nullable=True)
    BusinesName = db.Column(db.String(250), nullable=True)
    PhoneNumber = db.Column(db.String(250), nullable=True)
    Address = db.Column(db.String(250),  nullable=True)
    IdBusines = db.Column(db.Integer, db.ForeignKey('business.IdBusines'))
    IdCrop = db.Column(db.Integer, db.ForeignKey('crop.IdCrop'))
    IdQty = db.Column(db.Integer, db.ForeignKey('quantity.IdQty'))
    IdOrderStatus  = db.Column(db.Integer, db.ForeignKey('order_status.IdOrderStatus'))
    Price  = db.Column(db.String(250), nullable=True)
    Logistic  = db.Column(db.String(250), nullable=True)
    Ordertime = db.Column(db.String(250), nullable=True)
    CreatedAt = db.Column(db.DateTime, nullable=False)
    crop = db.relationship("Crop", backref="Orders") 
    qty = db.relationship("Quantity", backref="Orders")
    orderstatus = db.relationship("OrderStatus", backref="Orders")
    business = db.relationship("Business", backref="Orders") 

    def __repr__(self) :
        return f"Orders('{self.IdOrder}',{self.OrderNumber}','{self.BusinesName}','{self.PhoneNumber}','{self.Address}','{self.IdBusines}','{self.IdCrop}','{self.IdQty}','{self.IdOrderStatus}','{self.Price}','{self.Ordertime}','{self.CreatedAt}')"        

class OrderStatus(db.Model):
    IdOrderStatus = db.Column(db.Integer, primary_key=True)
    OrderStatus  = db.Column(db.String(250), nullable=False)
    CreatedAt  = db.Column(db.DateTime, nullable=False) 

    def __repr__(self) :
        return f"OrderStatus('{self.IdOrderStatus}','{self.OrderStatus}','{self.CreatedAt}')"


class Prediction(db.Model):
    IdPred = db.Column(db.Integer, primary_key=True)
    IdCrop = db.Column(db.Integer, db.ForeignKey('crop.IdCrop'))
    PredictionDate  = db.Column(db.String(250), nullable=False)
    AvgPrice = db.Column(db.String(250), nullable=False)
    PrePrice  = db.Column(db.String(250), nullable=False)
    CreatedAt = db.Column(db.DateTime, nullable=False) 
    crop = db.relationship("Crop", backref="Prediction") 


    def __repr__(self) :
        return f"Prediction('{self.IdPred}','{self.IdCrop},'{self.PredictionDate},'{self.AvgPrice}','{self.PrePrice}','{self.CreatedAt}')"


class Sales(db.Model):
    IdSale = db.Column(db.Integer, primary_key=True)
    IdOrder = db.Column(db.Integer, db.ForeignKey('orders.IdOrder'))
    Price  = db.Column(db.String(250), nullable=True)
    Paid  = db.Column(db.String(250),  nullable=True)
    CreatedAt = db.Column(db.DateTime, nullable=False) 
    order = db.relationship("Orders", backref="Sales") 


    def __repr__(self) :
        return f"Sales('{self.IdSale}','{self.IdOrder},'{self.Price}','{self.Paid}','{self.CreatedAt}')"
