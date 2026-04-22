from flask import Flask, jsonify
from flask_cors import CORS
from FlightRadar24 import FlightRadar24API

app = Flask(__name__)
CORS(app)
fr_api = FlightRadar24API()

@app.route('/radar')
def get_radar():
    try:
        # 1. Obtenemos la lista básica de aviones de la aerolínea
        flights = fr_api.get_flights(airline="IBB,RSC,NAY")
        aviones_limpios = []
        
        for f in flights:
            # Variables por defecto
            origen = ""
            destino = ""
            std = None
            sta = None
            atd = None
            eta = None
            estado_texto = ""
            
            # 2. Extracción profunda de detalles
            try:
                details = fr_api.get_flight_details(f)
                
                if details:
                    # -- Extracción de Ruta --
                    airport_info = details.get("airport", {})
                    if airport_info:
                        if airport_info.get("origin") and airport_info["origin"].get("code"):
                            origen = airport_info["origin"]["code"]["iata"]
                        if airport_info.get("destination") and airport_info["destination"].get("code"):
                            destino = airport_info["destination"]["code"]["iata"]
                    
                    # -- Extracción de Tiempos (UNIX timestamps) --
                    time_info = details.get("time", {})
                    if time_info:
                        sched = time_info.get("scheduled", {})
                        real = time_info.get("real", {})
                        est = time_info.get("estimated", {})
                        
                        std = sched.get("departure")
                        sta = sched.get("arrival")
                        atd = real.get("departure")
                        eta = est.get("arrival")
                    
                    # -- Extracción de Estado (Ej: "Delayed", "Estimated 15:30") --
                    status_info = details.get("status", {})
                    if status_info:
                        estado_texto = status_info.get("text", "")
                        
            except Exception as ex:
                print(f"Aviso: No se pudieron obtener detalles extra para {f.callsign}. Razón: {ex}")

            # 3. Empaquetar todo el arsenal de datos
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
                "squawk": f.squawk or "",
                "on_ground": f.on_ground,
                "origen": origen,
                "destino": destino,
                "std_radar": std,
                "sta_radar": sta,
                "atd_radar": atd,
                "eta_radar": eta,
                "estado_radar": estado_texto
            })
            
        return jsonify({"success": True, "data": aviones_limpios})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
