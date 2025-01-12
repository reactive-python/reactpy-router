from example.resolvers import CustomResolver

from reactpy_router.routers import create_router

# This can be used in any location where `browser_router` was previously used
custom_router = create_router(CustomResolver)
