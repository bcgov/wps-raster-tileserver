# wps-raster-tileserver
Raster tile server for the Wildfire Predictive Services Unit

## Docker

```bash
docker compose build
docker compose run
```

## Openshift


### Prepare images

```bash
# build and tag raster tile server
docker build . --tag=wps-raster-tileserver:latest

# tag it for upload
docker tag wps-raster-tileserver:latest image-registry.apps.silver.devops.gov.bc.ca/e1e498-tools/wps-raster-tileserver:latest

# log into oc command line
oc login --token=yourtokenhere --server=yourserverhere

# log in to openshift docker
docker login -u developer -p $(oc whoami -t) image-registry.apps.silver.devops.gov.bc.ca

# push it
docker push image-registry.apps.silver.devops.gov.bc.ca/e1e498-tools/wps-raster-tileserver:latest

# prepare nginx - creating a build configuration
# note: for some reason specifying the tag for nginx will result in an image that doesn't support s2i
oc new-build nginx~[git hub repository] --context-dir=[folder with nginx config] --name=[name of buildconfig and imagestream]
# e.g.: oc -n e1e498-tools new-build nginx~https://github.com/bcgov/wps-raster-tileserver.git --context-dir=openshift --name=nginx-raster-tilecache
```

### Deploy

```bash
# deploy pg_tileserv
oc -n e1e498-dev process -f rasterserv.yaml | oc -n e1e498-dev apply -f -
```