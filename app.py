
from flask import Flask, render_template, request
import numpy as np
import requests
import config
import pickle
import pandas as pd
import os
from utils.fertilizer import fertilizer_dic

crop_recommendation_model_path = 'models\RandomForest.pkl'
crop_recommendation_model = pickle.load(
    open(crop_recommendation_model_path, 'rb'))


def weather_fetch(city_name):
    api_key = config.weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None




app = Flask(__name__)




@ app.route('/')
def home():
    
    return render_template('crop.html')



@ app.route('/crop-recommend')
def crop_recommend():
    return render_template('crop.html')

@ app.route('/fertilizer')
def fertilizer_recommendation():
    return render_template('fertilizer.html')


@ app.route('/crop-predict', methods=['POST'])
def crop_prediction():
    

    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # state = request.form.get("stt")
        city = request.form.get("city")

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = crop_recommendation_model.predict(data)
            final_prediction = my_prediction[0]

            return render_template('crop-result.html', prediction=final_prediction)

        else:
            return render_template('try_again.html')
        
@ app.route('/fertilizer-predict', methods=['POST'])
def fert_recommend():

    crop_name = str(request.form['cropname'])
    N = int(request.form['nitrogen'])
    P = int(request.form['phosphorous'])
    K = int(request.form['pottasium'])
    # ph = float(request.form['ph'])
    file_path = os.path.join('app', 'Data', 'fertilizer.csv')
    df = pd.read_csv(file_path)

    nr = df[df['Crop'] == crop_name]['N'].iloc[0]
    pr = df[df['Crop'] == crop_name]['P'].iloc[0]
    kr = df[df['Crop'] == crop_name]['K'].iloc[0]

    n = nr - N
    p = pr - P
    k = kr - K
    recommendations = []

    if not (-10 <= n <= 10):
        if n < -10:
            recommendations.append('NHigh')
            
        else:
            recommendations.append('Nlow')

        

    if not (-10 <= p <= 10):
        if p < -10:
            recommendations.append('PHigh')
        else:
            recommendations.append('Plow')
        

    if not (-10 <= k <= 10):
        if k < -10:
            recommendations.append('KHigh')
        else:
            recommendations.append('Klow')
        
    if not recommendations:
        return render_template('fertilizer-result.html', recommendation="Your ground is perfect for this crop")
    else:
        response = ''
        for key in recommendations:
            response+=str(fertilizer_dic[key])

        return render_template('fertilizer-result.html', recommendation=response)


if __name__ == '__main__':
    app.run(debug=True)
