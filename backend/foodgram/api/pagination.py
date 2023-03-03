from rest_framework.pagination import LimitOffsetPagination


class MinLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 6
