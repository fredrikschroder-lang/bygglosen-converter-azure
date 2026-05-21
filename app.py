from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from converter import convert_bygglosen_data
import io
import zipfile
from datetime import datetime
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
from functools import wraps
from clerk_backend_api import Clerk
from clerk_backend_api.security import authenticate_request as clerk_authenticate_request
from clerk_backend_api.security.types import AuthenticateRequestOptions

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'bygglosen-secret-key')
app.config['SESSION_COOKIE_NAME'] = 'bygglosen-session'
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

CLERK_SECRET_KEY = os.getenv('CLERK_SECRET_KEY')
CLERK_PUBLISHABLE_KEY = os.getenv('CLERK_PUBLISHABLE_KEY')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '')

sdk = Clerk(bearer_auth=CLERK_SECRET_KEY)


def get_user_from_request():
    """Verify Clerk session token from request and return user info, or None."""
    try:
        # Check if we have a token passed in the form data (fallback for short-lived cookies)
        token = request.form.get('clerk_token')
        
        if token:
            request.headers = dict(request.headers)
            request.headers['Authorization'] = f"Bearer {token}"

        # Reconstruct the authorized party from env if provided
        authorized_party = os.getenv('CLERK_AUTHORIZED_PARTY', '')
        origin = request.headers.get('Origin', '')
        
        # We prefer the explicitly configured party, but fall back to the origin
        authorized_parties = []
        if authorized_party:
            authorized_parties.append(authorized_party)
        if origin:
            authorized_parties.append(origin)
            
        opts = AuthenticateRequestOptions(authorized_parties=authorized_parties)
        
        # Verify the session token from the request
        request_state = sdk.authenticate_request(request, opts)
        
        if request_state.is_signed_in and request_state.payload:
            user_id = request_state.payload.get('sub')
            if user_id:
                user_response = sdk.users.get(user_id=user_id)
                if user_response:
                    email = user_response.email_addresses[0].email_address if user_response.email_addresses else None
                    first = user_response.first_name or ""
                    last = user_response.last_name or ""
                    name = f"{first} {last}".strip()
                    
                    return {
                        'id': user_id,
                        'email': email,
                        'name': name or email or "Användare",
                        'image_url': user_response.image_url,
                    }
    except Exception:
        pass
        
    return None


def require_auth(f):
    """Decorator: redirects to index if not authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_request()
        if not user:
            flash('Din session har gått ut. Vänligen logga in igen.')
            return redirect(url_for('index'))
        return f(*args, user=user, **kwargs)
    return decorated_function


def require_admin(f):
    """Decorator: requires admin email."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_request()
        if not user or user.get('email') != ADMIN_EMAIL:
            flash('Du har inte behörighet till adminsidan.')
            return redirect(url_for('index'))
        return f(*args, user=user, **kwargs)
    return decorated_function


@app.route('/')
def index():
    user = get_user_from_request()
    return render_template(
        'index.html',
        user=user,
        publishable_key=CLERK_PUBLISHABLE_KEY,
        admin_email=ADMIN_EMAIL,
    )


@app.route('/admin')
@require_admin
def admin(user):
    """Admin page: lists all users via Clerk API."""
    try:
        users_response = sdk.users.list()
        all_users = list(users_response) if users_response else []
        users_data = []
        for u in all_users:
            email = u.email_addresses[0].email_address if u.email_addresses else '–'
            name = f"{u.first_name or ''} {u.last_name or ''}".strip() or email
            last_login = '–'
            if u.last_sign_in_at:
                ts = u.last_sign_in_at
                if isinstance(ts, (int, float)):
                    from datetime import timezone
                    last_login = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M')
                else:
                    last_login = str(ts)

            users_data.append({
                'name': name,
                'email': email,
                'image_url': u.image_url,
                'last_login': last_login,
                'created_at': datetime.fromtimestamp(
                    u.created_at / 1000
                ).strftime('%Y-%m-%d') if u.created_at else '–',
            })
        users_data.sort(key=lambda x: x['last_login'], reverse=True)
    except Exception as e:
        flash(f'Kunde inte hämta användare: {str(e)}')
        users_data = []

    return render_template('admin.html', users=users_data, user=user)


@app.route('/analyze', methods=['POST'])
@require_auth
def analyze(user):
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
@require_auth
def convert(user):
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
