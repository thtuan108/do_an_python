from django.template.defaulttags import register

@register.filter
def get_value(dictionary, key):
    """
    input: dictionary và key
    output: giá trị tương ứng với key
    """
    return dictionary.get(key)
