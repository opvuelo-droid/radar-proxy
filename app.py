from flask import Flask, jsonify
from flask_cors import CORS
from FlightRadar24 import FlightRadar24API

app = Flask(__name__)
CORS(app)
fr_api = FlightRadar24API()

@app.route('/radar')
def get_radar():
    try:
        flights = fr_api.get_flights(airline="IBB,RSC,NAY")
        aviones_limpios = []
        for f in flights:
            aviones_limpios.append({
                "lat": f.latitude,
                "lon": f.longitude,
                "track": f.heading,
                "type": f.aircraft_code or "N/A",
                "reg": f.registration or "N/A",
                "flight": f.callsign or "",
                "altitud": f.altitude,
                "velocidad": f.ground_speed,
                "v_speed": f.vertical_speed,
                "on_ground": f.on_ground
            })
        return jsonify({"success": True, "data": aviones_limpios})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
