from django import template

register = template.Library()

@register.filter(name='nan')
def nan(string):
    return True if string == "nan" or string == None else False

@register.filter(name='not_nan')
def not_nan(string):
    return False if string == "nan" or string == None else True

@register.filter(name='RTE')
def RTE(string):
    return True if string == "1" or string == True else False

