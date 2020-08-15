from django import template

register = template.Library()

# lvlup
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
    price = switcher.get(number)
    if price:
        return price
    else:
        print(number)
        return "Wystąpił błąd, prawdopodobnie zmieniono operatora, ale nie zmieniono numerów SMS."

# microsms
@register.simple_tag
def change2(number):
    switcher = {
        71480: "1,23 PLN",
        72480: "2,46 PLN",
        73480: "3,69 PLN",
        74480: "4,92 PLN",
        75480: "6,15 PLN",
        76480: "7,38 PLN",
        79480: "11,07 PLN",
        91400: "17,22 PLN",
        91900: "23,37 PLN",
        92022: "24,60 PLN",
        92521: "30,75 PLN"
    }
    price = switcher.get(number)
    if price:
        return price
    else:
        return "Wystąpił błąd, prawdopodobnie zmieniono operatora, ale nie zmieniono numerów SMS."
