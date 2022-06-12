"""
Main Flask Server.
"""

import cv2
import pandas as pd
import numpy as np

from flask import Flask, render_template, Response, request, jsonify

from datetime import datetime

from main import database

import efficientdet as efficientdet

app = Flask(__name__)

camera = cv2.VideoCapture(1)

def run_inference(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame, prediction = efficientdet.test(frame)
    output_frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
    return output_frame

def gen_frames():  
    while True:
        # print("Reading from camera")
        success, frame = camera.read()
        if not success:
            print("Not streaming")
        else:
            # print("True")
            frame = run_inference(np.array(frame))
            # print("Running inference")
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('React_App.html')

@app.route('/database', methods=["GET"])
def db():
    if request.method == "GET":
        print("here")
        connection = database(label = 'pistol')
        timestamps = pd.read_sql_query("SELECT b FROM timestamps", connection)
        print(timestamps)
        print("here 2")
        data_pd = {}
        for index, col in timestamps.iterrows():
            data_pd[index] = str(dict(timestamps.loc[index])["b"].to_pydatetime())[0:-6]
        return jsonify(data_pd)

if __name__ == "__main__":
    print("Finished loading models.")
    print("Launching the app.")
    app.run(debug=True, port=5000)
    """
    from gevent.pywsgi import WSGIServer

    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
    """