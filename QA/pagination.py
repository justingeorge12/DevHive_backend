from rest_framework.pagination import PageNumberPagination

class InfiniteScrollPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'  
    max_page_size = 100 


class MessagePagination(PageNumberPagination):
    page_size = 50
    max_page_size = 100 


class AdminListPagination(PageNumberPagination):
    page_size = 6
    max_page_size = 100