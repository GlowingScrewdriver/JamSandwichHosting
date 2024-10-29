# Services
Each service is an app that is hosted. Services are defined in `services/<service-name>`

# The Reverse HTTP Proxy
Reverse proxying is accomplished with Caddy, and the corresponding Caddyfile can be found
at [`Caddyfile`](./Caddyfile).

Caddy listens on port **8001** and forwards to each service individually.

# Port multiplexing for SSH
SSLH is used to multiplex a single port between SSH and HTTP. This is needed
since only a single machine port can be exposed through a tunnel.

SSLH multiplexes port **8000**; the HTTP upstream listens on port **8001** (Caddy), while the
SSH upstream listens on port **22**.

# The Tunnel
Ngrok provides the tunnel that is used to connect to the WWW. Installation is
via Ngrok's DEB package, nothing out of the ordinary.

Port **80** faces Ngrok's server (the downstream), and **8000** faces SSLH (the upstream).
