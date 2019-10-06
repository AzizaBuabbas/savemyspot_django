from django.shortcuts import render
from django.views import View
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,

)
from rest_framework.views import APIView

from .serializers import (
    UserCreateSerializer, 
    UserLoginSerializer,  
)

from .serializers import (
    RestaurantListSerializer,
    QueueCreateSerializer,
    RestaurantDetailSerializer,
    QueueListSerializer
    
    
)
from .models import (
    Restaurant,
    Queue,
    RestaurantUser

)
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.http import Http404


class RestraurantListView(ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantListSerializer

class RestaurauntDetailView(RetrieveAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'restaurant_id'


class QueueView(APIView):
    def get(self, request):
        obj = request.data
        restaurant = Restaurant.objects.get(id = obj['restaurant'])
        queue = Queue.objects.filter(restaurant= restaurant)
        
        return Response(QueueListSerializer(queue, many=True).data)

    def post(self, request):
        obj = request.data
        user = User.object.get(id = obj['user'])
        restaurant = Restaurant.objects.get(id = obj['restaurant'])
        queue_obj = Queue(user = user, restaurant = restaurant, guests = obj['guests'] )
        queue_obj.increment_position()
        queue_obj.save()
    
        return Response(RestaurantListSerializer(restaurant).data)
        
    def delete(self, request, queue_id):
        queue = Queue.objects.get(id= queue_id)
        restaurant_queues = Queue.objects.filter(restaurant = queue.restaurant.id).order_by('position')
        restaurant = Restaurant.objects.get(id = queue.restaurant.id)
        pos = queue.position
        queue.delete()

        for q in range(0 , len(restaurant_queues)):
            if restaurant_queues[q].position > pos:
               restaurant_queues[q].position -= 1
               restaurant_queues[q].save()

        return Response(QueueListSerializer(queue).data)

class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer

class UserLoginAPIView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        my_data = request.data
        serializer = UserLoginSerializer(data=my_data)
        if serializer.is_valid(raise_exception=True):
            valid_data = serializer.data
            return Response(valid_data, status=HTTP_200_OK)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)
        

