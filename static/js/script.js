const doors = document.querySelectorAll("a.single-door[href]");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const activeDoorAnimations = new Map();

const resetDoorAnimation = (door) => {
  const cleanup = activeDoorAnimations.get(door);
  if (cleanup) {
    cleanup();
  } else {
    door.classList.remove("animate");
  }
};

const resetAllDoorAnimations = () => doors.forEach(resetDoorAnimation);

window.addEventListener("pageshow", resetAllDoorAnimations);
window.addEventListener("pagehide", resetAllDoorAnimations);

const redirectMessage = document.querySelector("[data-redirect-url]");
if (redirectMessage) {
  window.setTimeout(
    () => window.location.assign(redirectMessage.dataset.redirectUrl),
    Number(redirectMessage.dataset.redirectDelay) || 2000,
  );
}

doors.forEach((door) => {
  door.addEventListener("click", (event) => {
    if (
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) {
      return;
    }

    event.preventDefault();

    if (activeDoorAnimations.has(door)) {
      return;
    }

    resetDoorAnimation(door);

    if (reduceMotion.matches) {
      window.location.assign(door.href);
      return;
    }

    let navigationFallback;
    const cleanup = () => {
      window.clearTimeout(navigationFallback);
      door.removeEventListener("animationend", handleAnimationEnd);
      door.classList.remove("animate");
      activeDoorAnimations.delete(door);
    };

    const handleAnimationEnd = (animationEvent) => {
      if (animationEvent.animationName !== "bottomBubbles") {
        return;
      }

      cleanup();
      window.location.assign(door.href);
    };

    activeDoorAnimations.set(door, cleanup);
    door.addEventListener("animationend", handleAnimationEnd);
    navigationFallback = window.setTimeout(
      () => {
        cleanup();
        window.location.assign(door.href);
      },
      2000,
    );
    door.classList.add("animate");
  });
});

const hintDialog = document.getElementById("hint-dialog");
const hintTrigger = document.querySelector("[data-hint-trigger]");
const hintsElement = document.getElementById("riddle-hints");

if (hintDialog && hintTrigger && hintsElement) {
  const hints = JSON.parse(hintsElement.textContent);
  const hintText = document.getElementById("hint-text");
  const hintCounter = document.getElementById("hint-counter");
  const nextHintButton = document.getElementById("next-hint");
  const closeHintButton = hintDialog.querySelector("[data-hint-close]");
  let currentHintIndex = 0;

  const updateHint = () => {
    hintText.textContent = hints[currentHintIndex];
    hintCounter.textContent = `Hinweis ${currentHintIndex + 1} von ${hints.length}`;
    if (nextHintButton) {
      nextHintButton.hidden = currentHintIndex === hints.length - 1;
    }
  };

  hintTrigger.addEventListener("click", () => {
    updateHint();
    if (typeof hintDialog.showModal === "function") {
      hintDialog.showModal();
    } else {
      hintDialog.setAttribute("open", "");
      hintDialog.classList.add("hint-dialog-fallback");
      closeHintButton.focus();
    }
  });

  if (nextHintButton) {
    nextHintButton.addEventListener("click", () => {
      if (currentHintIndex < hints.length - 1) {
        currentHintIndex += 1;
        updateHint();
      }
    });
  }

  const closeHintDialog = () => {
    if (typeof hintDialog.close === "function") {
      hintDialog.close();
    } else {
      hintDialog.removeAttribute("open");
      hintDialog.classList.remove("hint-dialog-fallback");
      hintTrigger.focus();
    }
  };

  closeHintButton.addEventListener("click", closeHintDialog);
  hintDialog.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape" &&
      typeof hintDialog.showModal !== "function"
    ) {
      event.preventDefault();
      closeHintDialog();
    }
  });
}