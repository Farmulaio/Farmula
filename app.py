from farmula import app 

# app = Flask(__name__)
# db = pymysql.connect("localhost","root","ahmed@12345","farmula_dashboard")

# response = ""
# apikey = "1R4mWJ92xj2R37hvydNj8qvNREL_au-0NQfhOK35O6uS"

# # Get an IAM token from IBM Cloud
# url     = "https://iam.bluemix.net/oidc/token"
# headers = { "Content-Type" : "application/x-www-form-urlencoded" }
# data    = "apikey=" + apikey + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
# IBM_cloud_IAM_uid = "bx"
# IBM_cloud_IAM_pwd = "bx"
# response  = requests.post( url, headers=headers, data=data, auth=( IBM_cloud_IAM_uid, IBM_cloud_IAM_pwd ) )
# iam_token = response.json()["access_token"]

# header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + iam_token, 'ML-Instance-ID': "6a216236-adcc-48b5-901f-41e4cafbf033"}

# today = datetime.date.today()





# @app.route('/ussd', methods=['GET','POST'])
# def ussd_callback():
#     global response
#     session_id = request.values.get("sessionId", None)
#     service_code = request.values.get("serviceCode", None)
#     phone_number = request.values.get("phoneNumber", None)
#     text =  request.values.get("text", "default")


if __name__ == '__main__':
    app.secret_key = 'farmula'
    app.run(debug=True)