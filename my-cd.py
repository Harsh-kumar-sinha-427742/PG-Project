from flask import Flask, render_template_string

app = Flask(__name__)

html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Welcome to Python Webpage</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            text-align: center;
            padding: 5rem 1rem;
            margin: 0;
        }
        h1 {
            font-size: 4rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        }
        p {
            font-size: 1.5rem;
            margin-top: 0;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
        }
        .btn {
            margin-top: 2rem;
            background: white;
            color: #2575fc;
            font-weight: bold;
            padding: 1rem 2rem;
            border-radius: 30px;
            border: none;
            cursor: pointer;
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            font-size: 1.25rem;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            background: #1d5ece;
            color: white;
            box-shadow: 0 12px 20px rgba(29, 94, 206, 0.5);
        }
    </style>
</head>
<body>
    <h1>Welcome to a Python Webpage!</h1>
    <p>This webpage is served using a simple Flask application.</p>
    <a href="https://flask.palletsprojects.com/" class="btn" target="_blank">Learn Flask</a>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)

