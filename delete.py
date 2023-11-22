from flask import Flask, jsonify
import pyodbc
from datetime import datetime
import requests


app = Flask(__name__)

# Configuración de conexión a la base de datos
conn_str = 'DRIVER={SQL Server};SERVER=diseno2.database.windows.net;DATABASE=Diseño;UID=ehiderg;PWD=Diseño2023'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

def agregar_log(cedula, tipo_documento,operacion, detalles):
    # Agregar registro al log
    cursor.execute("INSERT INTO Log (CedulaPersona, TipoDocumento,Operacion, FechaOperacion, Detalles) VALUES (?, ?, ?, ?, ?)",
                   cedula, tipo_documento, operacion, datetime.now(), detalles)
    conn.commit()



@app.route('/borrar/<numero_documento>', methods=['DELETE'])
def borrar(numero_documento):
    # Consultar en el microservicio de consulta para verificar la existencia
    consulta_response = requests.get(f'http://localhost:5000/consultar/{numero_documento}')
    
    if consulta_response.status_code == 200:
        row = consulta_response.json()
        # Persona encontrada, proceder con el borrado
        cursor.execute("DELETE FROM Registro WHERE NumeroDocumento=?", numero_documento)
        conn.commit()

        # Agregar operación al log
        agregar_log(numero_documento, row['TipoDocumento'], 'Borrado', f"Se eliminó la información de {row['PrimerNombre']} {row['Apellidos']} con número de documento {numero_documento}")

        return jsonify({"mensaje": "Borrado exitoso"}), 200
    else:
        # Persona no encontrada, devolver un mensaje de error
        return jsonify({"error": "Persona no encontrada"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=3000)
