@rem python -m http.server
@rem usage: server.py [-h] [--cgi] [--bind ADDRESS] [--directory DIRECTORY] [port]

python -m http.server --bind 0.0.0.0 --directory ../.. 5000
pass