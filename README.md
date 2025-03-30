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
uv run fastapi run src/valueapi/main.py   
```

## Docker
```
docker compose up -d
```

## Authorization
Enable authorization by creating a `auth_token` value for a given `context`.
Afterwards, this access token must be passed in the `Authorization`-header of the http request.

### Example
```shell
# Create the `hello_world` value in the context `my_context` with the content `test123`
curl https://values.my-domain.de/my_context/hello_world/test123 

# Get this value -> Returns: test123
curl https://values.my-domain.de/my_context/hello_world

# Set an auth token:
curl https://values.my-domain.de/my_context/auth_token/my_secret_token

# Try to get the value -> Returns 402
curl https://values.my-domain.de/my_context/hello_world

# Try to get this value with the auth token -> Returns: test123
curl --header Authorization:my_secret_token https://values.my-domain.de/my_context/hello_world

# Delete the auth token
curl -X DELETE --header Authorization:my_secret_token https://values.my-domain.de/my_context/auth_token
```
