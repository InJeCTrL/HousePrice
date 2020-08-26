from flask import Flask, jsonify, send_file, request, render_template

app = Flask(__name__)

'''
from keras.models import load_model
# from sklearn.neighbors import KNeighborsRegressor
import pandas as pd
model = load_model("./wow.hdf5")
# 获得均值 & 标准差
df = pd.read_csv("./dataset_info.csv", encoding = "UTF-8")
x = df.iloc[:, :-1]
x.columns = range(len(x.columns))
len_x = len(x)
trainlimit = int(len_x * 0.8)
x = x[:trainlimit]
x_mean = x.mean(axis = 0)
x_std = x.std(axis = 0)
'''
''' kNN
reg = KNeighborsRegressor(5)
reg.fit(x, y)
'''

@app.route("/house", methods = ["GET"])
def getHouseList():
    return send_file('./dataset_geo.csv', mimetype='text/csv', as_attachment=True)

'''
@app.route("/pvalue", methods = ["GET"])
def getPredictValue():
    face_score = 0
    facedata = request.values.getlist("face")
    for face in facedata:
        face_score += int(face)
    test_input = pd.DataFrame([[float(request.args.get("deco")) if request.args.get("deco") else 0,
                                face_score,
                                float(request.args.get("square")) if request.args.get("square") else 0,
                                float(request.args.get("totalfloor")) if request.args.get("totalfloor") else 0, 
                                float(request.args.get("btype")) if request.args.get("btype") else 0, 
                                float(request.args.get("floor")) if request.args.get("floor") else 0,
                                float(request.args.get("lat")), float(request.args.get("lng")), 
                                float(request.args.get("nHall")) if request.args.get("nHall") else 0, 
                                float(request.args.get("nRoom")) if request.args.get("nRoom") else 0]])
    test_input -= x_mean
    test_input /= x_std
    # yp = reg.predict(test_input)
    
    return jsonify(str(model.predict(test_input)[0][0]))
    # return jsonify(str(yp[0]))
'''
@app.route("/", methods = ["GET"])
def mapindex():
    return send_file('./map.html')

app.run(host='127.0.0.1', port = 5555)