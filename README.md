# IoT RFID Security System
A general purpose rfid based authentication system for protecting anything with
a plastic card :rofl:

# Getting Started
## Setting up the auth service
The core of the authentication service is provided by [heatshield][1].

The following tasks need to be achieved before the auth service can be used:

### Set the database urls

```
$ cd rfid_auth_server
$ source setup.sh
```
### Add a client and user to the database
This can be done with [heatshield-cli][2].

# Infrastructure

## Backend
The backend server is implemented in the Rust Programming Language and provides
access to a number of different functions the client can request.  

## Frontend
The frontend is a command line client implemented in Python that talks to the
backend to perform operations.  Actions performed using the client require key card access.  

### Actions
The table below describes the actions available in this PoC.

Action | Description | Requires Key Card
--- | --- | ---
`file` | Request a file given an id card and filename.  Acts like a single flat directory for a users files, text only | yes
`door` | Request that a door be opened.  Actual implementation only prints `Opening Door` on the server and serves as an example that anything can be put behind a protected route.  | yes

# Authentication & Authorization
When an rfid card/token is scanned the data stored on a section of the storage
is read, parsed, and sent to the backend as a set of credentials.  Assuming that
the username and password supplied on the rfid card/token are valid, an access
token is generated and stored in the backend database and then sent to the
client.  The client is then able to make requests to a protected route with the
access token in the header of the request like this:

```
Authorization: Bearer ey.........................
```

An authorized user will have a valid access token that matches the access token
in the backend database and will not be rejected.  

A user with username and password that are not in the database, that is they do
not have an account, will not be granted an access token.  

# Protected Routes
Any route can be a protected route by adding `policy: Bearer` as an argument to
the function.  The Bearer policy is what is known as a RequestGuard in the
Rocket HTTP framework.  When a RequestGuard fails, the route that its used on is
never evaluated, this allows us to use our Bearer policy to protect routes.

As in the aforementioned `door` example, if the user does not have an access
token, the door route is never evaluated and thus never unlocked.  

[1]: https://github.com/technetos/heatshield
[2]: https://github.com/technetos/heatshield-cli
