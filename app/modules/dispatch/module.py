def register(app):
    from app.modules.dispatch.routes import router
    app.include_router(router)
