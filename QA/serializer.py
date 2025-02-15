
from rest_framework import serializers
from .models import *
from adminapp.models import Tag
from user.serializers import ListUsersSeralizer

class QuestionSerializer(serializers.ModelSerializer):
    user = ListUsersSeralizer(read_only = True)
    tags = serializers.SlugRelatedField(
        many = True,
        queryset = Tag.objects.all(),
        slug_field = 'name'
    )

    class Meta:
        model = Question
        fields = ['id', 'title', 'body', 'pos_vote', 'neg_vote', 'created', 'closed', 'accepted', 'answer_count', 'user', 'tags']


    
    def validate(self, data):
        request = self.context.get('request')

        if request.user.is_anonymous:
            raise serializers.ValidationError("User must be authenticated")

        return data
  
    
    def create(self, validate_data):
        tags_data = validate_data.pop('tags')
        question = Question.objects.create(**validate_data)
        
        for tag in tags_data:
            QuestionTag.objects.create(question=question, tag=tag)

        return question  
    

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'tags':
                tags_data = value
                existing_tags = set(instance.tags.all())
                new_tags = {Tag.objects.get_or_create(name=tag.name)[0] for tag in tags_data}
                instance.tags.set(existing_tags.union(new_tags))
            else:
                setattr(instance, attr, value)
        
        instance.save()
        return instance




class QuestionTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionTag
        fields = ['id', 'question', 'tag']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'description']


class AnswerSerializer(serializers.ModelSerializer):
    user = ListUsersSeralizer(read_only = True)
    is_acceptable = serializers.SerializerMethodField()
    class Meta:
        model = Answers
        fields = ['id', 'body', 'pos_vote', 'neg_vote', 'user', 'question', 'accepted', 'is_acceptable']

        extra_kwargs = {
            'user': {'read_only': True}

        }

    def get_is_acceptable(self, obj):
        return obj.user != obj.question.user



class SavedQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    class Meta:
        model = SavedQuestion
        fields = ['id', 'question']

