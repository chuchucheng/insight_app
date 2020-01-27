import pickle
#prediction function
def ValuePredictor(to_predict_list):
	#to_predict = np.array(to_predict_list).reshape(1,12)
	to_predict = to_predict_list
	loaded_model = pickle.load(open("model.pkl","rb"))
	result = loaded_model.predict(to_predict)
	return result[0]


#@app.route('/',methods = ['POST'])
def result(word,discount):
	#feats = word.split(',')
	#to_predict_list = [[float(feats[0]),bool(feats[1]), int(feats[2]),int(feats[3]),int(feats[4])]]
    discount = int(discount)
    to_pred = [[len(word)/3000 + discount/100]]
    result = ValuePredictor(to_pred)
    return int(result)