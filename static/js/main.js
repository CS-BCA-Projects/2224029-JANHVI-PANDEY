document.addEventListener('DOMContentLoaded', function() {
    // Add bounce effect to buttons on hover
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseover', function() {
            this.classList.add('animate__animated', 'animate__bounce');
        });
    });
});