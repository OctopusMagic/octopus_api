# OCTOPUS API
---
API for interacting with the [Sistema de Facturación DTES](https://factura.gob.sv/) of the [Ministerio de Hacienda](https://www.mh.gob.sv/).

## Installation
1. Create an account in the [Sistema de Facturación DTES](https://admin.factura.gob.sv/) and enable the test environment.
2. Generate a certificate and a API key.
3. Clone the repository.
4. Create a folder called "firmador" and inside create another folder called "temp". 
5. Copy the certificate in the "temp" folder, and rename it to "{your_nit}.crt" where {your_nit} is your NIT number without the dashes.
6. Copy the .env.example file and rename it to .env. Fill the variables with the corresponding values.
7. Run the docker compose file with the following command:
```bash
docker-compose up -d
```