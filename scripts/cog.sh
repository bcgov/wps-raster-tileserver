"""
Following instruction from: https://trac.osgeo.org/gdal/wiki/CloudOptimizedGeoTIFF
"""

# Iterate over all the tiff/bin files in the directory, and create cloud optimized geotiffs
for file in `ls *.tif *.tiff *.bin`; do
    echo $file
    # create de-compressed tiled tiff
    gdal_translate $file tmp.tif -co TILED=YES -co COMPRESS=DEFLATE
    # rebuild overview images
    gdaladdo -r nearest tmp.tif 2 4 8 16 32
    # create cloud optimized geotiff
    gdal_translate tmp.tif cog/cog_$file -co TILED=YES -co COMPRESS=LZW -co COPY_SRC_OVERVIEWS=YES \
        -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 --config GDAL_TIFF_OVR_BLOCKSIZE 512
    rm tmp.tif
done