from rest_framework import serializers
from .models import Profile
from apps.users.serializers import UserSerializer


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    bio = serializers.CharField(allow_blank=True, required=False)
    # image = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('id', 'bio', 'user')
        # read_only_fields = ('username',)

    # def get_image(self, obj):
    #     if obj.image:
    #         return obj.image
    #
    #     return 'https://static.productionready.io/images/smiley-cyrus.jpg'