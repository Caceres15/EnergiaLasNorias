from flask import Flask, request, render_template, send_file
import pdfplumber
import mysql.connector
from fpdf import FPDF
import io
import os
from flask import Flask, request, render_template, send_file
import pdfplumber
import mysql.connector
from fpdf import FPDF
import io
import tempfile

app = Flask(__name__)

# Configuración de la base de datos
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'recibo_db'
}

def guardar_pdf_en_bd(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            contenido = page.extract_text()
            if contenido:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO recibos (nombre, contenido) VALUES (%s, %s)", (f'recibo_{i+1}.pdf', contenido))
                conn.commit()
                cursor.close()
                conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pdf_file = request.files['pdf_file']
        guardar_pdf_en_bd(pdf_file)
        return "PDF subido y procesado."
    return render_template('index.html')

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    resultados = []
    if request.method == 'POST':
        texto_buscar = request.form['texto_buscar']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, contenido FROM recibos WHERE contenido LIKE %s", ('%' + texto_buscar + '%',))
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('buscar.html', resultados=resultados)



@app.route('/descargar/<int:recibo_id>')
def descargar(recibo_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, contenido FROM recibos WHERE id = %s", (recibo_id,))
    recibo = cursor.fetchone()
    cursor.close()
    conn.close()

    if recibo:
        nombre, contenido = recibo
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Agrega el contenido al PDF
        for linea in contenido.splitlines():
            pdf.cell(0, 10, linea, ln=True)

        # Crea un archivo temporal para guardar el PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            pdf.output(temp_pdf.name)
            temp_pdf.seek(0)
            return send_file(temp_pdf.name, as_attachment=True, download_name=nombre, mimetype='application/pdf')
    
    return "Recibo no encontrado", 404


if __name__ == '__main__':
    app.run(debug=True)
