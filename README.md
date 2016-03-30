# basic-http
## What is it?
This repository contains the source code for a basic HTTP system, required for the ELEN4017 Networks Fundamentals course.
There are 3 parts: an HTTP server, an HTTP client and an HTTP caching proxy server.

## HTTP Server
### Features
Implemented:
* Multithreading
* Persistent and non-persistent connections
* Receive arbitrary length requests
* Serving static files from a directory
* POST, PUT, DELETE requests

Not yet implemented:
* HTTP/1.1
* HTTPS

### How to use it
1. `server = Server(IP, 80)` Replace IP with the server's desired IP address
2. `server.run()`

Alternatively, run `python3 server.py` to quickly start the server on 127.0.0.1:8000

The server has optional arguments:
* allow_persistent: if False, all connections will be non-persistent
* static_dir: a directory containing static files to serve. `./static` by default

Once the server is running, go to localhost:8000/index.html (or whatever address/port you used) to access the home page. If you request a root URL (such as /index.html or /drinking_fountains.png), the server will try to serve the matching file in static_dir/.




## HTTP Client
### Features
Implemented:

Not yet implemented:

### How to use it



## HTTP Proxy
### Features
Implemented:

Not yet implemented:

### How to use it
1. `proxyServer = proxy_server(IP, 80)` Replace IP with the server's desired IP address
2. `proxyServer.run()`

Alternatively, run `python3 proxy_server.py` to quickly start the server on 127.0.0.1:7000

The server has optional arguments:
* allow_persistent: if False, all connections will be non-persistent
* static_dir: a directory containing static files to serve. `./static` by default
