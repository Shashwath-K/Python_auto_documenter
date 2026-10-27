document.addEventListener('DOMContentLoaded', () => {
    const targets = document.querySelectorAll('.page-header-row, .card, .feature-item, .pipeline-card, .tech-card, .testimonial-card, .hero-code-demo');
    targets.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(16px)';
        element.style.transition = `opacity .55s ease ${index * 45}ms, transform .7s cubic-bezier(.16,1,.3,1) ${index * 45}ms`;
    });
    requestAnimationFrame(() => targets.forEach(element => {
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }));
});
