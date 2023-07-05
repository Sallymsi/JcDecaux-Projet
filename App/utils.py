import requests

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
                "var mytext = $(`<div id='mytext' class='display_text' style='width: 100.0%; height: 100.0%;'> Ville : ${display_contract.text} <br> Arrêt : ${display_number.text} <br> Vélo(s) disponible(s) : ${display_bike.text} <br> Mecanique : ${display_meca.text} <br> Electrique : ${display_elec.text}</div>`)[0];"
                "popup.setContent(mytext);"
                "marker.bindPopup(popup);"
                'return marker};')

    return callback


def pourcentDispo(response):
    try:
        pourcentDispo = (response["totalStands"]["availabilities"]["bikes"] / response["totalStands"]["capacity"]) * 100
    except ZeroDivisionError:
        pourcentDispo = 0
    
    return str("%.2f" % pourcentDispo) + " %"


def pourcentElec(response):
    try:
        pourcentElec = (response["totalStands"]["availabilities"]["electricalBikes"] / response["totalStands"]["availabilities"]["bikes"]) * 100
    except ZeroDivisionError:
        pourcentElec = 0

    return str("%.2f" % pourcentElec) + " %"


def classementCity(response):
    stations = []
    for info in response:
        urlContract = "https://api.jcdecaux.com/vls/v3/stations?contract={contract}&apiKey={key}".format(contract = info['name'], key = 'e0a1bf2c844edb9084efc764c089dd748676cc14')
        headers = {"Accept": "application/json"}
        responseCity = requests.get(urlContract, headers=headers)
        infoCity = responseCity.json()
        standTotal = 0
        availabilitiesBike = 0
        elecBike = 0

        for stand in infoCity:
            standTotal = standTotal + stand['totalStands']['capacity']
            availabilitiesBike = availabilitiesBike + stand['totalStands']['availabilities']['bikes']
            elecBike = elecBike + stand['totalStands']['availabilities']['electricalBikes']
        
        try:
            pourcentDispo = (availabilitiesBike / standTotal) * 100
        except ZeroDivisionError:
            pourcentDispo = 0

        pourcentDispo = str("%.2f" % pourcentDispo) + " %"

        try:
            pourcentElec = (elecBike / availabilitiesBike) * 100
        except ZeroDivisionError:
            pourcentElec = 0
        
        pourcentElec = str("%.2f" % pourcentElec) + " %"

        stations.append([info['name'], standTotal, availabilitiesBike, pourcentDispo, pourcentElec])
    
    def myFunc(e):
        return e[1]
    
    stations.sort(reverse=True, key=myFunc)

    return stations

def classementStation(response):
    stations = []
    for info in response:
        isPresent = info["name"] in stations
        if not isPresent:
            stations.append(info)

    def myFunc(e):
        return e['totalStands']['availabilities']['bikes']
    
    stations.sort(reverse=True, key=myFunc)

    return stations