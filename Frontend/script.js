function toggle() {
    const menu = document.getElementById("menu");
    menu.style.display = menu.style.display === "flex" ? "none" : "flex";
}

const texts = document.querySelectorAll('.text');
let lastScrollY = window.scrollY;
let hasReachedBottom = false;

window.addEventListener('scroll', () => {
    const currentScrollY = window.scrollY;
    const scrollingDown = currentScrollY > lastScrollY;
    const scrollingUp = currentScrollY < lastScrollY;

    // Check if reached bottom once
    if (window.scrollY + window.innerHeight >= document.body.scrollHeight - 1) {
        hasReachedBottom = true;
    }

    texts.forEach(el => {
        const rect = el.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom > 0;

        if (hasReachedBottom || (scrollingDown && isVisible)) {
            el.classList.add('visible');
        } else if (!hasReachedBottom && scrollingUp) {
            el.classList.remove('visible');
        }
    });

    lastScrollY = currentScrollY;
});

// Chatbot functions
function toggleGlobalChat() {
    const chat = document.getElementById('global-chat');
    chat.classList.toggle('active');
}

function toggleProjectChat(projectId) {
    const chat = document.getElementById('chat-' + projectId);
    chat.classList.toggle('active');
}

