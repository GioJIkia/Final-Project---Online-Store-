from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # ვთიშავთ ყველანაირ ნაგულისხმევ დამხმარე ტექსტს პაროლის ველებიდან,
            if "password1" in self.fields:
                self.fields["password1"].help_text = None
            if "password2" in self.fields:
                self.fields["password2"].help_text = None
    def clean_username(self):
        username = self.cleaned_data.get("username")

        if not username:
            return username
        
        # სიგრძის შემოწმება
        if len(username) < 4:
            raise ValidationError(
                "მომხმარებლის სახელი უნდა შედგებოდეს მინიმუმ 4 სიმბოლოსგან."
            )

        # ლათინური ასოების, ციფრების და დაშვებული სიმბოლოების შემოწმება
        if not username.isalpha() or not username.isascii():
            raise ValidationError(
                "მომხმარებლის სახელი უნდა შედგებოდეს მხოლოდ ლათინური ასოებისგან."
            )
        
        # გამოვრიცხოთ სფეისები (სიცარიელეები) იუზერნეიმში
        if " " in username:
            raise ValidationError(
                "მომხმარებლის სახელი არ უნდა შეიცავდეს ცარიელ ადგილებს (სფეისებს)."
            )

        return username

    def clean_password1(self):
        password = self.cleaned_data.get("password1")

        if not password:
            return password

        # სიგრძის შემოწმება (მინიმუმ 8 სიმბოლო)
        if len(password) < 8:
            raise ValidationError("პაროლი უნდა შედგებოდეს მინიმუმ 8 სიმბოლოსგან.")

        # პირველი ასო უნდა იყოს დიდი
        if not password[0].isupper():
            raise ValidationError("პაროლის პირველი სიმბოლო უნდა იყოს დიდი ასო.")

        # მხოლოდ ლათინური ასოები, ციფრები და სიმბოლოები 
        if not password.isascii():
            raise ValidationError(
                "პაროლი უნდა შედგებოდეს მხოლოდ ლათინური ასოებისგან, ციფრებისა და სიმბოლოებისგან."
            )

        return password
