# Very simple VALUE API

In a given context `context`
- Store a value: 
    - GET `/{context}/{key}/{value}`
    - POST `/{context}/{key}` - Body: The value as string 
- Read a value: GET `/{context}/{key}`
- Delete a value: DELETE `/{context}/{key}`

Only plain text is supported, handling type casting must be done in the application.

## Run
```
uv sync
## Dev server
uv run fastapi dev src/valueapi/main.py 
# Production server
uv run fastapi run src/valueapi/main.py --port 80 --host 0.0.0.0
```

### Build and run with Docker
```
docker compose up -d
```

### Production
See [Deployment](https://github.com/ValueAPI/Deployment).

## Authorization
Enable authorization by creating a `auth_token` value for a given `context`.
Afterwards, this access token must be passed in the `Authorization`-header of the http request.

## Example
```shell
# Create the `hello_world` value in the context `my_context` with the content `test123`
curl https://values.my-domain.de/my_context/hello_world/test123 
# OR using POST:
curl -X POST -d "test123" --header Authorization:my_secret_token https://values.my-domain.de/my_context/hello_world

# Get this value -> Returns: test123
curl https://values.my-domain.de/my_context/hello_world

# Set an auth token:
curl -X POST -d "my_secret_token" https://values.my-domain.de/my_context/auth_token

# Try to get the value -> Returns 401
curl https://values.my-domain.de/my_context/hello_world

# Try to get this value with the auth token -> Returns: test123
curl --header Authorization:my_secret_token https://values.my-domain.de/my_context/hello_world

# Delete the auth token
curl -X DELETE --header Authorization:my_secret_token https://values.my-domain.de/my_context/auth_token
```

## Frontend
See [Frontend](https://github.com/ValueAPI/Frontend).

## Connectors
- [Python](https://github.com/ValueAPI/Connector-Python)

