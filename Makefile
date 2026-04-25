migrate:
	keto migrate up --config=./config/keto.config.yml

serve:
	keto serve --config=./config/keto.config.yml

start:
	uv run python -m src.bootstrap
	uv run python -m src.main