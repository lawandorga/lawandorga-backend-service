import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "config.asgi:application",
        reload=True,
        lifespan="off",
        # workers=2,  ignored because of reload=True
        log_config="./logconfig.json",
    )
