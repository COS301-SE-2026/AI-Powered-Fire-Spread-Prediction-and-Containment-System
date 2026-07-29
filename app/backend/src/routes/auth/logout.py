from fastapi import APIRouter, Response

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/logout")
def logout_route(response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {"message": "logged out"}
