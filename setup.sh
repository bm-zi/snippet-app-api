# Run this script from current directory by following command:
# sh setup.sh

echo '______________________ docker-compose down --volumes ________________________'
docker-compose down --volumes
echo

echo '___________________ rm -r app/core/migrations ___________________'
rm -r app/core/migrations
echo

echo '_________ docker-compose run --rm app sh -c "python manage.py makemigrations core" _______'
docker-compose run --rm app sh -c "python manage.py makemigrations core"
echo

echo '_________ docker-compose run --rm app sh -c "python manage.py migrate" ____________'
docker-compose run --rm app sh -c "python manage.py migrate"
echo

echo '__________ docker-compose run --rm app sh -c "python manage.py createsuperuser" _______'
docker-compose run --rm app sh -c "python manage.py createsuperuser"
echo

echo '___________________ docker-compose up _________________'
docker-compose up

# echo '__________ docker-compose run --rm app sh -c "python manage.py test && flake8" ___________'
# docker-compose run --rm app sh -c "python manage.py test && flake8"