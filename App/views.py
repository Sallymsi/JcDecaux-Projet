from flask import Flask, render_template
import requests
import folium
from folium import plugins
from .utils import *

app = Flask(__name__)

app.config.from_object("config")

@app.route("/")
def index():
    urlGlobal = "https://api.jcdecaux.com/vls/v1/stations?apiKey={key}".format(key = app.config['SECRET_KEY'])
    urlStation = "https://api.jcdecaux.com/vls/v3/contracts?apiKey={key}".format(key = app.config['SECRET_KEY'])

    responseGlobal = requests.get(urlGlobal, headers=app.config['HEADERS']).json()
    responseVilles = requests.get(urlStation, headers=app.config['HEADERS']).json()
    villes = []
    locations = []

    for info in responseVilles:
        isPresent = info["name"] in villes
        if not isPresent:
            villes.append(info["name"])

    villes.sort()

    m = folium.Map(
        location=[48.29649, 4.07360],
        zoom_start=5,
    )

    for info in responseGlobal:
        locations.append([info['position']['lat'], info["position"]["lng"], info['number'], info['contract_name'], info['available_bikes']])
    
    plugins.FastMarkerCluster(locations, callback=callbackIndex()).add_to(m)

    m.get_root().width = "100%"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    return render_template("index.html", iframe=iframe, villes=villes)

@app.route("/<contract>")
def city(contract):
    urlContract = "https://api.jcdecaux.com/vls/v3/stations?contract={contract}&apiKey={key}".format(contract = contract, key = app.config['SECRET_KEY'])

    response = requests.get(urlContract, headers=app.config['HEADERS']).json()
    stations = []
    locations = []


    m = folium.Map(
        location=[48.29649, 4.07360],
        zoom_start=5,
    ) 

    for info in response:
        locations.append([info['position']['latitude'], info["position"]["longitude"], info['number'], info['contractName'], info["totalStands"]["availabilities"]["bikes"], info["totalStands"]["availabilities"]["electricalBikes"], info["totalStands"]["availabilities"]["mechanicalBikes"]])
    
    plugins.FastMarkerCluster(locations, callback=callbackCity()).add_to(m)

    m.get_root().width = "100%"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    for info in response:
        isPresent = info['name'] in stations
        if not isPresent:
            stations.append(info)

    def myFunc(e):
        return e['number']
    
    stations.sort(key=myFunc)

    return render_template("city.html", infos=stations, iframe=iframe)

@app.route("/<contract>/<number>")
def station(contract, number):
    urlStation = "https://api.jcdecaux.com/vls/v3/stations/{station_number}?contract={contract_name}&apiKey={key}".format(station_number = number, contract_name = contract, key = app.config['SECRET_KEY'])

    response = requests.get(urlStation, headers=app.config['HEADERS']).json()

    m = folium.Map(
        location=[response["position"]["latitude"], response["position"]["longitude"]],
        zoom_start=20,
    )

    folium.Marker(
            [response["position"]["latitude"], response["position"]["longitude"]]
        ).add_to(m)

    m.get_root().width = "100%"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    return render_template("station.html", iframe=iframe, info=response, pourcentDispo=pourcentDispo(response), pourcentElec=pourcentElec(response))

@app.route("/classement")
def classement():
    urlGlobal = "https://api.jcdecaux.com/vls/v3/contracts?apiKey={key}".format(key = app.config['SECRET_KEY'])

    response = requests.get(urlGlobal, headers=app.config['HEADERS'])
    infos = response.json()

    stations = classementCity(infos)

    return render_template("classement.html", infos=infos, stations=stations)

@app.route("/classement/<contract>")
def statistique(contract):
    urlContract = "https://api.jcdecaux.com/vls/v3/stations?contract={contract}&apiKey={key}".format(contract = contract, key = app.config['SECRET_KEY'])
    contract = contract

    response = requests.get(urlContract, headers=app.config['HEADERS'])
    
    infos = response.json()

    return render_template("statistique.html", infos=classementStation(infos), contract=contract)