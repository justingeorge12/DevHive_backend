
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry

from .models import Question

@registry.register_document
class QuestionDocument(Document):
    class Index:
        name = 'questions'
        settings = {"number_of_shards":1,"number_of_replicas":0}

    class Django:
        model = Question
        fields = ['title', 'body', 'pos_vote', 'answer_count']




















# # documents.py
# from django_elasticsearch_dsl import Document, Index, fields
# from django_elasticsearch_dsl.registries import registry
# from .models import Question
# from .models import Tag

# # Define the index
# question_index = Index('questions')  # Name of the Elasticsearch index

# # Optional settings for the index
# question_index.settings(
#     number_of_shards=1,
#     number_of_replicas=0
# )

# @registry.register_document
# @question_index.document
# class QuestionDocument(Document):
#     tags = fields.ObjectField(properties={
#         'name': fields.TextField()
#     })

#     class Django:
#         model = Question  # The model associated with this document

#         # Fields to be indexed in Elasticsearch
#         fields = [
#             'title', 'body', 'pos_vote', 'neg_vote', 'created', 'closed', 'accepted', 'answer_count',
#         ]

#         # If there are foreign key relationships you want to add, you can define custom fields.
#         related_models = [Tag]

#     def get_queryset(self):
#         return super(QuestionDocument, self).get_queryset().select_related('user').prefetch_related('tags')
