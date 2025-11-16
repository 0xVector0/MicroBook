from flask import request, jsonify, Flask

def flask_server(orderbook_instance):
    app = Flask(__name__)

    @app.route("/limit-order", methods=["POST"])
    def new_limit_order():
        data = request.get_json()
        return jsonify(orderbook_instance.new_limit_order(
            data.get('amount'),
            data.get('price'),
            data.get('type')
        ))

    @app.route("/order", methods=["POST"])
    def new_order():
        data = request.get_json()
        return jsonify(orderbook_instance.new_order(
            data.get('amount'),
            data.get('type')
        ))

    @app.route("/orderbook")
    def get_orderbook():
        with orderbook_instance.lock:
            bids = list(orderbook_instance.bids)
            asks = list(orderbook_instance.asks)
        return jsonify({"bid": bids, "ask": asks})

    @app.route("/logs")
    def get_logs():
        return jsonify({"logs": orderbook_instance.logs[-100:]})

    return app