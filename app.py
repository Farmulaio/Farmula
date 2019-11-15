from farmula import app 

if __name__ == '__main__':
    app.secret_key = 'farmula'
    app.run(debug=True)