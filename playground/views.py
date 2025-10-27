from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Message


@require_GET
def messages_list(request):
    """Return messages from the database as a list of dicts.

    The view serializes Message objects into simple dictionaries. If there
    are no messages yet, it returns an empty list.
    """
    qs = Message.objects.all()
    data = [
        {
            "id": m.id,
            "text": m.text,
            "sender": m.sender,
            "timestamp": m.timestamp.isoformat(),
        }
        for m in qs
    ]
    return JsonResponse(data, safe=False)


from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from rest_framework_simplejwt.tokens import RefreshToken
import json
from django.views.decorators.csrf import csrf_exempt
import re

@csrf_exempt
@require_POST
def signup(request):
    try:
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        if not username or not password:
            return HttpResponseBadRequest('username and password required')
        # Username rules: 1-16 chars, no spaces, only letters, digits or underscore
        if len(username) > 16:
            return HttpResponseBadRequest('username must be 16 characters or fewer')
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            return HttpResponseBadRequest('username may only contain letters, numbers and underscores')
        if User.objects.filter(username=username).exists():
            return HttpResponseBadRequest('username taken')
        # Password rules: minimum 8 characters
        if len(password) < 8:
            return HttpResponseBadRequest('password must be at least 8 characters')
        user = User.objects.create_user(username=username, password=password)
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {'username': user.username},
        })
    except Exception as e:
        return HttpResponseBadRequest(str(e))


@csrf_exempt
@require_POST
def signin(request):
    """Authenticate a user and return JWT access/refresh tokens.

    Expects JSON body: {"username": "...", "password": "..."}
    Returns 200 with { access, refresh, user } on success, 400 on bad input,
    and 401 if authentication fails.
    """
    try:
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        if not username or not password:
            return HttpResponseBadRequest('username and password required')

        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'detail': 'Invalid credentials'}, status=401)

        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {'username': user.username},
        })
    except Exception as e:
        return HttpResponseBadRequest(str(e))