"""
Forms used by the site for validating user input.

Author: Stephen Xie <[redacted]@cmu.edu>
Version: 1.2.0
"""
from django import forms
from django.contrib.auth.models import User

from site_models.models import Message, UserExtended


class UserLoginForm(forms.Form):
    """
    Form for validating user login information.
    """
    username = forms.CharField(max_length=30,
                               widget=forms.TextInput(
                                   # customize html attribute of the
                                   # generated <input> tag from the widget
                                   # instance instantiation
                                   attrs={
                                       # name of the input field will be displayed
                                       # as placeholder
                                       'placeholder': 'Username',
                                       # this element automatically gets focus when the page loads.
                                       # Note-to-self: we can't use HTML5's attribute minimization (i.e.
                                       # just an 'autofocus' boolean attribute) because attrs is a dictionary.
                                       'autofocus': 'autofocus',
                                       # must add the 'autofocus_field' id to all autofocus fields;
                                       # it will be used during error modal toggling (js/toggle-error-modal.js).
                                       'id': 'autofocus_field',
                                       # inform browser that automatic completion feature can be enabled
                                       # for this field
                                       'autocomplete': 'username'
                                   }
                               ))
    password = forms.CharField(max_length=200,
                               label='password',
                               widget=forms.PasswordInput(
                                   attrs={
                                       'placeholder': 'Password',
                                       'autocomplete': 'current-password'
                                   }
                               ))

    # the PasswordInput widget corresponds to the HTML form
    # widget <input type="password">

    # override form validation for the username field
    def clean_username(self):
        username = self.cleaned_data.get('username')  # get the normalized username data
        if not User.objects.filter(username__exact=username):
            raise forms.ValidationError('Cannot find this username in our record.')

        # generally return the cleaned data we got from the cleaned_data dictionary
        return username


class UserPasswordForm(forms.Form):
    """
    Form for validating user password input.
    """
    password = forms.CharField(max_length=100,
                               label='password',
                               widget=forms.PasswordInput(
                                   attrs={
                                       'placeholder': 'Password',
                                       'autocomplete': 'new-password',
                                       'autofocus': 'autofocus',
                                       'id': 'autofocus_field',
                                       'class': 'form-control'
                                   }
                               ))
    # the PasswordInput widget corresponds to the HTML form
    # widget <input type="password">
    password_confirm = forms.CharField(max_length=100,
                                       label='password',
                                       widget=forms.PasswordInput(
                                           attrs={
                                               'id': 'password-confirm',
                                               'placeholder': 'Confirm password',
                                               'class': 'form-control'
                                           }
                                       ))

    # override the forms.Form.clean function; this customize
    # form validations so that user input data conform to
    # a specified format
    def clean(self):
        # call parent(forms.Form)'s clean function, and get a
        # dictionary of cleaned data
        cleaned_data = super(UserPasswordForm, self).clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        # confirm that the two passwords do match
        # Note: don't need to check beforehand the two password fields are
        # not None, because by default, each Field class assumes the value
        # is required, so if you pass an empty value – either None or the
        # empty string ("") – then clean() will raise a ValidationError
        # exception, therefore the two fields are guaranteed to contain
        # non-empty strings.
        if password != password_confirm:
            raise forms.ValidationError("Passwords did not match.")

        # generally return the cleaned data we got from parent
        return cleaned_data


class UserRegisterForm(UserPasswordForm):
    """
    Form for validating user login information; inherited from the PasswordForm.
    """
    first_name = forms.CharField(max_length=30,
                                 widget=forms.TextInput(
                                     attrs={
                                         'placeholder': 'First name',
                                         'autofocus': 'autofocus',
                                         'id': 'autofocus_field',

                                     }
                                 ))
    last_name = forms.CharField(max_length=30,
                                widget=forms.TextInput(
                                    attrs={
                                        'placeholder': 'Last name'
                                    }
                                ))
    email = forms.EmailField(max_length=100,
                             widget=forms.EmailInput(
                                 attrs={
                                     'placeholder': 'Email'
                                 }
                             ))
    username = forms.CharField(max_length=30,
                               widget=forms.TextInput(
                                   attrs={
                                       'placeholder': 'Username',
                                       # inform browser that automatic completion feature can be enabled
                                       # for this field
                                       'autocomplete': 'username'
                                   }
                               ))
    password = forms.CharField(max_length=100,
                               label='password',
                               widget=forms.PasswordInput(
                                   attrs={
                                       'placeholder': 'Password',
                                       'autocomplete': 'new-password',
                                   }
                               ))
    password_confirm = forms.CharField(max_length=100,
                                       label='password',
                                       widget=forms.PasswordInput(
                                           attrs={
                                               'placeholder': 'Confirm password'
                                           }
                                       ))

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # since this form is inherited from the UserPasswordForm, the password
        # fields will be in front of all fields. This manually specifies the
        # field order if this form is used to automatically generate HTML forms
        self.fields.keyOrder = ['first_name', 'last_name', 'email', 'username', 'password', 'password_confirm']

    # override form validation for the username field
    def clean_username(self):
        # confirms that the username is not already present in the
        # User model database
        username = self.cleaned_data.get('username')  # get the normalized username data
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # generally return the cleaned data we got from the cleaned_data dictionary
        return username


