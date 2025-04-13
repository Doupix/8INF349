
run:
	sudo docker-compose up --build

stop:
	sudo docker-compose down

init-db:
	sudo docker exec -it api8inf349 flask init-db

logs:
	sudo docker logs api8inf349

clean:
	sudo docker-compose down -v
	sudo docker system prune -f
