from fastapi import FastAPI
from fastapi.routing import APIRoute


_FRAMEWORK_ROUTES = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}


def include_domain_routes(target: FastAPI, *domains: FastAPI) -> None:
    """Add domain endpoints to a shared app without duplicating app lifespans."""
    for domain in domains:
        target.router.routes.extend(
            route
            for route in domain.router.routes
            if isinstance(route, APIRoute) and route.path not in _FRAMEWORK_ROUTES
        )
