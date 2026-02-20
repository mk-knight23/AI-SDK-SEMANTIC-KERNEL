from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return jsonify({
        "status": "healthy",
        "service": "patentiq-backend",
        "version": "0.1.0"
    }), 200


@app.route("/", methods=["GET"])
def root():
    """Root endpoint."""
    return jsonify({
        "message": "Hello World from PatentIQ Backend",
        "service": "patentiq-backend",
        "version": "0.1.0"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)