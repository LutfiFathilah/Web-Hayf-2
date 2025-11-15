from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Customer, Review

class LoginForm(AuthenticationForm):
    """Form login dengan pesan error Bahasa Indonesia"""
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'nama@email.com',
            'id': 'loginEmail'
        })
    )
    password = forms.CharField(
        label='Kata Sandi',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Kata Sandi *',
            'id': 'loginPassword'
        })
    )
    
    error_messages = {
        'invalid_login': 'Email atau kata sandi yang Anda masukkan salah.',
        'inactive': 'Akun ini tidak aktif. Silakan hubungi administrator.',
    }


class RegisterForm(UserCreationForm):
    """Form registrasi dengan validasi dan pesan error Indonesia"""
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label='Nama Depan',
        widget=forms.TextInput(attrs={'placeholder': 'Nama Depan *'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        label='Nama Belakang',
        widget=forms.TextInput(attrs={'placeholder': 'Nama Belakang *'})
    )
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'nama@email.com *'})
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        label='Nomor Telepon',
        widget=forms.TextInput(attrs={
            'placeholder': 'Nomor Telepon *',
            'type': 'tel'
        })
    )
    birth_day = forms.IntegerField(
        required=True,
        label='Hari',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Hari',
            'min': 1,
            'max': 31
        })
    )
    birth_month = forms.IntegerField(
        required=True,
        label='Bulan',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Bulan',
            'min': 1,
            'max': 12
        })
    )
    birth_year = forms.IntegerField(
        required=True,
        label='Tahun',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Tahun',
            'min': 1900,
            'max': 2024
        })
    )
    gender = forms.ChoiceField(
        choices=[('pria', 'Pria'), ('wanita', 'Wanita')],
        required=True,
        label='Jenis Kelamin',
        widget=forms.RadioSelect()
    )
    password1 = forms.CharField(
        label='Kata Sandi',
        widget=forms.PasswordInput(attrs={'placeholder': 'Kata Sandi *'}),
        help_text='Minimal 8 karakter, kombinasi huruf dan angka'
    )
    password2 = forms.CharField(
        label='Konfirmasi Kata Sandi',
        widget=forms.PasswordInput(attrs={'placeholder': 'Konfirmasi Kata Sandi *'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize error messages
        self.fields['password1'].error_messages = {
            'required': 'Kata sandi wajib diisi.',
        }
        self.fields['password2'].error_messages = {
            'required': 'Konfirmasi kata sandi wajib diisi.',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email sudah terdaftar. Silakan gunakan email lain atau login.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Validasi format nomor telepon Indonesia
        if not phone.startswith('08') and not phone.startswith('+62'):
            raise ValidationError('Nomor telepon harus diawali dengan 08 atau +62')
        if len(phone) < 10:
            raise ValidationError('Nomor telepon minimal 10 digit')
        return phone
    
    def clean_birth_day(self):
        day = self.cleaned_data.get('birth_day')
        if day and (day < 1 or day > 31):
            raise ValidationError('Hari harus antara 1-31')
        return day
    
    def clean_birth_month(self):
        month = self.cleaned_data.get('birth_month')
        if month and (month < 1 or month > 12):
            raise ValidationError('Bulan harus antara 1-12')
        return month
    
    def clean_birth_year(self):
        year = self.cleaned_data.get('birth_year')
        if year:
            from datetime import datetime
            current_year = datetime.now().year
            if year < 1900 or year > current_year:
                raise ValidationError(f'Tahun harus antara 1900-{current_year}')
            age = current_year - year
            if age < 13:
                raise ValidationError('Anda harus berusia minimal 13 tahun untuk mendaftar')
        return year

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Kata sandi tidak cocok. Silakan coba lagi.')
        
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create customer profile
            from datetime import date
            birth_date = date(
                self.cleaned_data['birth_year'],
                self.cleaned_data['birth_month'],
                self.cleaned_data['birth_day']
            )
            Customer.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                date_of_birth=birth_date,
                gender=self.cleaned_data['gender']
            )
        return user


class CustomerProfileForm(forms.ModelForm):
    """Form edit profile customer"""
    class Meta:
        model = Customer
        fields = ['phone', 'address', 'city', 'state', 'postal_code', 'country', 'profile_image']
        labels = {
            'phone': 'Nomor Telepon',
            'address': 'Alamat Lengkap',
            'city': 'Kota',
            'state': 'Provinsi',
            'postal_code': 'Kode Pos',
            'country': 'Negara',
            'profile_image': 'Foto Profil'
        }
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor Telepon'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Alamat Lengkap', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kota'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Provinsi'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kode Pos'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Negara'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        error_messages = {
            'phone': {
                'required': 'Nomor telepon wajib diisi',
                'invalid': 'Format nomor telepon tidak valid'
            },
            'postal_code': {
                'required': 'Kode pos wajib diisi',
            }
        }


class ReviewForm(forms.ModelForm):
    """Form review produk"""
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        labels = {
            'rating': 'Rating',
            'title': 'Judul Review',
            'comment': 'Komentar'
        }
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'required': True,
                'placeholder': '1-5'
            }),
            'title': forms.TextInput(attrs={'placeholder': 'Judul Review'}),
            'comment': forms.Textarea(attrs={
                'placeholder': 'Tulis review Anda tentang produk ini...',
                'rows': 4
            }),
        }
        error_messages = {
            'rating': {
                'required': 'Rating wajib diisi',
                'min_value': 'Rating minimal 1 bintang',
                'max_value': 'Rating maksimal 5 bintang'
            },
            'comment': {
                'required': 'Komentar wajib diisi',
            }
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise ValidationError('Rating harus antara 1-5 bintang')
        return rating
    
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if comment and len(comment) < 10:
            raise ValidationError('Komentar minimal 10 karakter')
        return comment


class ContactForm(forms.Form):
    """Form kontak"""
    name = forms.CharField(
        max_length=100,
        label='Nama Lengkap',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan nama lengkap'}),
        error_messages={
            'required': 'Nama wajib diisi',
            'max_length': 'Nama maksimal 100 karakter'
        }
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'nama@email.com'}),
        error_messages={
            'required': 'Email wajib diisi',
            'invalid': 'Format email tidak valid'
        }
    )
    subject = forms.CharField(
        max_length=200,
        label='Subjek',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan subjek pesan'}),
        error_messages={
            'required': 'Subjek wajib diisi',
            'max_length': 'Subjek maksimal 200 karakter'
        }
    )
    message = forms.CharField(
        label='Pesan',
        widget=forms.Textarea(attrs={
            'class': 'form-textarea', 
            'placeholder': 'Tulis pesan Anda di sini...',
            'rows': 5
        }),
        error_messages={
            'required': 'Pesan wajib diisi'
        }
    )

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if message and len(message) < 20:
            raise ValidationError('Pesan minimal 20 karakter')
        return message