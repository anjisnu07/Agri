# Importing essential libraries and modules

from flask import Flask, render_template, request
import numpy as np
import requests
import config
import pickle
import joblib  # Import joblib for model persistence


crop_recommendation_model_path = 'models/RandomForest.pkl'

# Load the model using joblib instead of pickle
crop_recommendation_model = joblib.load(crop_recommendation_model_path)

# Define the function to fetch weather data
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

# Render home page
@app.route('/')
def home():
    return render_template('crop.html')

# Render crop recommendation form page
@app.route('/crop-recommend')
def crop_recommend():
    return render_template('crop.html')

@app.route('/crop-predict', methods=['POST'])
def crop_prediction():
    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        city = request.form.get("city")

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = crop_recommendation_model.predict(data)
            final_prediction = my_prediction[0]

            return render_template('crop-result.html', prediction=final_prediction)

        else:
            return render_template('try_again.html')

if __name__ == '__main__':
    app.run(debug=True)
