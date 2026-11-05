from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ვთიშავთ მხოლოდ დამხმარე ტექსტს ეკრანზე
        self.fields["username"].help_text = None
