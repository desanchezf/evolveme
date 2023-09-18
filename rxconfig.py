import reflex as rx

class EvolvemeConfig(rx.Config):
    pass

config = EvolvemeConfig(
    app_name="evolveme",
    # frontend_port=<port>,
    # redis_url="",
    telemetry_enabled=False
    # username="",
)