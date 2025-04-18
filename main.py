from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def hello_world():
  """Example Hello World route."""
  name = request.args.get("name", "World")  # Get 'name' from request arguments
  return f"Hello {name}!"

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=3001)  # Use a fixed port for local testing
