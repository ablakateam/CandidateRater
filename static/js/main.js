// Add any global JavaScript functionality here

// Example: Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Example: Toggle mobile menu (if you decide to add one later)
// const mobileMenuButton = document.getElementById('mobile-menu-button');
// const mobileMenu = document.getElementById('mobile-menu');

// if (mobileMenuButton && mobileMenu) {
//     mobileMenuButton.addEventListener('click', () => {
//         mobileMenu.classList.toggle('hidden');
//     });
// }
