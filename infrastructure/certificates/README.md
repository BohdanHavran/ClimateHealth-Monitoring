# Public RDS CA bundle

Public trust anchors for **us-east-1**, downloaded26.11.2026 from [AWS RDS truststore](https://truststore.pki.rds.amazonaws.com/us-east-1/us-east-1-bundle.pem). Not a private key or credential. Included unchanged in backend image; no OS-wide trust store changes.

Use with DB_TLS_MODE=verify_identity and the RDS DNS endpoint. Review AWS CA rotation and certificate validity before each image release. A private MySQL deployment requires its own verified CA/DNS; this regional bundle does not authenticate arbitrary private servers. Do not disable hostname verification to resolve a mismatch.
