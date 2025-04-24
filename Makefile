
run:
	docker-compose up --build -d
	docker build -t api8inf349 .
	sleep 1
	docker run --env-file .env api8inf349:latest flask init-db
	docker run --network host --env-file .env api8inf349:latest flask run --host=0.0.0.0

logs:
	docker logs api8inf349

clean:
	docker-compose down -v
	docker system prune -f
