
docker:
	docker build -t idle_exporter/idle_exporter:0.1.0 . --network host

docker-run:
	docker run --name idle_exporter -d \
	    -p 3003:3003 \
	    idle_exporter/idle_exporter:0.1.0 \
	    bash -c "python ./idle_exporter.py"
