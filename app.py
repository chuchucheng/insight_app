from flask import Flask, render_template, request

# import the function to process input
from scrape import predpct

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    result = [0,0]
    if request.method == "POST":
        # get url that the user has entered
        try:
            url = request.form['url']

            result = predpct(str(url))
        except Exception as e:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."  + str(url) + "; error is " + str(e) 
            )
    return render_template('index.html', result1 = result[0], result2 = result[1], errors=errors)
	

if __name__ == '__main__':
    app.run(debug=True)