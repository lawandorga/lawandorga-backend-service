import asyncio

from core.seedwork.api_layer import Router

router = Router()


async def sleep():
    await asyncio.sleep(1)
    print("Slept for 1 seconds.")


@router.api(url="run/", output_schema=str)
async def run_cronjobs():
    loop = asyncio.get_event_loop()
    loop.create_task(sleep())
    return "Started"
