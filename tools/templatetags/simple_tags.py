
from django import template

register = template.Library()

@register.simple_tag(name="test_tag")
def test_tag(arg1,arg2):
    return arg1+"_"+arg2+"_test_tag"






