# Services
A service is an app that is hosted. Services are defined in `services/<service-name>`.
Each service runs on a different TCP port and is capable of running entirely under
a subpath of the root server (see "The Reverse HTTP Proxy" below).

The [home page](/pages/home.html) has a list of all currently running services.

## Service Definitions
Each service must have a `<service-name>/functions.sh` file that defines instructions
to install and start a service. `functions.sh` is executed with either `bringup`
or `start` as an argument, to install or start the service respectively. Stopping a
service is handled by `jam-sandwich-hosting.sh` independent of `functions.sh`.

## Persistent Store
Each service gets an area on the filesystem to store any kind of persistent data -- this
includes the installation files themselves. This persistent store is at
`persist/<service-name>`.

## Process Control
Starting a process is accomplished by running `functions.sh start`. This command is
expected to block as long as the service is active. The PID of this blocking process
is written to a file, and is later used to stop the process.

This approach to process control is rather simple. The only complexity, the only
thing that can vary per service, is the actual startup procedure. Most well-behaved
apps should be simple to work with; as long as `functions.sh` can be written
to wrap the app in such a way that killing the `functions.sh` instance kills the app,
the job is done.

# The Reverse HTTP Proxy
Reverse proxying is accomplished with Caddy. The idea is that while each service
spins up its own HTTP server, they all appear on different subpaths of a single
HTTP server.

Caddy listens for traffic from the Ngrok agent (the downstream) on port **8001**
and forwards a service (the upstreams) on the basis of the leading component of
the request path.

# The Tunnel
Ngrok provides the tunnel that is used to connect to the WWW despite NAT. 
Installation is via Ngrok's DEB package, nothing out of the ordinary. Along
with serving as a tunnel, Ngrok also encrypts the traffic with TLS so we have
(foolproof) HTTPS at no extra effort.

The Ngrok agent establishes a connection with the Ngrok server (the downstream)
on an arbitrary port, and traffic is forwarded to and from Caddy (the upstream) through
port **8001**.
