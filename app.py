from flask import Flask, request, jsonify, render_template
import math
from operator import itemgetter
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def distancia(coord1, coord2):
    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]

    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

def en_ruta(rutas, c):
    ruta = None
    for r in rutas:
        if c in r:
            ruta = r
    return ruta

def peso_ruta(ruta, pedidos):
    total = 0
    for c in ruta:
        total = total + pedidos[c]
    return total

def vrp_voraz(coord, pedidos, almacen, max_carga):
    # Calcular ahorros
    s = {}
    for c1 in coord:
        if c1 != almacen:
            for c2 in coord:
                if c2 != c1 and c2 != almacen:
                    if not (c2, c1) in s:
                        d_c1_c2 = distancia(coord[c1], coord[c2])
                        d_c1_almacen = distancia(coord[c1], coord[almacen])
                        d_c2_almacen = distancia(coord[c2], coord[almacen])
                        s[c1, c2] = d_c1_almacen + d_c2_almacen - d_c1_c2

    # Ordenar ahorros
    s = sorted(s.items(), key=itemgetter(1), reverse=True)

    # Construir las rutas
    rutas = []
    for k, v in s:
        rc1 = en_ruta(rutas, k[0])
        rc2 = en_ruta(rutas, k[1])

        if rc1 is not None and rc2 is None:
            # Ciudad 1 ya está en ruta, agregar la ciudad 2
            if rc1[0] == k[0]:
                if peso_ruta(rc1, pedidos) + pedidos[k[1]] <= max_carga:
                    rutas[rutas.index(rc1)].insert(0, k[1])
            elif rc1[-1] == k[0]:
                if peso_ruta(rc1, pedidos) + pedidos[k[1]] <= max_carga:
                    rutas[rutas.index(rc1)].append(k[1])
        elif rc1 is None and rc2 is not None:
            # Ciudad 2 ya está en ruta, agregar la ciudad 1
            if rc2[0] == k[1]:
                if peso_ruta(rc2, pedidos) + pedidos[k[0]] <= max_carga:
                    rutas[rutas.index(rc2)].insert(0, k[0])
            elif rc2[-1] == k[1]:
                if peso_ruta(rc2, pedidos) + pedidos[k[0]] <= max_carga:
                    rutas[rutas.index(rc2)].append(k[0])
        elif rc1 is not None and rc2 is not None and rc1 != rc2:
            # La ciudad 1 y 2 ya están en diferentes rutas, tratar de unirlas
            if rc1[0] == k[0] and rc2[-1] == k[1]:
                if peso_ruta(rc1, pedidos) + peso_ruta(rc2, pedidos) <= max_carga:
                    rutas[rutas.index(rc1)] = rc2[::-1] + rc1
            elif rc1[-1] == k[0] and rc2[0] == k[1]:
                if peso_ruta(rc1, pedidos) + peso_ruta(rc2, pedidos) <= max_carga:
                    rutas[rutas.index(rc1)] = rc1 + rc2
            elif rc1[0] == k[0] and rc2[0] == k[1]:
                if peso_ruta(rc1, pedidos) + peso_ruta(rc2, pedidos) <= max_carga:
                    rutas[rutas.index(rc1)] = rc2[::-1] + rc1
            elif rc1[-1] == k[0] and rc2[-1] == k[1]:
                if peso_ruta(rc1, pedidos) + peso_ruta(rc2, pedidos) <= max_carga:
                    rutas[rutas.index(rc1)] = rc1 + rc2[::-1]
        elif rc1 is None and rc2 is None:
            # No están en ninguna ruta, crear una nueva ruta
            if peso_ruta([k[0], k[1]], pedidos) <= max_carga:
                rutas.append([k[0], k[1]])

    return rutas

@app.route("/")
def home():
    return render_template('index.html')


@app.route("/rutas_optimas", methods=['POST'])
def calcular_ruta_optima():
    data = request.get_json()
    coord = data["coord"]
    pedidos = data["pedidos"]
    max_carga = data["max_carga"]
    almacen = 'almacen'

    rutas_optimas = vrp_voraz(coord, pedidos, almacen, max_carga)

    return jsonify(rutas_optimas)

if __name__ == "__main__":
    app.run(debug = False, host = '0.0.0.0')
