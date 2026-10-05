let toastTimer;

function showToast(title, message, type = "normal", duration = 3000) {
    const toast = document.getElementById("toast-component");
    if (!toast) return;

    const toastType = ["success", "error"].includes(type) ? type : "normal";
    toast.classList.remove("toast-success", "toast-error", "toast-normal");
    toast.classList.add(`toast-${toastType}`);
    document.getElementById("toast-title").textContent = title;
    document.getElementById("toast-message").textContent = message;
    clearTimeout(toastTimer);

    if (!toast.matches(":popover-open")) {
        toast.showPopover();
        void toast.offsetHeight;
    }
    toast.classList.replace("toast-hidden", "toast-show");
    toastTimer = setTimeout(() => {
        toast.classList.replace("toast-show", "toast-hidden");
        toastTimer = setTimeout(() => toast.hidePopover(), 300);
    }, duration);
}
