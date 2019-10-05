from rest_framework import serializers

from .models import (
    Restaurant,
    Day,
    OperatingTime,
    Category,
    Item,
    Queue,
    RestaurantUser
)

from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class OperatingTimeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatingTime
        fields = '__all__'


class RestaurantListSerializer(serializers.ModelSerializer):
    operatingtime = OperatingTimeListSerializer(many = True)
    queue = serializers.SerializerMethodField()
    class Meta:
        model = Restaurant
        fields = '__all__'

    def get_queue(self, obj):
        return obj.queue.count() 

class QueueListSerializer(serializers.ModelSerializer):
    restaurant = RestaurantListSerializer()
    user = UserSerializer()
    class Meta:
        model = Queue
        fields = '__all__'


class ItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class CategoryListSerializer(serializers.ModelSerializer):
    item = ItemListSerializer(many = True)
    class Meta:
        model = Category
        fields = '__all__'


class RestaurantDetailSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer(many = True)
    queue = QueueListSerializer(many = True)
    operatingtime = OperatingTimeListSerializer(many = True)

    class Meta:
        model = Restaurant
        fields = '__all__'


class QueueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        exclude = ['position',]

    def create(self, validated_data):
        restaurant = validated_data['restaurant']
        user = validated_data['user']
        enter_q = Queue(restaurant= restaurant, user = user)
        enter_q.increment_position()
        enter_q.save()
        return validated_data

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        email = validated_data['email']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        new_user = User(username=username, email= email, first_name = first_name, last_name = last_name)
        new_user.set_password(password)
        new_user.save()
        return validated_data

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(allow_blank=True, read_only=True)
    restaurant = serializers.CharField(allow_blank= True, read_only = True)

    def validate(self, data):
        my_username = data.get('username')
        my_password = data.get('password')

        try:
            user_obj = User.objects.get(username=my_username)

        except:
            raise serializers.ValidationError("This username does not exist")

        if not user_obj.check_password(my_password):
            raise serializers.ValidationError("Incorrect username/password")

        try:
            restaurant_user = RestaurantUser.objects.get(user = user_obj)
            data['restaurant']= restaurant_user.id

        except:
            pass

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user_obj)
        token = jwt_encode_handler(payload)

        
        data["token"] = token

        return data

class QueueUserSerializer(serialzers.ModelSerializer):
    restaurant = RestaurantDetailSerializer()
    
    class Meta:
        model = Qeueu
        fields = '__all__'



