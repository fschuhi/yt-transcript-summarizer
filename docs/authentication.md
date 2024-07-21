---
layout: default
title: Authentication workflow
---

21.07.24 (simple API_KEY)

1. When a user visits the root endpoint ("/") of the web app, the `read_root` function in `main.py` is called. This function renders the `summarizer-form.html` template using Jinja2 and returns it as a response to the user's browser.

2. The rendered HTML page includes the `script.js` file, which contains the JavaScript code for handling form submission and authentication.

3. When the user submits the form on the web page, the `handleSubmit` function in `script.js` is called. This function first checks if the `accessToken` variable is set. If it's not set, it means the user hasn't authenticated yet.

4. If the user hasn't authenticated, the `login` function in `script.js` is called. This function prompts the user to enter their API key using the `prompt` function.

5. If the user enters an API key and clicks "OK", the `login` function sends a POST request to the `/login` endpoint of the FastAPI backend. The API key is included in the request headers as `X-API-Key`.

6. In `main.py`, the `/login` endpoint is defined with the `login` function. This function uses the `get_api_key` dependency, which is responsible for validating the API key.

7. The `get_api_key` function in `main.py` retrieves the API key from the request headers using the `api_key_header` dependency. It then compares the provided API key with the `API_KEY` variable loaded from the `.env` file.

   - If the API key matches, the `get_api_key` function returns the API key, indicating that the authentication is successful.
   - If the API key doesn't match, the `get_api_key` function raises an `HTTPException` with a status code of 403 (Forbidden) and an error message.

8. If the authentication is successful, the `/login` endpoint returns a JSON response containing the `access_token` (which is the same as the API key) and the `token_type` (set to "bearer").

9. Back in the `login` function of `script.js`, if the response from the `/login` endpoint is successful (indicated by `response.ok`), the `access_token` is extracted from the response JSON and stored in the `accessToken` variable. The function then returns `true` to indicate a successful login.

10. If the response from the `/login` endpoint is not successful, an alert is shown to the user with the message "Invalid API key", and the function returns `false`.

11. After a successful login, the `handleSubmit` function in `script.js` proceeds to submit the summarization request to the `/summarize` endpoint of the FastAPI backend. The `accessToken` is included in the request headers as `X-API-Key`.

12. In `main.py`, the `/summarize` endpoint is defined with the `summarize` function. This function also uses the `get_api_key` dependency to validate the API key included in the request headers.

13. If the API key is valid, the `summarize` function proceeds to process the summarization request. If the API key is invalid, the `get_api_key` function raises an `HTTPException`, and the summarization request is not processed.

In summary, the authentication process works as follows:
- The user enters their API key on the web page when prompted.
- The API key is sent to the `/login` endpoint of the FastAPI backend.
- The FastAPI backend validates the API key using the `get_api_key` dependency.
- If the API key is valid, the `/login` endpoint returns an access token (which is the same as the API key).
- The access token is stored in the `accessToken` variable in the JavaScript code.
- Subsequent requests to the `/summarize` endpoint include the access token in the request headers for authentication.
- The FastAPI backend validates the access token using the `get_api_key` dependency before processing the summarization request.

This authentication mechanism ensures that only users with a valid API key can access the summarization functionality of the web app.