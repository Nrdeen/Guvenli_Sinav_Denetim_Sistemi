import reflex as rx

config = rx.Config(
    app_name="object_cheating",
    # Optimize compilation
    timeout=300,  # Increase timeout
    next_compression=False,  # Disable compression to speed up
    react_strict_mode=False,  # Disable strict mode
)