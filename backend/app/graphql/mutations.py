import strawberry

@strawberry.type
class AuthPayload:
    success: bool
    token: str | None = None
    error_message: str | None = None

@strawberry.type
class Mutation:
    @strawberry.mutation
    def login_user_mock(self, email: str, password: str) -> AuthPayload:
        if email == "demo@example.com" and password == "password":
            return AuthPayload(
                success=True,
                token="mock_jwt_token_for_" + email
            )
        return AuthPayload(
            success=False,
            error_message="Invalid credentials"
        )
