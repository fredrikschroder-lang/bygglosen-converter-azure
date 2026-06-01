from flask import Flask, render_template, request, send_file, flash, redirect
from converter import convert_bygglosen_data
from datetime import datetime
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'bygglosen-secret-key')
app.config['SESSION_COOKIE_NAME'] = 'bygglosen-session'
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    from flask import jsonify
    xml_files = request.files.getlist('xml_files')
    csv_file = request.files.get('csv_file')
    mode = request.form.get('mode', 'anstalld')

    if not xml_files or all(f.filename == '' for f in xml_files):
        return jsonify({'error': 'Inga XML-filer uppladdade.'}), 400

    xml_files = [f for f in xml_files if f.filename != '']
    csv_stream = None
    if csv_file and csv_file.filename != '':
        csv_stream = csv_file.stream

    try:
        from converter import analyze_bygglosen_data
        xml_streams = [f.stream for f in xml_files]
        warnings = analyze_bygglosen_data(xml_streams, csv_stream, mode=mode)
        return jsonify({'warnings': warnings})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/convert', methods=['POST'])
def convert():
    xml_files = request.files.getlist('xml_files')
    csv_file = request.files.get('csv_file')
    mode = request.form.get('mode', 'anstalld')
    download_format = request.form.get('format', 'xml')
    override_start = request.form.get('override_start')
    override_end = request.form.get('override_end')

    if not xml_files or all(f.filename == '' for f in xml_files):
        flash('Du måste ladda upp minst en XML-fil.')
        return redirect('/')

    xml_files = [f for f in xml_files if f.filename != '']

    csv_stream = None
    if csv_file and csv_file.filename != '':
        csv_stream = csv_file.stream

    try:
        xml_streams = [f.stream for f in xml_files]

        if download_format == 'csv':
            _, csv_result, header_data = convert_bygglosen_data(
                xml_streams, csv_stream, include_csv=True,
                override_start=override_start, override_end=override_end, mode=mode
            )
            start_date = header_data.get('LoneperiodStartdatum', '')
            period_str = start_date[:6] if len(start_date) >= 6 else datetime.now().strftime('%Y%m')

            return send_file(
                csv_result,
                as_attachment=True,
                download_name=f'LOSEN_konverterad_{period_str}.csv',
                mimetype='text/csv'
            )
        else:
            xml_result, header_data = convert_bygglosen_data(
                xml_streams, csv_stream, include_csv=False,
                override_start=override_start, override_end=override_end, mode=mode
            )
            start_date = header_data.get('LoneperiodStartdatum', '')
            period_str = start_date[:6] if len(start_date) >= 6 else datetime.now().strftime('%Y%m')

            return send_file(
                xml_result,
                as_attachment=True,
                download_name=f'LOSEN_konverterad_{period_str}.xml',
                mimetype='application/xml'
            )
    except Exception as e:
        flash(f'Ett fel uppstod vid konvertering: {str(e)}')
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
