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
* GET, HEAD, POST, PUT, DELETE responses
* Demo web pages (/index.html and /content.html)
* Accessible by other hosts on the network

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
* Persistent and non-persistent connections
* Receive arbitrary length requests
* Perform requests through proxy server (no authentication)
* GET, HEAD, POST, PUT, DELETE requests
* Conditional GET
* Download all images on page (by parsing HTML)
* Redirection

Not yet implemented:
* HTTP/1.1
* HTTPS
* GUI front-end

### How to use it


The client has been tested with the following websites:
* [Loot](http://www.loot.co.za)
* [Amazon](http://www.amazon.com)
* [Takealot](http://www.takealot.com)
* [Wits](http://www.wits.ac.za)
* [Stackoverflow](http://stackoverflow.com)
* [Copernica](http://www.copernica.com)
* [Post Test Server](http://www.posttestserver.com/post.php)
* Our custom HTTP server



## HTTP Proxy
### Features
Implemented:
* Caching
* Conditional GET
* Persistent and non-persistent connections
* Multithreading
* Accessible by other hosts on the network

Not yet implemented:
* HTTP/1.1
* HTTPS

### How to use it
1. `proxyServer = proxy_server(IP, 80)` Replace IP with the server's desired IP address
2. `proxyServer.run()`

Alternatively, run `python3 proxy_server.py` to quickly start the server on 127.0.0.1:7000

The server has optional arguments:
* allow_persistent: if False, all connections will be non-persistent
* static_dir: a directory containing static files to serve. `./static` by default
