from django.core.paginator import Paginator

NUMBER = 6


def get_page(page_number, posts):
    paginator = Paginator(posts, NUMBER)
    page_obj = paginator.get_page(page_number)
    return page_obj
