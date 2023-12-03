import dateparser
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


class CamerasService:
    cameras: list[Camera] = []
    """Singleton local storage of cameras.
    """

    CAMERAS_API = "https://datos.vigo.org/data/trafico/camaras-trafico.json"
    """Returns a JSON Array of Camera-parseable objects.
    """

    CAMERA_PICTURE_ENDPOINT = "https://camaras.vigo.org/webcam/cam.php?id={id}"

    @classmethod
    def _get_camera_picture_endpoint(cls, camera_id: str) -> str:
        return cls.CAMERA_PICTURE_ENDPOINT.format(id=camera_id)

    @classmethod
    def _get_http_client(cls):
        return httpx.AsyncClient(verify=False)

    @classmethod
    async def load_cameras_to_cache(cls):
        cls.cameras = await cls.get_cameras_from_api()
        return cls.cameras

    @classmethod
    async def get_cameras_from_api(cls):
        async with cls._get_http_client() as client:
            client: httpx.AsyncClient
            r = await client.get(cls.CAMERAS_API)
            r.raise_for_status()

            return [Camera.model_validate(camera_dict) for camera_dict in r.json()]

    @classmethod
    async def get_camera_last_picture_timestamp(cls, camera_id: str) -> int:
        """Camera picture endpoint returns a header 'Last-Modified' corresponding with the datetime of the currently
        served picture snapshot. Example: 'Sun, 03 Dec 2023 18:51:34 GMT'
        """
        async with cls._get_http_client() as client:
            client: httpx.AsyncClient
            r = await client.head(cls._get_camera_picture_endpoint(camera_id))
            r.raise_for_status()
            last_modified_header = r.headers["Last-Modified"]
            return int(dateparser.parse(last_modified_header).timestamp())

    @classmethod
    async def get_camera_picture(cls, camera_id: str) -> bytes:
        async with cls._get_http_client() as client:
            client: httpx.AsyncClient
            r = await client.get(cls._get_camera_picture_endpoint(camera_id))
            r.raise_for_status()
            return await r.aread()
