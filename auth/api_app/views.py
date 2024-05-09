from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated  # Import the IsAuthenticated permission
from .models import YourModel
from .serializers import YourModelSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class YourModelViewSet(viewsets.ModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
    permission_classes = [IsAuthenticated] 


class GetAccessTokenView(APIView):
    permission_classes = [IsAuthenticated]  # Only allow authenticated users to request tokens

    def post(self, request, *args, **kwargs):
        user = request.user
        token, created = Token.objects.get_or_create(user=user)
        return Response({'access_token': token.key})