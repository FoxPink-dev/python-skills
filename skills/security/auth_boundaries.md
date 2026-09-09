# Security: Authentication/Authorization Boundaries

**Purpose**: Enforce auth boundaries correctly in code.

**When to use**: Any code with user identity, permissions, or access control.

---

## Core Rules

### Authentication vs Authorization
- **Authentication**: Who are you? (Identity)
- **Authorization**: What can you do? (Permissions)

### Never Trust Client-Side Identity
```python
# WRONG — trusting header
def get_user_profile(request, user_id: str):
    return db.get_user(user_id)  # User can access ANY profile!

# CORRECT — verified identity
def get_user_profile(request, current_user: User):
    if current_user.id != request.path_params["user_id"]:
        raise ForbiddenError()
    return current_user
```

### Authorization at Boundary
```python
# Dependency injection (FastAPI example)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(),
) -> User:
    user = await user_service.verify_token(token)
    if not user:
        raise UnauthorizedError()
    return user

@app.get("/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(),
):
    # Authorization check
    if not current_user.can_access_user(user_id):
        raise ForbiddenError("Cannot access this user")
    return await user_service.get(user_id)
```

### Permission Models
```python
# Role-based
class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

# Permission-based (more flexible)
class Permission(str, Enum):
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    ADMIN_PANEL = "admin:panel"

# User model
class User(BaseModel):
    id: str
    roles: list[Role] = []
    permissions: list[Permission] = []
    
    def has_permission(self, perm: Permission) -> bool:
        return perm in self.permissions or Role.ADMIN in self.roles
    
    def can_access_user(self, user_id: str) -> bool:
        return self.id == user_id or self.has_permission(Permission.USER_READ)
```

### Resource-Level Authorization
```python
# Policy-based
class AuthorizationPolicy:
    def can_read(self, user: User, resource: Resource) -> bool:
        if user.has_permission(Permission.ADMIN):
            return True
        return resource.owner_id == user.id or resource.is_public
    
    def can_write(self, user: User, resource: Resource) -> bool:
        if user.has_permission(Permission.ADMIN):
            return True
        return resource.owner_id == user.id

# Usage
policy = AuthorizationPolicy()

@app.put("/resources/{resource_id}")
async def update_resource(
    resource_id: str,
    data: ResourceUpdate,
    current_user: User = Depends(get_current_user),
    resource_service: ResourceService = Depends(),
):
    resource = await resource_service.get(resource_id)
    if not policy.can_write(current_user, resource):
        raise ForbiddenError()
    return await resource_service.update(resource_id, data)
```

### Secure Session/Cookie Handling
```python
# HttpOnly, Secure, SameSite cookies
response.set_cookie(
    "session",
    session_token,
    httponly=True,
    secure=True,        # HTTPS only
    samesite="lax",     # CSRF protection
    max_age=3600,
)

# CSRF protection for state-changing operations
@app.post("/action")
async def action(
    request: Request,
    csrf_token: str = Form(),
    session: Session = Depends(get_session),
):
    if not verify_csrf(session, csrf_token):
        raise ForbiddenError("Invalid CSRF token")
```

---

## Decision Rules

| Boundary | Enforcement |
|----------|-------------|
| API endpoint | Dependency injection + policy check |
| Database query | Filter by user_id in query (not post-filter) |
| File access | Verify ownership before serve |
| Admin panel | Role check + audit log |
| Internal service | mTLS / service mesh / shared secret |

---

## Preferred Patterns

```python
# Centralized authorization
class AuthorizationService:
    def __init__(self, policy: AuthorizationPolicy):
        self.policy = policy
    
    def authorize(self, user: User, action: str, resource: Resource) -> None:
        if not self.policy.check(user, action, resource):
            raise ForbiddenError(f"Cannot {action} {resource}")

# Decorator for endpoints
def require_permission(perm: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if not current_user.has_permission(perm):
                raise ForbiddenError(f"Requires {perm}")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

@require_permission(Permission.USER_WRITE)
async def create_user(...):
    ...
```

---

## Avoid

- Checking permissions after fetching data (leak via error messages)
- Client-controlled authorization (user_id in body/query)
- Missing authorization on any state-changing endpoint
- Hardcoded role checks (`if user.role == "admin"`) instead of permissions
- No audit logging for sensitive operations

---

## Validation Considerations

- Test with different user roles
- Test resource access boundaries
- Test privilege escalation attempts
- Audit log review

---

## Related Skills

- `security/input_validation.md`
- `security/secrets.md`
- `generation/error_handling.md`
- `engineering/http_clients.md`