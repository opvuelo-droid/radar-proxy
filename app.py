from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Esto es vital: Permite que tu web de Google lea estos datos sin que salte el error de CORS
CORS(app)

@app.route('/radar')
def get_radar():
    # Buscamos toda la flota a nivel global para que no haya bloqueos de coordenadas
    url = 'https://data-live.flightradar24.com/zones/fcgi?faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=0&estimated=1&maxage=14400&gliders=0&stats=0&airline=ibb,nay,rsc'
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.flightradar24.com/",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        aviones = []
        
        # FR24 devuelve los aviones dentro de arrays indexados por IDs
        for key, val in data.items():
            if key not in ["full_count", "version", "stats"] and isinstance(val, list):
                # Extraemos indicativo (índice 16 o 13)
                flight_callsign = val[16] if len(val) > 16 and val[16] else (val[13] if len(val) > 13 else "")
                
                aviones.append({
                    "lat": val[1],
                    "lon": val[2],
                    "track": val[3],
                    "type": val[8] if len(val) > 8 else "N/A",
                    "reg": val[9] if len(val) > 9 else "N/A",
                    "flight": flight_callsign
                })
                
        return jsonify({"success": True, "data": aviones})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
