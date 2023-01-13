# Run this script from current directory by following command:
# sh setup.sh

docker-compose down
docker volume rm snippet-app-api_dev-db-data
rm -r app/core/migrations
docker-compose run --rm app sh -c "python manage.py makemigrations core"
docker-compose run --rm app sh -c "python manage.py migrate"
docker-compose run --rm app sh -c "python manage.py createsuperuser"
docker-compose up
