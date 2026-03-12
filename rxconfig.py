import reflex as rx

config = rx.Config(
    app_name="comanda_app",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)
