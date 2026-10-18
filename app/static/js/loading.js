document.addEventListener('DOMContentLoaded', function() {
    const cube = document.querySelector('.cube');
    const overlay = document.getElementById('loading-overlay');

    // Animate the cube with anime.js
    anime({
        targets: cube,
        rotateX: '360deg',
        rotateY: '360deg',
        duration: 5000,
        easing: 'easeInOutQuad',
        complete: function() {
            // Hide the overlay after animation completes
            overlay.style.opacity = '0';
            setTimeout(function() {
                overlay.style.display = 'none';
            }, 500); // Match the CSS transition if any
        }
    });
});