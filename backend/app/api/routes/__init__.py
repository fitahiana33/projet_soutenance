from app.api.routes.authentication.auth import router as auth_router
from app.api.routes.users.user import router as user_router
from app.api.routes.roles.role import router as role_router
from app.api.routes.permissions.permission import router as permission_router
from app.api.routes.dolibarr.dolibarr import router as dolibarr_router
from app.api.routes.products.product import router as product_router
from app.api.routes.stocks.stock import router as stock_router
from app.api.routes.purchases.purchase import router as purchase_router
from app.api.routes.sales.sales import router as sales_router
from app.api.routes.hr.hr import router as hr_router
from app.api.routes.hr.holidays import router as holidays_router
from app.api.routes.recruitment.recruitment import router as recruitment_router
from app.api.routes.audit.audit import router as audit_router
from app.api.routes.system.system import router as system_router

routers = [
    auth_router,
    user_router,
    role_router,
    permission_router,
    dolibarr_router,
    product_router,
    stock_router,
    purchase_router,
    sales_router,
    hr_router,
    holidays_router,
    recruitment_router,
    audit_router,
    system_router,
]
