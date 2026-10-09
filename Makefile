.PHONY: setup run run-snowflake app serve
setup:          ## install dependencies
	pip install -r requirements.txt
run:            ## run every product locally (DuckDB) and log it
	python -m switchyard.run
run-snowflake:  ## run every product on Snowflake and log it to PLATFORM.OPS
	python -m switchyard.run --target snowflake
app:            ## build the combined app from the ops log
	python -m app.build_app
serve:          ## open the app at http://localhost:8000
	cd app/build && python -m http.server 8000
