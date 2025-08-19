from django import forms
from .models import Event
from django.utils.safestring import mark_safe

ICON_CHOICES = [
    ("fa-calendar-check", "Kalendarz (domyślna)"),
    ("fa-cake-candles", "Tort urodzinowy"),
    ("fa-briefcase", "Praca"),
    ("fa-heart", "Serce"),
    ("fa-plane", "Podróż"),
    ("fa-graduation-cap", "Edukacja"),
    ("fa-stethoscope", "Zdrowie"),
    ("fa-gift", "Prezent"),
    ("fa-music", "Muzyka"),
    ("fa-star", "Gwiazdka"),
    ("fa-home", "Dom"),
    ("fa-car", "Samochód"),
    ("fa-utensils", "Jedzenie"),
    ("fa-coffee", "Kawa"),
    ("fa-beer", "Piwo"),
    ("fa-wine-glass", "Wino"),
    ("fa-dumbbell", "Sport"),
    ("fa-running", "Bieganie"),
    ("fa-bicycle", "Rower"),
    ("fa-swimming-pool", "Basen"),
    ("fa-gamepad", "Gry"),
    ("fa-tv", "Telewizja"),
    ("fa-book", "Książka"),
    ("fa-newspaper", "Gazeta"),
    ("fa-laptop", "Komputer"),
    ("fa-mobile-alt", "Telefon"),
    ("fa-camera", "Aparat"),
    ("fa-palette", "Sztuka"),
    ("fa-paint-brush", "Malowanie"),
    ("fa-guitar", "Gitara"),
    ("fa-microphone", "Śpiew"),
    ("fa-theater-masks", "Teatr"),
    ("fa-film", "Film"),
    ("fa-ticket-alt", "Bilet"),
    ("fa-shopping-cart", "Zakupy"),
    ("fa-credit-card", "Płatność"),
    ("fa-bank", "Bank"),
    ("fa-chart-line", "Finanse"),
    ("fa-handshake", "Spotkanie"),
    ("fa-users", "Ludzie"),
    ("fa-user-friends", "Przyjaciele"),
    ("fa-baby", "Dziecko"),
    ("fa-dog", "Pies"),
    ("fa-cat", "Kot"),
    ("fa-leaf", "Natura"),
    ("fa-tree", "Drzewo"),
    ("fa-sun", "Słońce"),
    ("fa-moon", "Księżyc"),
    ("fa-cloud", "Pogoda"),
    ("fa-umbrella", "Deszcz"),
    ("fa-snowflake", "Śnieg"),
    ("fa-fire", "Ogień"),
    ("fa-lightbulb", "Pomysł"),
    ("fa-tools", "Narzędzia"),
    ("fa-wrench", "Naprawa"),
    ("fa-hammer", "Remont"),
    ("fa-paint-roller", "Malowanie"),
    ("fa-broom", "Sprzątanie"),
    ("fa-bath", "Kąpiel"),
    ("fa-bed", "Sen"),
    ("fa-clock", "Czas"),
    ("fa-stopwatch", "Stoper"),
    ("fa-hourglass", "Klepsydra"),
    ("fa-calendar-plus", "Dodaj"),
    ("fa-calendar-minus", "Usuń"),
    ("fa-calendar-times", "Anuluj"),
    ("fa-calendar-day", "Dzień"),
    ("fa-calendar-week", "Tydzień"),
    ("fa-calendar-alt", "Kalendarz"),
    ("fa-bell", "Dzwonek"),
    ("fa-bell-slash", "Wycisz"),
    ("fa-exclamation", "Ważne"),
    ("fa-question", "Pytanie"),
    ("fa-info-circle", "Informacja"),
    ("fa-check-circle", "Sukces"),
    ("fa-times-circle", "Błąd"),
    ("fa-exclamation-triangle", "Ostrzeżenie"),
    ("fa-thumbs-up", "Lubię"),
    ("fa-thumbs-down", "Nie lubię"),
    ("fa-smile", "Uśmiech"),
    ("fa-frown", "Smutek"),
    ("fa-meh", "Neutralny"),
    ("fa-laugh", "Śmiech"),
    ("fa-angry", "Złość"),
    ("fa-surprise", "Zaskoczenie"),
    ("fa-tired", "Zmęczenie"),
    ("fa-dizzy", "Zawroty"),
    ("fa-kiss", "Pocałunek"),
    ("fa-kiss-wink-heart", "Pocałunek z sercem"),
    ("fa-grin", "Grin"),
    ("fa-grin-stars", "Grin z gwiazdkami"),
    ("fa-grin-hearts", "Grin z sercami"),
    ("fa-grin-tears", "Grin ze łzami"),
    ("fa-grin-tongue", "Grin z językiem"),
    ("fa-grin-tongue-wink", "Grin z językiem i mrugnięciem"),
    ("fa-grin-tongue-squint", "Grin z językiem i przymrużeniem"),
    ("fa-grin-squint", "Grin z przymrużeniem"),
    ("fa-grin-squint-tears", "Grin z przymrużeniem i łzami"),
    ("fa-grin-beam", "Grin z promieniami"),
    ("fa-grin-beam-sweat", "Grin z promieniami i potem"),
    ("fa-grin-wink", "Grin z mrugnięciem"),
]

class IconSelect(forms.Select):
    def create_option(self, *args, **kwargs):
        option = super().create_option(*args, **kwargs)
        # Pozwól na HTML w labelu
        option['label'] = mark_safe(option['label'])
        return option

class EventForm(forms.ModelForm):
    icon = forms.ChoiceField(choices=ICON_CHOICES, required=False, label="Ikona wydarzenia", initial="fa-calendar-check", widget=IconSelect())
    class Meta:
        model = Event
        fields = [
            'date', 'category', 'custom_category', 'description', 'is_recurring', 'recurrence_type', 'recurrence_end', 'icon'
        ]
        labels = {
            'date': 'Data:',
            'category': 'Kategoria:',
            'custom_category': 'Własna kategoria:',
            'description': 'Opis:',
            'is_recurring': 'Wydarzenie cykliczne:',
            'recurrence_type': 'Typ powtarzalności:',
            'recurrence_end': 'Data końca powtarzania:',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Wybierz datę'}),
            'category': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Wybierz kategorię'}),
            'custom_category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wpisz własną kategorię'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Opisz wydarzenie', 'rows': 3, 'maxlength': 200}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recurrence_type': forms.Select(attrs={'class': 'form-select'}),
            'recurrence_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Data końca powtarzania'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.date:
            self.fields['date'].initial = self.instance.date.strftime('%Y-%m-%d')
        # Ustaw wartość ikony dla edycji
        if self.instance and self.instance.pk and self.instance.icon:
            self.fields['icon'].initial = self.instance.icon

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        custom_category = cleaned_data.get('custom_category')
        is_recurring = cleaned_data.get('is_recurring')
        recurrence_type = cleaned_data.get('recurrence_type')
        icon = cleaned_data.get('icon')
        
        if category == 'inne' and not custom_category:
            self.add_error('custom_category', 'Podaj własną kategorię dla typu "inne".')
        # Automatycznie ustaw recurrence_type na 'yearly' jeśli cykliczne i brak wyboru
        if is_recurring and (not recurrence_type or recurrence_type == 'none'):
            cleaned_data['recurrence_type'] = 'yearly'
        
        # Upewnij się, że ikona ma wartość domyślną jeśli jest pusta
        if not icon:
            cleaned_data['icon'] = 'fa-calendar-check'
        
        return cleaned_data 