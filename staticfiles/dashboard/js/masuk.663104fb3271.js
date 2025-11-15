// Fungsi untuk toggle password visibility
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

// Handle form login
function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    // Validasi field kosong
    if (!email || !password) {
        alert('Mohon isi semua field yang diperlukan');
        return;
    }
    
    // Validasi format email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Format email tidak valid');
        return;
    }
    
    // Di sini Anda bisa menambahkan logika untuk mengirim data ke server
    alert('Login berhasil! (Demo)');
    
    // Redirect ke halaman utama setelah login berhasil
    window.location.href = 'LandingPage.html';
}

// Handle forgot password
function handleForgotPassword(e) {
    e.preventDefault();
    alert('Fitur reset password akan segera hadir!');
}

// Handle registrasi button - REDIRECT KE HALAMAN REGISTRASI
function handleRegister(e) {
    e.preventDefault();
    // Redirect ke halaman registrasi.html
    window.location.href = 'registrasi.html';
}

// Handle Google login
function handleGoogleLogin(e) {
    e.preventDefault();
    alert('Login dengan Google akan segera tersedia!');
}

// Override tombol kembali untuk kembali ke LandingPage.html
window.addEventListener('DOMContentLoaded', function() {
    const backButton = document.querySelector('.back-button');
    if (backButton) {
        backButton.onclick = function(e) {
            e.preventDefault();
            // Redirect ke halaman LandingPage.html
            window.location.href = 'LandingPage.html';
        };
    }
});

console.log('masuk.js loaded successfully!');