import asyncio

from .cameras import CamerasService, Camera


async def tst():
    # TODO Remove
    import random
    cam: Camera = random.choice(CamerasService.cameras)
    last_modified = await CamerasService.get_camera_last_picture_timestamp(cam.id)
    print("Camera", cam, "- Last modified:", last_modified)

    picture_bytes = await CamerasService.get_camera_picture(cam.id)
    with open(f"/media/ram/{cam.name} {last_modified}.jpg", "wb") as f:
        f.write(picture_bytes)


async def amain():
    await CamerasService.load_cameras_to_cache()
    print(*CamerasService.cameras, sep="\n")
    await tst()


def main():
    asyncio.get_event_loop().run_until_complete(amain())
