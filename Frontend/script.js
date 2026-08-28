// ---- Scroll reveal ----
const revealEls = document.querySelectorAll('.reveal');

if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                io.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });
    revealEls.forEach(el => io.observe(el));
} else {
    revealEls.forEach(el => el.classList.add('visible'));
}

// ---- Seamless marquee loop (duplicate the track content) ----
const track = document.getElementById('marquee-track');
if (track) {
    track.innerHTML += track.innerHTML; // duplicates items so translateX(-50%) loops seamlessly
}

