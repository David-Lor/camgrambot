import asyncio

from .cameras import CamerasCache


async def amain():
    await CamerasCache.load_cameras_to_cache()
    print(*CamerasCache.cameras, sep="\n")


def main():
    asyncio.get_event_loop().run_until_complete(amain())
