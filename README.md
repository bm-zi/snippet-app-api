## Snippet App API

This project is about creating an API for a repository of code snippets in different programming languages.  

The project created based on 
[Django Rest Framework Tutorial](https://www.django-rest-framework.org/tutorial/quickstart/)


Now assuming the docker and docker-compose is installed and configured properly on you local machine, then you can follow the instruction to get this API launched.  


*Run the following commands from main project directory:*  
```bash
docker-compose run --rm app sh -c "python manage.py makemigrations core"
docker-compose run --rm app sh -c "python manage.py migrate"
docker-compose run --rm app sh -c "python manage.py createsuperuser"
docker-compose up
```

*Or run the setup.sh script from main project directory:*  
```bash
sh setup.sh
```

After creating a super user and bringing up the server,
you can create a token for admin authentication at this following url:
http://127.0.0.1:8000/api/user/token

Then you can include authentication token in the header of your browser.
I use ModHeader for firefox browser.  

You also can view the API documentation in swagger from url:  
http://127.0.0.1:8000/api/docs/


For start, you can post the following json payload to following url, to create a sample code snippet in database.  
http://127.0.0.1:8000/api/snippet/snippets  


```json
{
  "language_name": "python",
  "style": "colorful",
  "linenos": false,
  "highlighted": "",
  "source_code": {
    "title": "my first code snippet",
    "author": "bm-zi",
    "code": "print('Hello world')",
    "notes": "no notes",
    "url": "http://example.com/first_code",
    "status": "C",
    "rating": 1,
    "is_favorite": true
  },
  "tags": [{
    "name": "Django Rest Framework"
  }]
}
```