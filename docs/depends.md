---
layout: default
title: What does FastAPI Depends() ?
---

21.07.24 (simple API_KEY)

In FastAPI, `Depends` is a function that is used to declare dependencies for route handlers, endpoint functions, and other dependencies. Dependencies are functions that are called before the route handler or endpoint function is executed. They can perform various tasks, such as authentication, authorization, database connection, or any other necessary operations.

In the given code, `Depends` is used in two places:

1. In the `login` function:
   ```python
   @app.post("/login")
   async def login(api_key: str = Depends(get_api_key)):
       return {"access_token": api_key, "token_type": "bearer"}
   ```
   Here, `Depends(get_api_key)` is used as a default value for the `api_key` parameter. It means that before the `login` function is executed, the `get_api_key` function will be called to retrieve the API key from the request headers.

2. In the `summarize` function:
   ```python
   @app.post("/summarize")
   async def summarize(summarize_request: SummarizeRequest, api_key: str = Depends(get_api_key)):
       # ...
   ```
   Similarly, `Depends(get_api_key)` is used as a default value for the `api_key` parameter. It ensures that the `get_api_key` function is called before the `summarize` function is executed to validate the API key.

Now, let's examine the `get_api_key` function in more detail:

```python
def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )
```

In this function, `Depends(api_key_header)` is used as a default value for the `api_key` parameter. `api_key_header` is an instance of `APIKeyHeader`, which is a built-in dependency class in FastAPI. It is defined as follows:

```python
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
```

`APIKeyHeader` is used to extract the value of the `X-API-Key` header from the request headers. The `name` parameter specifies the name of the header to look for, and `auto_error=False` means that if the header is not found, FastAPI will not automatically raise an error.

When a request is made to the `/login` or `/summarize` endpoint, FastAPI checks if the `X-API-Key` header is present in the request headers. If the header is found, its value is passed as the `api_key` argument to the `get_api_key` function.

Inside the `get_api_key` function, the `api_key` value is compared with the `API_KEY` variable loaded from the `.env` file. If they match, the `api_key` is returned, indicating successful authentication. If they don't match, an `HTTPException` with a status code of 403 (Forbidden) is raised, indicating invalid credentials.

The returned `api_key` value from the `get_api_key` function is then assigned to the `api_key` parameter of the `login` or `summarize` function, respectively.

By using `Depends`, FastAPI automatically resolves the dependencies and passes the resolved values to the corresponding parameters of the route handlers or endpoint functions. This allows for a clean and modular way to handle authentication and other dependencies in the application.

In the JavaScript code (`script.js`), when the `login` function sends a POST request to the `/login` endpoint, it includes the API key in the `X-API-Key` header. FastAPI extracts the value of this header using the `api_key_header` dependency and passes it to the `get_api_key` function for validation.

Similarly, when the `handleSubmit` function sends a POST request to the `/summarize` endpoint, it includes the access token (which is the same as the API key) in the `X-API-Key` header. Again, FastAPI extracts the value using the `api_key_header` dependency and passes it to the `get_api_key` function for validation before executing the `summarize` function.

This dependency injection mechanism provided by FastAPI simplifies the process of handling authentication and allows for a clear separation of concerns between the route handlers and the authentication logic.