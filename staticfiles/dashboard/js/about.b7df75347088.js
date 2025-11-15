// about.js
document.addEventListener("DOMContentLoaded", () => {
    console.log("Halaman Tentang Kami siap ✅");
    
    // Contoh: animasi sederhana pada scroll
    const aboutSection = document.querySelector('.about-section');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            aboutSection.classList.add('visible');
        }
    });
});
