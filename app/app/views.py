from django.http import HttpResponse


def index(request):
    return HttpResponse('''
    <pre>
    APIs urls:

    http://127.0.0.1:8000/admin/
    http://127.0.0.1:8000/api/schema/ [name='api-schema']
    http://127.0.0.1:8000/api/docs/ [name='api-docs']
    http://127.0.0.1:8000/api/user/
    http://127.0.0.1:8000/api/user/me
    http://127.0.0.1:8000/api/user/token
    http://127.0.0.1:8000/api/user/create
    http://127.0.0.1:8000/api/snippet/
    http://127.0.0.1:8000/api/snippet/snippets
    http://127.0.0.1:8000/api/snippet/source_codes
    http://127.0.0.1:8000/api/snippet/tags
    </pre>''')
