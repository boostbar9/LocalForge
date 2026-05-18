"""CLI front-end for batch model downloads. Useful for portable builds.

Example:
  python download_models.py sdxl_base esrgan
"""
import asyncio, sys
from model_manager import download_recommended, RECOMMENDED

async def main(ids: list[str]):
    for i in ids:
        if i not in RECOMMENDED:
            print(f"unknown id: {i}; available: {list(RECOMMENDED)}"); continue
        print(f"Downloading {i} …")
        await download_recommended(i)

if __name__ == "__main__":
    ids = sys.argv[1:] or ["sdxl_base", "esrgan"]
    asyncio.run(main(ids))
