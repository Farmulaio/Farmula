from wtforms import Form, StringField, IntegerField, validators, SelectField, DateField


class PredicitForm(Form):
    crop = SelectField(u'Pick a Crop', choices=[('1', 'Red Irish Patoto'), ('2', 'White Irish Patoto')])
    month = SelectField(u'Pick a Month', choices=[('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'Novmber'), ('12', 'December')])
    day = IntegerField(u'Enter a Day', [validators.NumberRange(min=1, max=31)])
    year = IntegerField(u'Enter a Year', [validators.NumberRange(min=1970, max=2050)])


class OrderForm(Form):
    produce = SelectField(u'Pick a Crop', choices=[('Red Irish Patoto', 'Red Irish Patoto'), ('White Irish Patoto', 'White Irish Patoto')])
    qty = SelectField(u'Pick a Quantity', choices=[('50kg', '50kg Bag'), ('90kg', '90kg Bag')])
    customer_name = StringField(u'Enter your name', [validators.required()])
    phone_number = StringField(u'Enter your phone number', [validators.Length(min=10)])
    customer_address = StringField(u'Enter your address', [validators.required()])