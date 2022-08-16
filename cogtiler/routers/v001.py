import logging
from time import perf_counter
from fastapi import APIRouter
from fastapi import Response
from rio_tiler.io import COGReader
from rio_tiler.errors import TileOutsideBounds
from rasterio.errors import RasterioIOError
from rio_tiler.utils import render
from decouple import config
from cogtiler.classify import ftl, hfi
from cogtiler.redis import create_redis

logger = logging.getLogger("gunicorn.error")

router = APIRouter(
    prefix="/v0.0.1"
)

cache_control = config('CACHE-CONTROL', 'max-age=604800')
cache_expiry_seconds = 604800  # 10,080 minutes, 168 hours, 7 days

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
    start = perf_counter()
    s3_url = f's3://{path}'
    key = f'/tile/{z}/{x}/{y}?path={path}&source={source}'
    cache = create_redis()
    logger.info('%s ; s3_url: %s', key, s3_url)
    try:
        cached_data = cache.get(key)
    except Exception as error:
        cached_data = None
        logger.error(error, exc_info=error)
    if cached_data:
        logger.info('redis cache hit %s', key)
        response = Response(content=cached_data, media_type="image/png")
        response.headers["Cache-Control"] = cache_control
        return response
    else:
        logger.info('redis cache miss %s', key)
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
    except Exception as e:
        logger.error(e, exc_info=True)
    # TODO: This part (`render`) gives an error:
    # "ERROR 4: `/vsimem/xxxx.tif' not recognized as a supported file format."
    # We can replace this with a different method. It's just taking an array of rgba values
    # and turning it into a png file.
    rendered = render(data, mask)
    response = Response(content=rendered, media_type="image/png")
    try:
        cache.set(key, rendered, ex=cache_expiry_seconds)
    except Exception as error:  # pylint: disable=broad-except
        logger.error(error, exc_info=error)
    # cache it for a week - we probably only need to cache for a day or two, but this is on
    # the client, so we don't care.
    response.headers["Cache-Control"] = cache_control
    end = perf_counter()
    delta = end - start
    logger.info('/ftl/%s/%s/%s?path=%s&source=%s took %f seconds', z, x, y, path, source, delta)
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