// Contact Form Handler
document.getElementById('contactForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get form values
    const formData = {
        nama: this.querySelector('input[type="text"]').value,
        email: this.querySelector('input[type="email"]').value,
        subjek: this.querySelectorAll('input[type="text"]')[1].value,
        pesan: this.querySelector('textarea').value
    };
    
    // Show success toast
    showToast('Pesan berhasil dikirim!');
    
    // Reset form
    this.reset();
    
    // Log form data (in production, send to server)
    console.log('Form submitted:', formData);
});

// Toast notification function
function showToast(message) {
    const toast = document.getElementById('toast');
    const toastMessage = toast.querySelector('span');
    
    toastMessage.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Optional: Smooth scroll for back link
document.querySelector('.back-link').addEventListener('click', function(e) {
    e.preventDefault();
    window.history.back();
});