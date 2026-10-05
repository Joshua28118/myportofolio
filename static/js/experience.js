(() => {
    const grid = document.getElementById("grid");
    const searchForm = document.getElementById("experience-search-form");
    const searchInput = document.getElementById("experience-search");
    const experienceForm = document.getElementById("experience-form");
    const template = document.getElementById("experience-card-template");
    const placeholderId = "00000000-0000-0000-0000-000000000000";
    let experiencesAbortController;
    let searchDebounceTimer;

    function displayPageSection(section) {
        for (const id of ["loading", "error", "empty", "grid"]) {
            document.getElementById(id).classList.toggle("hide", id !== section);
        }
        grid.setAttribute("aria-busy", String(section === "loading"));
    }

    function buildExperienceCardElement(item) {
        const experience = item.fields;
        const card = template.content.firstElementChild.cloneNode(true);
        card.querySelector("h2").textContent = experience.title;
        card.querySelector(".feature-category").textContent = experience.category_display;
        card.querySelector(".feature-description").textContent = experience.description;

        card.querySelector(".feature-status").textContent = experience.is_ongoing ? "Ongoing" : "Completed";
        const thumbnail = card.querySelector(".experience-thumbnail");
        try {
            const url = new URL(experience.thumbnail);
            if (!["http:", "https:"].includes(url.protocol)) {
                throw new Error("Invalid thumbnail URL");
            }
            thumbnail.src = url.href;
            thumbnail.alt = experience.title;
            thumbnail.addEventListener("error", () => thumbnail.remove(), { once: true });
        } catch {
            thumbnail.remove();
        }

        for (const form of card.querySelectorAll("form[data-action]")) {
            form.action = form.dataset.action.replace(placeholderId, encodeURIComponent(item.pk));
        }
        for (const link of card.querySelectorAll("a[data-href]")) {
            link.href = link.dataset.href.replace(placeholderId, encodeURIComponent(item.pk));
        }
        const starButton = card.querySelector(".button-star");
        const count = card.querySelector(".star-count");
        count.textContent = starButton ? experience.star_count : `${experience.star_count} star`;
        if (starButton) {
            starButton.classList.toggle("is-starred", experience.is_starred);
            starButton.setAttribute("aria-pressed", String(experience.is_starred));
            card.querySelector(".star-label").textContent = experience.is_starred ? "Unstar" : "Star";
        }
        const deleteModal = card.querySelector(".experience-delete-modal");
        if (deleteModal) {
            deleteModal.id = `delete-experience-${item.pk}`;
            const heading = deleteModal.querySelector("h2");
            heading.id = `delete-experience-title-${item.pk}`;
            deleteModal.setAttribute("aria-labelledby", heading.id);
            card.querySelector(".experience-delete-title").textContent = experience.title;
            for (const button of card.querySelectorAll(".experience-delete-button, .experience-delete-cancel")) {
                button.setAttribute("popovertarget", deleteModal.id);
            }
        }
        return card;
    }

    async function fetchExperiences(searchQuery = "") {
        experiencesAbortController?.abort();
        const controller = new AbortController();
        experiencesAbortController = controller;
        displayPageSection("loading");
        const url = new URL(grid.dataset.endpoint, window.location.origin);
        if (searchQuery) url.searchParams.set("title", searchQuery);
        try {
            const response = await fetch(url, {
                headers: { Accept: "application/json" },
                signal: controller.signal,
            });
            if (!response.ok) throw new Error("Failed to load experiences");
            const experiences = await response.json();
            if (controller.signal.aborted) return;
            grid.replaceChildren(...experiences.map(buildExperienceCardElement));
            document.getElementById("empty").textContent = searchQuery
                ? `Tidak ada Experience dengan judul "${searchQuery}".`
                : "No experience has been added yet.";
            displayPageSection(experiences.length ? "grid" : "empty");
        } catch (error) {
            if (error.name !== "AbortError" && !controller.signal.aborted) {
                displayPageSection("error");
                showToast("Gagal memuat Experience", "Tidak dapat mengambil data. Silakan coba lagi.", "error");
            }
        }
    }

    function searchExperiences() {
        clearTimeout(searchDebounceTimer);
        fetchExperiences(searchInput.value.trim());
    }

    function getCookie(name) {
        const cookie = document.cookie.split(";").find(value => value.trim().startsWith(`${name}=`));
        return cookie ? decodeURIComponent(cookie.trim().slice(name.length + 1)) : "";
    }

    async function addExperience(event) {
        event.preventDefault();
        const submitButton = experienceForm.querySelector('button[type="submit"]');
        if (submitButton.disabled) return;
        submitButton.disabled = true;
        try {
            const response = await fetch(experienceForm.dataset.ajaxUrl, {
                method: "POST",
                headers: { "X-CSRFToken": getCookie("csrftoken") },
                body: new FormData(experienceForm),
            });
            const result = await response.json().catch(() => ({}));
            if (response.ok) {
                experienceForm.reset();
                document.getElementById("add-experience-modal").hidePopover();
                showToast("Berhasil", "Experience berhasil ditambahkan.", "success");
                searchExperiences();
            } else {
                const errors = result.errors
                    ? Object.values(result.errors).flat().map(error => error.message)
                    : [result.message || `Permintaan gagal (status ${response.status}).`];
                showToast("Gagal menambahkan Experience", errors.join(" "), "error");
            }
        } catch {
            showToast("Gagal menambahkan Experience", "Tidak dapat menghubungi server. Silakan coba lagi.", "error");
        } finally {
            submitButton.disabled = false;
        }
    }

    searchInput.addEventListener("input", () => {
        clearTimeout(searchDebounceTimer);
        experiencesAbortController?.abort();
        searchDebounceTimer = setTimeout(searchExperiences, 300);
    });
    searchForm.addEventListener("submit", event => {
        event.preventDefault();
        searchExperiences();
    });
    searchForm.addEventListener("reset", event => {
        event.preventDefault();
        searchInput.value = "";
        searchExperiences();
    });
    document.getElementById("retry-experiences").addEventListener("click", searchExperiences);
    experienceForm?.addEventListener("submit", addExperience);
    document.getElementById("add-experience-modal")?.addEventListener("toggle", event => {
        if (event.newState === "open") experienceForm.elements.title.focus();
    });
    searchExperiences();
})();
