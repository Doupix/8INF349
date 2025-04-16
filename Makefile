
run:
	docker-compose up --build -d

stop:
	docker-compose down

init-db:
	docker exec -it api8inf349 flask init-db

logs:
	docker logs api8inf349

clean:
	docker-compose down -v
	docker system prune -f
