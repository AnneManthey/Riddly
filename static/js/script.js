const doors = document.querySelectorAll(".single-door");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

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

    if (door.classList.contains("animate")) {
      return;
    }

    if (reduceMotion.matches) {
      window.location.assign(door.href);
      return;
    }

    const handleAnimationEnd = (animationEvent) => {
      if (animationEvent.animationName !== "bottomBubbles") {
        return;
      }

      door.removeEventListener("animationend", handleAnimationEnd);
      window.clearTimeout(navigationFallback);
      window.location.assign(door.href);
    };

    const navigationFallback = window.setTimeout(
      () => window.location.assign(door.href),
      2000,
    );
    door.addEventListener("animationend", handleAnimationEnd);
    door.classList.add("animate");
  });
});