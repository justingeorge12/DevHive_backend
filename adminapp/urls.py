
from django.urls import path, include
from . views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'tags', ManageTag, basename= 'tags')
router.register(r'product', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)), 
    path('usermanage',UserList.as_view(), name='usermanage'),
    path('usermanage/<int:id>',UserManage.as_view(), name='usermanage'),
    path('listquestion', ListQuestions.as_view(), name='listquestion'),
    path('listanswers', ListAnswers.as_view(), name='listanswers'),
    path('onequestiondetail/<int:id>', AdminQuestionDetailView.as_view(), name='onequestiondetail'),
    path('questionsanswer/<int:id>', AdminQuestionAnswerView.as_view(), name='questionsanswer'),
    path('questindelete/<int:id>', DeleteQuestionView.as_view(), name='questindelete'),
    path('deleteanswer/<int:id>', DeleteAnswerView.as_view(), name='deleteanswer'),
    path('blockuser/<int:pk>', BlockUserView.as_view(), name='blockuser'),
    path('orderlist', OrdersList.as_view(), name='orderlist'),
    path('oneorderdetails/<int:id>', OrderRetriveView.as_view(), name='oneorderdetails'),
    path('changeorderstatus/<int:id>',OrderStatusUpdateView.as_view(), name='changeorderstatus'),
]
