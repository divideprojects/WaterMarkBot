format:
	@pre-commit run --all-files

run:
	@python3 -m dpwatermarkbot

clean:
	@pyclean .
	@rm -rf dpwatermarkbot/*.session dpwatermarkbot/*.session-journal
