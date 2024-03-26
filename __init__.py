from flask import Flask, render_template_string, render_template, jsonify
from flask import render_template
from flask import json
from datetime import datetime
from urllib.request import urlopen
from io import BytesIO
import sqlite3
import requests
import matplotlib.pyplot as plt
import base64

                                                                                                                                       
app = Flask(__name__)                                                                                                                  

owner = 'Lucas-FB'
repo = '5MCSI_Metriques'
token = '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'

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route('/tawarano/')
def meteo():
    response = urlopen('https://samples.openweathermap.org/data/2.5/forecast?lat=0&lon=0&appid=xxx')
    raw_content = response.read()
    json_content = json.loads(raw_content.decode('utf-8'))
    results = []
    for list_element in json_content.get('list', []):
        dt_value = list_element.get('dt')
        temp_day_value = list_element.get('main', {}).get('temp') - 273.15 # Conversion de Kelvin en °c 
        results.append({'Jour': dt_value, 'temp': temp_day_value})
    return jsonify(results=results)

@app.route("/rapport/")
def mongraphique():
    return render_template("graphique.html")

@app.route("/histogramme/")
def histogramme():
    return render_template("histogramme.html")

@app.route("/commits/")
def commits():
    try:
        headers = {'Authorization': f'token {token}'}
        url = f'https://api.github.com/repos/{owner}/{repo}/commits'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            commits = response.json()
            timestamps = [datetime.strptime(commit['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ") for commit in commits]
            # Création d'un histogramme des commits par minute
            minutes = [timestamp.minute + timestamp.hour * 60 for timestamp in timestamps]
            bins = max(minutes) - min(minutes) + 1
            plt.hist(minutes, bins=bins, edgecolor='black', linewidth=1.2)
            plt.xlabel('Temps écoulé (minutes)')
            plt.ylabel('Nombre de commits')
            plt.title('Nombre de commits par minute')
            # Conversion du graphique en base64 pour l'afficher dans la page HTML
            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            graph_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
            return render_template('commits.html', graph_url=graph_url)
        else:
            return 'Error fetching commits', 500
    except Exception as e:
        return str(e), 500
  
if __name__ == "__main__":
  app.run(debug=True)
