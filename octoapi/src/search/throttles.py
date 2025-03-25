from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class SearchUserRateThrottle(UserRateThrottle):
    rate = "1000/day"
    scope = "search_user"


class SearchAnonRateThrottle(AnonRateThrottle):
    rate = "100/day"
    scope = "search_anon"
