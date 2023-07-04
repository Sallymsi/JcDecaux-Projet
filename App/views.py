from flask import Flask, render_template
import requests
import folium
from folium import plugins

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
        prefer_canvas=True,
    )

    callback = ('function (row) {' 
                'var marker = L.marker(new L.LatLng(row[0], row[1]));'
                'var icon = L.AwesomeMarkers.icon({'
                "icon: 'info-sign',"
                "iconColor: 'white',"
                "markerColor: 'blue',"
                "prefix: 'glyphicon',"
                "extraClasses: 'fa-rotate-0'"
                    '});'
                'marker.setIcon(icon);'
                "var popup = L.popup({maxWidth: '300'});"
                "const display_number = {text: row[2]};"
                "const display_contract = {text: row[3]};"
                "const display_bike = {text: row[4]};"
                "var mytext = $(`<div id='mytext' class='display_text' style='width: 100.0%; height: 100.0%;'> Ville : ${display_contract.text} <br> Arrêt : ${display_number.text} <br> Vélo(s) disponible(s) : ${display_bike.text}</div>`)[0];"
                "popup.setContent(mytext);"
                "marker.bindPopup(popup);"
                'return marker};')

    for info in responseGlobal:
        locations.append([info['position']['lat'], info["position"]["lng"], info['number'], info['contract_name'], info['available_bikes']])
    
    plugins.FastMarkerCluster(locations, callback=callback).add_to(m)

    m.get_root().width = "100%"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    return render_template("index.html", iframe=iframe, villes=villes)

@app.route("/<city>")
def city(city):
    urlContract = "https://api.jcdecaux.com/vls/v3/stations?contract={city}&apiKey={key}".format(city = city, key = app.config['SECRET_KEY'])

    response = requests.get(urlContract, headers=app.config['HEADERS']).json()
    stations = []
    locations = []

    callback = ('function (row) {' 
                'var marker = L.marker(new L.LatLng(row[0], row[1]));'
                'var icon = L.AwesomeMarkers.icon({'
                "icon: 'info-sign',"
                "iconColor: 'white',"
                "markerColor: 'blue',"
                "prefix: 'glyphicon',"
                "extraClasses: 'fa-rotate-0'"
                    '});'
                'marker.setIcon(icon);'
                "var popup = L.popup({maxWidth: '300'});"
                "const display_number = {text: row[2]};"
                "const display_contract = {text: row[3]};"
                "const display_bike = {text: row[4]};"
                "const display_elec = {text: row[5]};"
                "const display_meca = {text: row[6]};"
                "var mytext = $(`<div id='mytext' class='display_text' style='width: 100.0%; height: 100.0%;'> Ville : ${display_contract.text} <br> Arrêt : ${display_number.text} <br> Vélo(s) disponible(s) : ${display_bike.text} <br> Mecanique : ${display_meca.text} <br> Electrique : ${display_elec.text}</div>`)[0];"
                "popup.setContent(mytext);"
                "marker.bindPopup(popup);"
                'return marker};')

    m = folium.Map(
        location=[48.29649, 4.07360],
        zoom_start=5,
        prefer_canvas=True,
    ) 

    for info in response:
        locations.append([info['position']['latitude'], info["position"]["longitude"], info['number'], info['contractName'], info["totalStands"]["availabilities"]["bikes"], info["totalStands"]["availabilities"]["electricalBikes"], info["totalStands"]["availabilities"]["mechanicalBikes"]])
    
    plugins.FastMarkerCluster(locations, callback=callback).add_to(m)

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
def station(number, contract):
    urlStation = "https://api.jcdecaux.com/vls/v3/stations/{station_number}?contract={contract_name}&apiKey={key}".format(station_number = number, contract_name = contract, key = app.config['SECRET_KEY'])

    response = requests.get(urlStation, headers=app.config['HEADERS']).json()

    m = folium.Map(
        location=[response["position"]["latitude"], response["position"]["longitude"]],
        zoom_start=20,
        prefer_canvas=True,
    )

    folium.Marker(
            [response["position"]["latitude"], response["position"]["longitude"]],
            tooltip=response["name"]
        ).add_to(m)

    m.get_root().width = "100%"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    try:
        pourcentDispo = str((response["totalStands"]["availabilities"]["bikes"] / response["totalStands"]["capacity"]) * 100) + " %"
    except ZeroDivisionError:
        pourcentDispo = 0
    
    try:
        pourcentElec = str((response["totalStands"]["availabilities"]["electricalBikes"] / response["totalStands"]["availabilities"]["bikes"]) * 100) + " %"
    except ZeroDivisionError:
        pourcentElec = 0

    return render_template("station.html", iframe=iframe, info=response, pourcentDispo=pourcentDispo, pourcentElec=pourcentElec)

@app.route("/classement")
def classement():
    urlGlobal = "https://api.jcdecaux.com/vls/v1/stations?apiKey={key}".format(key = app.config['SECRET_KEY'])

    response = requests.get(urlGlobal, headers=app.config['HEADERS'])

    infos = response.json()

    stations = []

    for info in infos:
        isPresent = info["name"] in stations
        if not isPresent:
            stations.append(info)

    def myFunc(e):
        return e['bike_stands']
    
    stations.sort(reverse=True, key=myFunc)

    return render_template("classement.html", infos=stations)