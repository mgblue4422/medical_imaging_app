from flask import Flask, request, render_template, redirect, url_for, send_file, abort
import paramiko
from io import BytesIO

app = Flask(__name__)

# SFTP server details
SFTP_HOST = 'ssh2.ux.uis.no'
SFTP_PORT = 22
SFTP_USERNAME = 'u250639'
SFTP_PASSWORD = 'x'  # Replace with your actual password
REMOTE_FILE_PATH = '/nfs/prosjekt/IschemicStroke/Data/Region_Analysis/Plots/NO_holes/Core_CTP_and_NOTCore_DWI/histogram3D/100/CBF_COV/2D/Clear/CBF_COV_LVO.png'

@app.route('/image', methods=['GET'])
def get_image():
    try:
        # Create an SFTP client
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)

        # Check if the server requires OTP
        if transport.is_authenticated():
            sftp = paramiko.SFTPClient.from_transport(transport)

            # Open the remote file
            with sftp.file(REMOTE_FILE_PATH, 'rb') as remote_file:
                image_data = remote_file.read()

            # Close the SFTP connection
            sftp.close()
            transport.close()

            # Serve the image
            return send_file(BytesIO(image_data), mimetype='image/png')
        else:
            # If authentication fails, check if it requires OTP
            # This is a placeholder; you may need to implement a specific check based on your server's response
            if 'OTP' in transport.get_security_options().supported_auths:
                return redirect(url_for('otp_form'))
            else:
                abort(403)  # Forbidden if no valid authentication method is available

    except Exception as e:
        print(f"Error: {e}")
        abort(404)  # Return a 404 error if something goes wrong

@app.route('/otp', methods=['GET', 'POST'])
def otp_form():
    if request.method == 'POST':
        otp = request.form.get('otp')  # Get OTP from form submission
        return redirect(url_for('get_image', otp=otp))  # Redirect to image route with OTP

    # Render the OTP input form
    return '''
        <form method="post">
            <label for="otp">Enter OTP:</label>
            <input type="text" id="otp" name="otp" required>
            <input type="submit" value="Submit">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
