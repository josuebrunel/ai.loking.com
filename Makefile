build:
	# pip install -r requirements.txt
	pip install "fastapi[all]" "uvicorn[standard]" pydantic

run:
	uvicorn app:app --reload
