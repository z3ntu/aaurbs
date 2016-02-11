from flask import Flask, request, send_from_directory
import aaurbs
import sys


def main():
    app = Flask(__name__)

    @app.route('/')
    def root():
        return send_from_directory('static', 'index.html')

    @app.route('/api/')
    def api_a():
        print("hi")
        return 'OK'

    @app.route('/<path:filename>')
    def catch_all(filename):
        print(filename)
        return send_from_directory('static', filename)

    try:
        app.run(host='0.0.0.0',
                port=8080,
                debug=True)
    except OSError as err:
        print("[ERROR] " + err.strerror, file=sys.stderr)
        print("[ERROR] The program will now terminate.", file=sys.stderr)

if __name__ == '__main__':
    main()
