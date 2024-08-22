# Authentication Flow

The YouTube Transcript Summarizer uses JWT (JSON Web Tokens) for authentication. Here's an overview of the authentication process:

1. User Registration
   - Endpoint: POST /register
   - User provides username, email, and password
   - Password is hashed and stored in the database

2. User Login
   - Endpoint: POST /token
   - User provides username/email and password
   - If credentials are valid, a JWT token is generated and returned

3. Authenticated Requests
   - Client includes the JWT token in the Authorization header
   - Format: Authorization: Bearer <token>

4. Token Verification
   - The server verifies the token for each protected endpoint
   - If valid, the request is processed; if not, a 401 Unauthorized response is returned

## JWT Token

- Contains user identifier (sub claim)
- Has an expiration time (exp claim)
- Signed with a secret key

## Security Measures

- Passwords are hashed using bcrypt
- JWT tokens are signed to prevent tampering
- Token expiration limits the window of potential misuse

For implementation details, see `services/user_auth_service.py` and `utils/auth_utils.py`.