
for file in `ls *.tif *.tiff`; do
    echo $file
    gdal_translate $file tmp.tif -co TILED=YES -co COMPRESS=DEFLATE
    gdaladdo -r nearest tmp.tif 2 4 8 16 32
    gdal_translate tmp.tif cog/cog_$file -co TILED=YES -co COMPRESS=LZW -co COPY_SRC_OVERVIEWS=YES
    rm tmp.tif
done