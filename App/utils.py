import requests

# Callback de mise en forme des popup des points sur la maps de la page principale (index)
def callbackIndex():
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
    return callback
# Callback mise en forme des popup des points sur la maps de la page secondaire (city)
def callbackCity():
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
                "var mytext = $(`<div id='mytext' class='display_text' style='width: 100.0%; height: 100.0%;'> Ville : ${display_contract.text} <br> Arrêt : ${display_number.text} <br> Vélo(s) disponible(s) : ${display_bike.text} <br> Mécanique : ${display_meca.text} <br> Éléctrique : ${display_elec.text}</div>`)[0];"
                "popup.setContent(mytext);"
                "marker.bindPopup(popup);"
                'return marker};')

    return callback
# Renvoie une liste des villes sans doublon
def listCity(response):
    city = []
    for info in response:
        isPresent = info["name"] in city
        if not isPresent:
            city.append(info["name"])

    city.sort()

    return city
# Renvoie une liste des stations d'une ville dans l'ordre en fonctions de son numéro
def listStation(response):
    stations = []
    for info in response:
        isPresent = info['name'] in stations
        if not isPresent:
            stations.append(info)

    def myFunc(e):
        return e['number']
    
    stations.sort(key=myFunc)

    return stations
# Renvoie la disponibilité de vélo en pourcentage
def pourcentDispo(available, capacity):
    try:
        pourcentDispo = (available / capacity) * 100
    except ZeroDivisionError:
        pourcentDispo = 0
    
    return str("%.1f" % pourcentDispo) + " %"
# Renvoie le pourcentage de velo disponible en fonction du type (éléctrique ou mécanique)
def pourcentType(type, available):
    try:
        pourcentType = (type / available) * 100
    except ZeroDivisionError:
        pourcentType = 0

    return str("%.1f" % pourcentType) + " %"
# Renvoie le classement des villes en fonction de la capacité totale de vélo sous forme de liste
def classementCity(response):
    stations = []
    for info in response:
        urlContract = "https://api.jcdecaux.com/vls/v3/stations?contract={contract}&apiKey={key}".format(contract = info['name'], key = 'e0a1bf2c844edb9084efc764c089dd748676cc14')
        headers = {"Accept": "application/json"}
        responseCity = requests.get(urlContract, headers=headers)
        infoCity = responseCity.json()
        standTotal = 0
        availableBike = 0
        elecBike = 0

        for stand in infoCity:
            standTotal = standTotal + stand['totalStands']['capacity']
            availableBike = availableBike + stand['totalStands']['availabilities']['bikes']
            elecBike = elecBike + stand['totalStands']['availabilities']['electricalBikes']

        stations.append([info['name'], standTotal, availableBike, pourcentDispo(availableBike, standTotal),elecBike, pourcentType(elecBike, availableBike)])
    
    def myFunc(e):
        return e[1]
    
    stations.sort(reverse=True, key=myFunc)

    return stations
# Renvoie le classement des stations d'une ville en fonction de la capacité totale de vélo sous forme de liste
def classementStation(response):
    stations = []
    for info in response:
        isPresent = info["name"] in stations
        if not isPresent:
            stations.append(info)

    def myFunc(e):
        return e['totalStands']['capacity']
    
    stations.sort(reverse=True, key=myFunc)

    return stations