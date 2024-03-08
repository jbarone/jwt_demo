# JWT Demo Environment

This repository contains a demo environment for JWT (JSON Web Token) 
based authentication and authorization. And is used for the demonstration 
of how JWT security can go wrong. This is the demonstration environment 
that was used in my talk 
["JWTs: The Good, the Bad, and the Ugly (Security Edition)"](https://www.sans.org/webcasts/jwts-good-bad-ugly-security-edition/).

[![JWTs: The Good, the Bad, and the Ugly (Security Edition)](https://img.youtube.com/vi/Y9b-r8OnGGI/0.jpg)](https://youtu.be/Y9b-r8OnGGI?si=U2v3ZcINzQYWgCt_)

## Setup

The entire environment is built using Docker Compose. To start the systems, 
simply run:

```bash
$ docker compose up -d
```

This will start up three different environments demonstrating three different 
types of JWT security issues.

## Exploiting the Environments

### Simple

The first environment is a simple JWT implementation. The JWT is signed using
a secret key. To exploit this environment, you don't even need to know the 
secret key. You can simply change the algorithm used to none and the JWT will 
be accepted.

[http://localhost:5000/](http://localhost:5000/)

### Algorithm Juggling

This environment uses a private key to sign the JWT. The public key is always
used when verifying the JWT. However, the application will accept whatever algorithm
is specified in the header. This means you can use a symmetric algorithm to sign
the JWT using the public key.

[http://localhost:5001/](http://localhost:5001/)

**NOTE**: The public key is stored in the keys folder as
[juggle.jwk](keys/juggle.jwk)

### SQL Injection

This environmnent uses a collection of keys for signing the JWT. The keys are stored
in a SQLite database, and uses the Key ID (`kid`) to look up the key. However, the
the `kid` is not properly sanitized and is vulnerable to SQL injection.

[http://localhost:5002/](http://localhost:5002/)

**NOTE**: A key will be needed to sign the JWT. The [simple](keys/simple.jwk)
key can be used, with the value `mysecret` or you can create your own key.

## Shutting Down

To shut down the environment, run:

```bash
$ docker compose down -v
```
