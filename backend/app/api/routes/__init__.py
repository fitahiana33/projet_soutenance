from app.api.routes.authentication.auth import router as auth_router
from app.api.routes.users.user import router as user_router
from app.api.routes.roles.role import router as role_router
from app.api.routes.permissions.permission import router as permission_router
from app.api.routes.dolibarr.dolibarr import router as dolibarr_router
from app.api.routes.products.product import router as product_router
from app.api.routes.stocks.stock import router as stock_router

routers = [
    auth_router,
    user_router,
    role_router,
    permission_router,
    dolibarr_router,
    product_router,
    stock_router,
]
