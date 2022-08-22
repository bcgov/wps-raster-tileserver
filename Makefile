ifdef VIRTUAL_ENV
POETRY_RUN=
else
POETRY_RUN=poetry run
endif

define run-api
	# function to run api	
	${1} uvicorn cogtiler.main:app --host 0.0.0.0 --reload --port 8090 --log-level debug;
endef

run:
	${call run-api,$(POETRY_RUN)}

run-gunicorn:
	poetry run gunicorn -w 2 -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8090 cogtiler.main:app

run-uvicorn:
	poetry run uvicorn cogtiler.main:app --host 0.0.0.0 --workers 1 --port 8090

notebook:
	# Run jupyter notebooks.
	POSTGRES_HOST=localhost PYTHONPATH=$(shell pwd) JUPYTER_PATH=$(shell pwd) poetry run jupyter notebook --ip 0.0.0.0

bash:
	docker compose run --rm --service-ports server bash
