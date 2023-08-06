import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "config.asgi:application",
        reload=True,
        lifespan="off",
        host="localhost",
        # workers=2,  ignored because of reload=True
        log_config="./logconfig.json",
    )

# export DJANGO_SETTINGS_MODULE=config.settings.local_postgres
# gunicorn config.asgi:application --bind 0.0.0.0:8000 --timeout 240 -w 4 -k
#   uvicorn.workers.UvicornWorker
# hypercorn config.asgi:application --bind 0.0.0.0:8000 -w 4
