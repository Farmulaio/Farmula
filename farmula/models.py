from farmula import app, db

class Crop(db.Model):
    IdCrop = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(250), nullable=False)
    Enabled = db.Column(db.Integer, db.ForeignKey('situation.IdSituation'))
    CreatedAt = db.Column(db.DateTime, nullable=False)
    situation = db.relationship('Situation', backref='Crop')

    def __repr__(self) :
        return f"Crop('{self.IdCrop}','{self.Name},'{self.Enabled}','{self.CreatedAt}')"


class Situation(db.Model):
    IdSituation = db.Column(db.Integer, primary_key=True)
    Situation  = db.Column(db.String(250), nullable=False)
    CreatedAt  = db.Column(db.DateTime, nullable=False) 

    def __repr__(self) :
        return f"Situation('{self.IdSituation}','{self.Situation}','{self.CreatedAt}')"



class OrderStatus(db.Model):
    IdOrderStatus = db.Column(db.Integer, primary_key=True)
    OrderStatus  = db.Column(db.String(250), nullable=False)
    CreatedAt  = db.Column(db.DateTime, nullable=False) 

    def __repr__(self) :
        return f"OrderStatus('{self.IdOrderStatus}','{self.OrderStatus}','{self.CreatedAt}')"


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

class Orders(db.Model):
    IdOrder = db.Column(db.Integer, primary_key=True)
    OrderNumber = db.Column(db.String(250), nullable=True)
    BusinesName = db.Column(db.String(250), nullable=True)
    PhoneNumber = db.Column(db.String(250), nullable=True)
    Address = db.Column(db.String(250), nullable=True)
    IdCrop = db.Column(db.Integer, db.ForeignKey('crop.IdCrop'))
    IdMarket = db.Column(db.Integer, db.ForeignKey('market.IdMarket'))
    IdQty = db.Column(db.Integer, db.ForeignKey('quantity.IdQty'))
    IdOrderStatus  = db.Column(db.Integer, db.ForeignKey('order_status.IdOrderStatus'))
    Price  = db.Column(db.String(250), nullable=True)
    CreatedAt = db.Column(db.DateTime, nullable=False)
    crop = db.relationship("Crop", backref="Orders") 
    market = db.relationship("Market", backref="Orders")
    qty = db.relationship("Quantity", backref="Orders")
    orderstatus = db.relationship("OrderStatus", backref="Orders")


    def __repr__(self) :
        return f"Orders('{self.IdOrder}',{self.OrderNumber}','{self.BusinesName}','{self.PhoneNumber}','{self.Address}','{self.IdCrop}','{self.IdMarket}','{self.IdQty}'),'{self.IdOrderStatus}'),'{self.Price}','{self.CreatedAt}')"


class Price(db.Model):
    IdPrice = db.Column(db.Integer, primary_key=True)
    IdCrop = db.Column(db.Integer, db.ForeignKey('crop.IdCrop'))
    IdMarket = db.Column(db.Integer, db.ForeignKey('market.IdMarket'))
    IdQty = db.Column(db.Integer, db.ForeignKey('quantity.IdQty'))
    Price  = db.Column(db.String(250), nullable=True)
    CreatedAt = db.Column(db.DateTime, nullable=False)
    crop = db.relationship("Crop", backref="Price") 
    market = db.relationship("Market", backref="Price")
    qty = db.relationship("Quantity", backref="Price")

    def __repr__(self) :
        return f"Price('{self.IdPrice}',{self.IdCrop}','{self.IdMarket}','{self.IdQty}','{self.Price}','{self.CreatedAt}')"        


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