class MessageForm(forms.ModelForm):
    """
    Model form for validating posting messages; created from the Message model.
    """

    class Meta:
        model = Message
        fields = ['message']
        # Note: you should only include properties that will be modified by the USER;
        # if there're any other attributes you need to modify in program, don't include
        # them here, but instead use the save(commit=False) method and add those attributes
        # later, as demonstrated here:
        # https://docs.djangoproject.com/en/1.11/topics/forms/modelforms/#selecting-the-fields-to-use
        widgets = {
            'message': forms.TextInput(
                attrs={
                    'placeholder': 'New Message',
                    'autofocus': 'autofocus',
                    'id': 'autofocus_field',
                    'class': 'text-box'
                }
            ),
            # 'photo': forms.FileInput()
        }


class UserInfoForm(forms.ModelForm):
    """
    Model form for validating content for editing information stored in User
    """
    # all fields are optional
    first_name = forms.CharField(required=False, help_text='30 characters max.')
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'placeholder': 'First name',
                    'autofocus': 'autofocus',
                    'class': 'form-control',
                    'id': 'autofocus_field',
                }
            ),

            'last_name': forms.TextInput(
                attrs={
                    'placeholder': 'Last name',
                    'class': 'form-control',
                    'id': 'last_name'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'placeholder': 'Your email',
                    'class': 'form-control',
                    'id': 'email'
                }
            )
        }


class UserExtInfoForm(forms.ModelForm):
    """
    Model form for validating content for editing information stored in UserExtended
    """
    # all fields are optional
    avatar = forms.ImageField(required=False)
    signature = forms.CharField(required=False)
    gender = forms.ChoiceField(required=False, choices=UserExtended.GENDER_CHOICES)
    age = forms.IntegerField(required=False)
    hometown = forms.CharField(required=False)
    hobby = forms.CharField(required=False)
    bio = forms.CharField(required=False)
    # an additional hidden field signaling backend view of user info modification
    user_info_mod = forms.BooleanField(widget=forms.HiddenInput(), initial=True)

    class Meta:
        model = UserExtended
        # fields also determines the order of auto-generated form fields
        fields = ['avatar', 'signature', 'gender', 'age',
                  'hometown', 'hobby', 'bio']
        widgets = {
            'avatar': forms.FileInput(
                attrs={
                    # attributes for Bootstrap form control and label
                    'class': 'form-control-file',
                    'id': 'avatar-upload'
                }
            ),

            'signature': forms.TextInput(
                attrs={
                    'placeholder': 'A short sentence that will be displayed on your profile cover',
                    'class': 'form-control',
                    'id': 'signature'
                }
            ),

            'age': forms.NumberInput(
                attrs={
                    'placeholder': 'Your age',
                    'class': 'form-control',
                    'id': 'age'
                }
            ),

            'gender': forms.RadioSelect(
                attrs={
                    'class': 'form-control',
                    'id': 'gender'
                }
            ),

            'hometown': forms.TextInput(
                attrs={
                    'placeholder': 'Your hometown',
                    'class': 'form-control',
                    'id': 'hometown'
                }
            ),

            'hobby': forms.TextInput(
                attrs={
                    'placeholder': 'Your hobby',
                    'class': 'form-control',
                    'id': 'hobby'
                }
            ),

            'bio': forms.Textarea(
                attrs={
                    'placeholder': 'A short biography of who you are. Introduce yourself to the world!',
                    'class': 'form-control',
                    'id': 'bio',
                    'cols': 20,
                    'rows': 10
                }
            )
        }
