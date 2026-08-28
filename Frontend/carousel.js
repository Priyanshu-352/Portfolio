// Horizontal projects carousel
const track = document.getElementById("projects-track");
const prev = document.querySelector(".projects-carousel .carousel-arrow.prev");
const next = document.querySelector(".projects-carousel .carousel-arrow.next");

if (track && prev && next) {
    let index = 0;

    function cardWidth() {
        // Each card: media + body. Compute from first child or default.
        const first = track.querySelector(".project-card");
        const margin = 24; // matches gap
        return first ? first.getBoundingClientRect().width + margin : 380;
    }

    function maxIndex() {
        const n = track.querySelectorAll(".project-card").length;
        const visible = Math.max(1, Math.floor(track.clientWidth / cardWidth()));
        return Math.max(0, n - visible);
    }

    function update() {
        const max = maxIndex();
        if (index > max) index = max;
        if (index < 0) index = 0;
        track.style.transform = `translateX(${-index * cardWidth()}px)`;
    }

    function nextSlide() {
        index = Math.min(index + 1, maxIndex());
        update();
    }

    function prevSlide() {
        index = Math.max(index - 1, 0);
        update();
    }

    next.addEventListener("click", nextSlide);
    prev.addEventListener("click", prevSlide);

    // Keyboard arrows
    document.addEventListener("keydown", (e) => {
        if (e.key === "ArrowRight") nextSlide();
        if (e.key === "ArrowLeft") prevSlide();
    });

    // Touch / drag
    let startX = 0;
    let dragging = false;
    track.addEventListener("touchstart", (e) => {
        startX = e.touches[0].clientX;
        dragging = true;
    });
    track.addEventListener("touchend", (e) => {
        if (!dragging) return;
        dragging = false;
        const dx = e.changedTouches[0].clientX - startX;
        if (dx < -40) nextSlide();
        else if (dx > 40) prevSlide();
    });

    // Recompute on resize
    let resizeTimer;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(update, 150);
    });

    update();
}
