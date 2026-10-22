(function () {
    const overlay = document.getElementById('loading-overlay');
    if (!overlay) return;

    let hasVisited = false;
    try {
        hasVisited = sessionStorage.getItem('semanticflow-loader-seen-v2') === '1';
    } catch (error) {
        // Continue with the loader when storage is unavailable.
    }

    if (hasVisited || document.documentElement.classList.contains('skip-loader')) {
        overlay.remove();
        return;
    }

    try { sessionStorage.setItem('semanticflow-loader-seen-v2', '1'); } catch (error) { /* no-op */ }

    const progress = document.getElementById('loading-progress');
    const percent = document.getElementById('loading-percent');
    const status = document.getElementById('loading-status');
    const mark = document.querySelector('.loading-mark');
    const statuses = ['Aligning signal', 'Warming parser', 'Opening workspace'];
    let statusIndex = 0;

    const finish = () => {
        overlay.classList.add('is-complete');
        window.setTimeout(() => overlay.remove(), 480);
    };

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !window.anime) {
        progress.style.width = '100%';
        percent.textContent = '100%';
        status.textContent = 'Ready';
        window.setTimeout(finish, 220);
        return;
    }

    anime({ targets: mark, rotate: ['45deg', '405deg'], duration: 1100, easing: 'easeInOutQuart' });
    anime({ targets: '.loading-orbit-a', rotate: ['36deg', '396deg'], duration: 900, easing: 'easeInOutSine' });
    anime({ targets: '.loading-orbit-b', rotate: ['-36deg', '-396deg'], duration: 1200, easing: 'easeInOutSine' });
    anime({
        targets: progress,
        width: ['0%', '100%'],
        duration: 1150,
        easing: 'easeInOutQuart',
        update: (animation) => {
            const value = Math.round(animation.progress);
            percent.textContent = `${String(value).padStart(2, '0')}%`;
            const nextIndex = Math.min(statuses.length - 1, Math.floor(value / 34));
            if (nextIndex !== statusIndex) {
                statusIndex = nextIndex;
                status.textContent = statuses[statusIndex];
            }
        },
        complete: () => {
            status.textContent = 'Ready';
            window.setTimeout(finish, 120);
        }
    });
})();
