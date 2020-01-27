from flask import Flask, render_template, request

# import the function to process input
from predict_pop import result

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    letters = []
    if request.method == "POST":
        # get url that the user has entered
        try:
            word = request.form['word']
            
            discount = request.form['discount']
            letters = result(word,discount)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again." + str(word) + str(discount) + str(letters)
            )
    return render_template('index.html', letters=letters, errors=errors)
	

if __name__ == '__main__':
    app.run(debug=True)