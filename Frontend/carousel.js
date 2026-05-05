const stack = document.getElementById("stack");
const next = document.getElementById("next");
const prev = document.getElementById("prev");

// Next button
next.addEventListener("click", () => {
    stack.appendChild(stack.firstElementChild);
});

// Prev button
prev.addEventListener("click", () => {
    stack.insertBefore(stack.lastElementChild, stack.firstElementChild);
});

// Mouse wheel support
stack.addEventListener("wheel", (e) => {
    e.preventDefault();
    if (e.deltaY > 0) {
        stack.appendChild(stack.firstElementChild);
    } else {
        stack.insertBefore(stack.lastElementChild, stack.firstElementChild);
    }
});

// Initialize stack visibility for 5 cards
function updateStack() {
    const cards = stack.children;
    for (let i = 0; i < cards.length; i++) {
        const card = cards[i];
        if (i === 0) {
            card.style.transform = 'translateY(0px) scale(1)';
            card.style.opacity = '1';
            card.style.zIndex = '5';
        } else if (i === 1) {
            card.style.transform = 'translateY(40px) scale(0.95)';
            card.style.opacity = '0.9';
            card.style.zIndex = '4';
        } else if (i === 2) {
            card.style.transform = 'translateY(80px) scale(0.9)';
            card.style.opacity = '0.7';
            card.style.zIndex = '3';
        } else if (i === 3) {
            card.style.transform = 'translateY(120px) scale(0.85)';
            card.style.opacity = '0.5';
            card.style.zIndex = '2';
        } else if (i === 4) {
            card.style.transform = 'translateY(160px) scale(0.8)';
            card.style.opacity = '0.3';
            card.style.zIndex = '1';
        }
    }
}

updateStack();

// Update after each interaction
const observer = new MutationObserver(updateStack);
observer.observe(stack, { childList: true });
