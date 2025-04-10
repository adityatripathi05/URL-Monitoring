# backend/apps/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated # Use Annotated for Depends with OAuth2

# Import necessary functions and schemas from our modules
from config.database import get_db_connection
from apps.auth.services import authenticate_user, UserNotFound, InvalidPassword, get_user_by_email
from apps.auth.security import create_access_token, create_refresh_token, decode_token
from apps.auth.schemas import TokenData, UserOut, Token, RefreshTokenRequest, AccessTokenResponse # Import new schemas
from config.settings import get_token_expiry_by_role


router = APIRouter(
    prefix="/auth", # Add prefix for clarity
    tags=["Authentication"] # Add tags for Swagger UI
)

# OAuth2 scheme definition (points to the login route)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_token_data(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    """
    Dependency: Decodes JWT token, validates payload structure, returns TokenData.
    Raises HTTPException 401 if token is invalid or payload structure is wrong.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None: # decode_token returns None on JWTError
        raise credentials_exception
    try:
        # Validate payload structure using TokenData schema
        token_data = TokenData(**payload)
    except Exception: # Catch potential Pydantic validation errors or missing keys
         raise credentials_exception

    # Add check for token type if necessary (e.g., ensure it's an access token)
    if token_data.type != "access":
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data

# Dependency for checking roles
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, token_data: TokenData = Depends(get_current_token_data)):
        if token_data.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return token_data # Or return True, or the role itself

# Example usage: admin_dependency = Depends(RoleChecker(["admin"]))

async def get_current_active_user(
    token_data: Annotated[TokenData, Depends(get_current_token_data)]
) -> UserOut:
    """
    Dependency: Gets validated token data and fetches the corresponding active user.
    Raises HTTPException 404 if user not found, potentially 400 if inactive/unverified.
    """
    user = await get_user_by_email(token_data.sub) # Use email from token subject
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Optional: Add checks for active/verified status if needed
    # if not user.is_verified:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User account not verified")
    return user


@router.post('/login', response_model=Token) # Use Token response model
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    Logs in a user using email/password form data and returns an access token.
    """
    try:
        # form_data.username contains the email
        user = await authenticate_user(form_data.username, form_data.password)
        # authenticate_user returns UserOut on success, raises UserNotFound/InvalidPassword on failure

        # Determine access token expiration based on role from the UserOut object
        access_token_expires = get_token_expiry_by_role(user.role)

        # Create token payload using data from the UserOut object
        token_payload = {"sub": user.email, "role": user.role}

        access_token = create_access_token(
            data=token_payload, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data=token_payload) # Generate refresh token
        return Token(access_token=access_token, refresh_token=refresh_token) # Return both tokens

    except (UserNotFound, InvalidPassword):
        # Catch specific exceptions from authenticate_user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password", # Keep error generic for security
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Log the unexpected error for debugging
        print(f"Unexpected error during login for {form_data.username}: {e}") # Basic print
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred during login.",
        )


# Example protected route using the dependency that returns the full UserOut object
@router.get('/users/me', response_model=UserOut) # Return UserOut schema
async def read_users_me(
    current_user: Annotated[UserOut, Depends(get_current_active_user)]
):
    """
    Protected endpoint: Returns the details of the currently authenticated user.
    """
    return current_user


# Example Admin-only route
@router.get("/admin/test", response_model=dict)
async def admin_test_route(
    # Apply the RoleChecker dependency for 'admin' role
    admin_user_data: Annotated[TokenData, Depends(RoleChecker(["admin"]))]
):
    """
    Example protected endpoint accessible only by users with the 'admin' role.
    """
    return {"message": f"Welcome Admin user: {admin_user_data.sub}"}


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest
):
    """
    Refreshes the access token using a valid refresh token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(refresh_request.refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise credentials_exception

        # Validate payload structure using TokenData schema
        token_data = TokenData(**payload)

        # TODO: Check if refresh token is blacklisted (when blacklist is implemented)
        # if await is_token_blacklisted(token_data.jti):
        #     raise credentials_exception

        # Fetch user details based on the subject (email) from the refresh token
        user = await get_user_by_email(token_data.sub)
        if user is None:
            raise credentials_exception # User associated with token not found

        # Determine new access token expiration based on role
        access_token_expires = get_token_expiry_by_role(user.role)

        # Create new access token payload
        new_token_payload = {"sub": user.email, "role": user.role}

        new_access_token = create_access_token(
            data=new_token_payload, expires_delta=access_token_expires
        )
        return AccessTokenResponse(access_token=new_access_token)

    except Exception as e: # Catch potential decoding errors or other issues
        print(f"Error during token refresh: {e}") # Basic logging
        raise credentials_exception


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token_data: dict = Depends(get_current_token_data), # Validate token first
    db = Depends(get_db_connection)
):
    """
    Endpoint to logout user by blacklisting the refresh token.
    """
    refresh_token_request = RefreshTokenRequest(refresh_token=request.headers.get("Authorization").split("Bearer ")[-1]) # Extract from Authorization header
    if not refresh_token_request or not refresh_token_request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token required for logout"
        )
    await blacklist_token(refresh_token_request.refresh_token, db) # Blacklist the refresh token
    return None # 204 No Content - successful logout with no response body
