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