from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):  # Chỉ xử lý nếu là dictionary
        return dictionary.get(key)
    return None  # Trả về None nếu không phải dictionary
