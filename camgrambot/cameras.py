import pydantic
import httpx


class Camera(pydantic.BaseModel):
    """Model corresponding with the data model from:
    https://datos-ckan.vigo.org/dataset/t-camaras/resource/e8b3f98f-5971-405c-b08a-8fde705564fb
    """
    id: str
    name: str = pydantic.Field(alias="nombre")
    lat: float
    lon: float

    @property
    def url(self):
        return f"https://camaras.vigo.org/webcam/cam.php?id={self.id}"


class CamerasCache:
    cameras: list[Camera] = []
    """Singleton local storage of cameras.
    """

    CAMERAS_API = "https://datos.vigo.org/data/trafico/camaras-trafico.json"
    """Returns a JSON Array of Camera-parseable objects.
    """

    @classmethod
    async def load_cameras_to_cache(cls):
        cls.cameras = await cls.get_cameras_from_api()
        return cls.cameras

    @classmethod
    async def get_cameras_from_api(cls):
        async with httpx.AsyncClient() as client:
            client: httpx.AsyncClient
            r = await client.get(cls.CAMERAS_API)
            r.raise_for_status()

            return [Camera.model_validate(camera_dict) for camera_dict in r.json()]
