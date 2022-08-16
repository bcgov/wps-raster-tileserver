import logging
from fastapi import APIRouter
from fastapi import Response
from rio_tiler.io import COGReader
from rio_tiler.errors import TileOutsideBounds
from rasterio.errors import RasterioIOError
from rio_tiler.utils import render
from decouple import config
from cogtiler.classify import ftl, hfi

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v0.0.1"
)

cache_control = config('CACHE-CONTROL', 'max-age=604800')

@router.get('/tile/{z}/{x}/{y}')
def tile_xyz(z: int, x: int, y: int, path: str, source: str) -> Response:
    """
    Prepare your images:
    ```bash
    gdal_translate ftl2018.bin ftl_2018.tif -co TILED=YES -co COMPRESS=DEFLATE
    gdaladdo -r nearest ftl_2018.tif 2 4 8 16 32
    gdal_translate ftl_2018.tif ftl_2018_cloudoptimized.tif -co TILED=YES -co COMPRESS=LZW -co COPY_SRC_OVERVIEWS=YES
    ```
    """
    s3_url = f's3://{path}'
    logger.info('/ftl/%s/%s/%s?path=%s ; s3_url: %s', z, x, y, path, s3_url)
    try:
        with COGReader(s3_url) as image:
            try:
                img = image.tile(x, y, z)
            except TileOutsideBounds:
                response = Response(status_code=404)
                response.headers["Cache-Control"] = cache_control
                return response
            if source == 'ftl':
                data, mask = ftl.classify(img.data)
            elif source == 'hfi':
                data, mask = hfi.classify(img.data)
    except RasterioIOError:
        # If the file is not found, return 404
        response = Response(status_code=404)
        return response
    # TODO: This part (`render`) gives an error:
    # "ERROR 4: `/vsimem/xxxx.tif' not recognized as a supported file format."
    # We can replace this with a different method. It's just taking an array of rgba values
    # and turning it into a png file.
    rendered = render(data, mask)
    response = Response(content=rendered, media_type="image/png")
    # cache it for a week - we probably only need to cache for a day or two, but this is on
    # the client, so we don't care.
    response.headers["Cache-Control"] = cache_control
    return response


@router.get('/value/{band}/{lat}/{lon}')
def value(band: int, lat: float, lon: float, path: str) -> Response:
    s3_url = f's3://{path}'
    try:
        with COGReader(s3_url) as image:
            point = image.point(lon, lat, indexes=band)
            # TODO: put in nice json response. This could even be a nice geojson thing
            return point[band - 1]
    except RasterioIOError:
        # If the file is not found, return 404
        response = Response(status_code=404)
        return response