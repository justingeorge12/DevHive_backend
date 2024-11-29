from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class InfiniteScrollPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'  
    max_page_size = 100 



class AdminListPagination(PageNumberPagination):
    page_size = 6
    max_page_size = 100

class MessagePagination(PageNumberPagination):
    page_size = 20
    def get_paginated_response(self, data):
        # Reversing data for correct order from newest to oldest
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': list(reversed(data)),  # Reverse the order here
        })