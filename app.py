from flask import Flask, jsonify
from flask_cors import CORS
from FlightRadar24 import FlightRadar24API

app = Flask(__name__)
# Permitimos que tu web de Google Apps Script lea los datos
CORS(app)

# Inicializamos el "hacker" de FlightRadar
fr_api = FlightRadar24API()

@app.route('/radar')
def get_radar():
    try:
        # La librería se salta el firewall y pide solo las aerolíneas que queremos
        flights = fr_api.get_flights(airline="IBB,RSC,NAY")
        
        aviones_limpios = []
        
        for f in flights:
            aviones_limpios.append({
                "lat": f.latitude,
                "lon": f.longitude,
                "track": f.heading,
                "type": f.aircraft_code or "N/A",  # Ej: "E295"
                "reg": f.registration or "N/A",    # Ej: "EC-NQA"
                "flight": f.callsign or ""         # Ej: "IBB123A"
            })
                
        return jsonify({"success": True, "data": aviones_limpios})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
