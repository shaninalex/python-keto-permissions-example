migrate:
	keto migrate up --config=./config/keto.config.yml

serve:
	keto serve --config=./config/keto.config.yml

start:
	uv run python -m src.bootstrap
	uv run python -m src.main

dump:
	@for ns in User Role Order OrderItem; do \
		keto relation-tuple get \
			--namespace "$$ns" \
			--format json \
			--page-size 1000 \
			--read-remote 127.0.0.1:4466 \
			--insecure-disable-transport-security \
		| jq '.relation_tuples'; \
	done | jq -s 'add' > ./config/relation-tuples/tuples.dump.json
	@echo "./config/relation-tuples/tuples.dump.json"