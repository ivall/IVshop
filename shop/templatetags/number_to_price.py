from django import template

register = template.Library()


@register.simple_tag
def change(number):
    switcher = {
        70068: "0,62 PLN",
        7168: "1,23 PLN",
        72068: "2,46 PLN",
        73068: "3,69 PLN",
        74068: "4,92 PLN",
        75068: "6,15 PLN",
        76068: "7,38 PLN",
        79068: "11,07 PLN",
        91068: "12,30 PLN",
        91758: "20,91 PLN",
        92578: "30,75 PLN"
    }
    return switcher.get(number)
