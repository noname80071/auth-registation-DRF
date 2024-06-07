from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample
from django.contrib.auth.models import User
from .serializers import *

from random import choices
import string


class UserRegistrationView(GenericAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer

    # ////////////////DOCS/////////////////////
    @extend_schema(summary='Регистрация пользователя',
                   description='Регистрация пользователя. '
                               'После получения запроса сервер отправляет на указаную почту код.')
    # /////////////////////////////////////
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            code = ''.join(choices(string.digits, k=6))

            # Отправление письма на почту.
            send_mail(
                'Код подтверждения',
                f'Ваш код подтверждения: {code}',
                'noname80071',
                [email],
                fail_silently=False,
            )

            request.session['email'] = email
            request.session['username'] = username
            request.session['password'] = password
            request.session['registration_code'] = code

            return Response({'username': username,
                             'email': email}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationSuccess(GenericAPIView):
    serializer_class = VerificationCodeSerializer

    # ////////////////DOCS/////////////////////
    @extend_schema(summary='Подтверждение почты',
                   description='Подтвеждения кода отправленного на почту. После получения запроса и проверки кода, '
                               'сервер зарегистрирует аккаунт в базу данных.',
                   examples=[OpenApiExample(
                       'Example',
                       value={
                           'detail': 'Код подтверждён.'
                       },
                       response_only=True
                   )])
    # /////////////////////////////////////
    def post(self, request):
        email = request.session['email']
        username = request.session['username']
        password = request.session['password']

        code = request.session.get('registration_code')
        if not code:
            return Response({'error': 'Пожалуйста, сначала запросите код подтверждения'},
                            status=status.HTTP_400_BAD_REQUEST)

        confirmation_serializer = VerificationCodeSerializer(data=request.data)
        if confirmation_serializer.is_valid():
            entered_code = confirmation_serializer.validated_data['code']
            if entered_code != code:
                return Response({'error': 'Неверный код подтверждения'},
                                status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(username=username, email=email)
            user.set_password(password)
            user.is_active = True
            user.save()

            return Response({'detail': 'Пользователь успешно создан'},
                            status=status.HTTP_201_CREATED)
        else:
            return Response(confirmation_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
