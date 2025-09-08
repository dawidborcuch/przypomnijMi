from django import template

register = template.Library()


@register.filter(name='polish_pluralize')
def polish_pluralize(value, forms):
    """
    Zwraca poprawną polską formę rzeczownika w zależności od liczby.
    Użycie w szablonie:
      {{ count }} {{ count|polish_pluralize:"wydarzenie,wydarzenia,wydarzeń" }}

    Kolejność form: 1, 2-4, 5+
    Reguła: 2-4 jeśli (value % 10 w 2..4) i (value % 100 nie w 12..14)
    """
    try:
        count = int(value)
    except (TypeError, ValueError):
        return ''

    try:
        one, few, many = [s.strip() for s in forms.split(',')]
    except ValueError:
        # jeśli niepoprawny format, zwróć pusty string
        return ''

    if count == 1:
        return one

    mod10 = count % 10
    mod100 = count % 100
    if mod10 in (2, 3, 4) and mod100 not in (12, 13, 14):
        return few
    return many


