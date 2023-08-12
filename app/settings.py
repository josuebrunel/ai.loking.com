import os

_settings = {
    "LK_NAME": ("LokingAI", str),
    "LK_DEBUG": (False, bool),
    "LK_IMAGE_CTYPES":
    (["image/jpeg", "image/png", "image/gif", "image/svg+xml"], list),
    "LK_IMAGE_MAXSIZE": (5 * 1024 * 1024, int),
}


class AppSettings:

    def __init__(self):
        for key, val in _settings.items():
            val_env = os.getenv(key)
            _, key = key.split("_", 1)
            val_default, val_type = val
            if val_env:
                if val_type is bool:
                    val_default = True if val_env.lower() == "true" else False
                elif val_type is list:
                    val_default = val_env.split(",")
                elif val_type is int:
                    try:
                        val_default = int(val_env)
                    except (ValueError, ):
                        pass
                else:
                    val_default = val_env

            setattr(self, key, val_default)


settings = AppSettings()
