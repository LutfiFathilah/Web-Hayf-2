// Toggle password visibility
function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);
    
    if (input.type === 'password') {
        input.type = 'text';
        button.innerHTML = `
            <svg class="eye-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
            </svg>
            HIDE
        `;
    } else {
        input.type = 'password';
        button.innerHTML = `
            <svg class="eye-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
            </svg>
            SHOW
        `;
    }
}

// Validate password strength
function validatePassword(password) {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);
    
    return password.length >= minLength && hasUpperCase && hasLowerCase && hasNumber;
}

// Validate phone number (Indonesian format)
function validatePhoneNumber(phone) {
    // Regex untuk nomor telepon Indonesia (08xx atau +62)
    const phoneRegex = /^(\+62|62|0)[0-9]{9,12}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
}

// Validate date
function validateDate(day, month, year) {
    const currentYear = new Date().getFullYear();
    
    if (year > currentYear || year < 1900) {
        return false;
    }
    
    if (month < 1 || month > 12) {
        return false;
    }
    
    const daysInMonth = new Date(year, month, 0).getDate();
    if (day < 1 || day > daysInMonth) {
        return false;
    }
    
    return true;
}

// Handle form submission
function handleSubmit(e) {
    e.preventDefault();
    
    // Get form values
    const namaDepan = document.getElementById('namaDepan').value.trim();
    const namaBelakang = document.getElementById('namaBelakang').value.trim();
    const nomorTelepon = document.getElementById('nomorTelepon').value.trim();
    const day = parseInt(document.getElementById('day').value);
    const month = parseInt(document.getElementById('month').value);
    const year = parseInt(document.getElementById('year').value);
    const gender = document.querySelector('input[name="gender"]:checked')?.value;
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validations
    if (!namaDepan || !namaBelakang) {
        alert('Mohon lengkapi nama depan dan nama belakang');
        return;
    }
    
    if (!validatePhoneNumber(nomorTelepon)) {
        alert('Format nomor telepon tidak valid. Gunakan format: 08xxxxxxxxxx atau +62xxxxxxxxxx');
        return;
    }
    
    if (!validateDate(day, month, year)) {
        alert('Tanggal lahir tidak valid');
        return;
    }
    
    if (!gender) {
        alert('Mohon pilih gender');
        return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Format email tidak valid');
        return;
    }
    
    if (!validatePassword(password)) {
        alert('Password harus minimal 8 karakter dengan kombinasi huruf besar, huruf kecil, dan angka');
        return;
    }
    
    if (password !== confirmPassword) {
        alert('Password dan konfirmasi password tidak cocok');
        return;
    }
    
    // Create user data object
    const userData = {
        namaDepan,
        namaBelakang,
        nomorTelepon,
        tanggalLahir: `${day}/${month}/${year}`,
        gender,
        email,
        password
    };
    
    console.log('Data Registrasi:', userData);
    
    // Success message
    alert('Registrasi berhasil! Selamat datang di Kopi Hayf.');
    
    // Redirect to login page
    window.location.href = 'masuk.html';
}

// Handle Google login
function handleGoogleLogin() {
    alert('Login dengan Google akan segera tersedia!');
    // Implement Google OAuth here
}

// Auto-format phone number
document.getElementById('nomorTelepon')?.addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    e.target.value = value;
});

// Limit day, month, year input
document.getElementById('day')?.addEventListener('input', function(e) {
    if (e.target.value > 31) e.target.value = 31;
    if (e.target.value < 0) e.target.value = '';
});

document.getElementById('month')?.addEventListener('input', function(e) {
    if (e.target.value > 12) e.target.value = 12;
    if (e.target.value < 0) e.target.value = '';
});

document.getElementById('year')?.addEventListener('input', function(e) {
    const currentYear = new Date().getFullYear();
    if (e.target.value > currentYear) e.target.value = currentYear;
    if (e.target.value < 1900) e.target.value = 1900;
});

// Password strength indicator (optional enhancement)
document.getElementById('password')?.addEventListener('input', function(e) {
    const password = e.target.value;
    const hint = document.querySelector('.password-hint');
    
    if (password.length === 0) {
        hint.style.color = '#767677';
        return;
    }
    
    if (validatePassword(password)) {
        hint.style.color = '#4CAF50';
        hint.textContent = '✓ Password kuat';
    } else {
        hint.style.color = '#F44336';
        hint.textContent = 'Harap gunakan 8+ karakter, dengan sedikitnya 1 angka dan perpaduan huruf besar dan kecil';
    }
});

// Override tombol kembali untuk kembali ke masuk.html
window.addEventListener('DOMContentLoaded', function() {
    const backButton = document.querySelector('.back-button');
    if (backButton) {
        backButton.onclick = function(e) {
            e.preventDefault();
            // Redirect ke halaman masuk.html
            window.location.href = 'masuk.html';
        };
    }
});

console.log('Registrasi page loaded successfully!');