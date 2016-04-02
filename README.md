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
1. `proxyServer = proxy_server(IP, Port)` Replace IP with the server's desired IP address and corresponding port number
2. `proxyServer.run()`
3. Alternatively, run `python3 proxy_server.py` to quickly start the server on 127.0.0.1:7000

The server has optional arguments:
* allow_persistent: if False, all connections will be non-persistent
* static_dir: a directory containing static files to serve. `./static` by default

## Main
We have created a demo program `main.py` in order to test the web browsing application
### How to use it 
1. Run `python3 main.py`
2. Input your desired proxy IP address
3. Input the corresponding proxy port number
4. If you would not like to connect to a proxy server, simply press enter (leaving it blank) when prompted for the proxy IP      address
5. Making a request:
  * Get request:
    - Use this request when you simply want to retrieve a webpage
    - Enter 'get' as your desired HTTP method (without the quotation marks)
    - Enter the address you would like to make the request to
    - The server's response will now be displayed 
  * Condtional Get request: 
    - The get request above by default implements caching, however if you would like to specify a date for when you want to         check the modification against, use this request
    - Enter 'cond get' as your desired HTTP method (without the quotation marks)
    - Enter the address you would like to make the request to
    - Enter the date against which you would like to check if the page has been modified since
    - The server's response will now be displayed
  * Post and put request:
    - Use these requests when you want to send information along with your request
    - Enter 'post' or 'put' as your desired HTTP method (without the quotation marks) 
    - Enter the address you would like to post information to
    - Enter the information you would like to post/put
    - The server's response will now be displayed
  * Delete request: 
    - This request allows you to delete information in your desired web address
    - Enter 'delete' as your desired HTTP method (without the quotation marks)
    - Enter the address you would like to delete information from
    - The server's response to your delete request will not be displayed
