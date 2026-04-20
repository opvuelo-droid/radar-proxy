from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Permitimos la conexión desde Google Apps Script
CORS(app)

@app.route('/radar')
def get_radar():
    # Coordenadas perfectas: Norte(45), Sur(25), Este(5), Oeste(-20)
    # Pedimos la caja entera de la península y Canarias, sin filtrar aerolíneas en la URL
    url = 'https://data-live.flightradar24.com/zones/fcgi?bounds=45.0,25.0,5.0,-20.0&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1'
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.flightradar24.com/",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        aviones = []
        
        for key, val in data.items():
            if key not in ["full_count", "version", "stats"] and isinstance(val, list):
                
                # ESCUDO: Si el avión no transmite datos completos, lo ignoramos para evitar cuelgues
                if len(val) < 17:
                    continue
                    
                callsign = str(val[16]).strip().upper()
                iata = str(val[13]).strip().upper()
                tipo = str(val[8]).upper() if len(val) > 8 else ""
                
                # FILTRO EN PYTHON: Extraemos solo nuestra flota (IBB, RSC, NAY o NT)
                if callsign.startswith("IBB") or callsign.startswith("RSC") or callsign.startswith("NAY") or iata.startswith("NT"):
                    aviones.append({
                        "lat": val[1],
                        "lon": val[2],
                        "track": val[3],
                        "type": tipo,
                        "reg": val[9] if len(val) > 9 else "N/A",
                        "flight": callsign if callsign else iata
                    })
                        
        return jsonify({"success": True, "data": aviones})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
