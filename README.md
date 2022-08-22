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
```

### Deploy

```bash
# test deploy
oc -n e1e498-dev process -f rasterserv.yaml | oc -n e1e498-dev apply --dry-run=client -f -
# deploy
oc -n e1e498-dev process -f rasterserv.yaml | oc -n e1e498-dev apply -f -
```