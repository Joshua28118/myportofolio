(() => {
    const grid = document.getElementById("grid");
    const searchForm = document.getElementById("experience-search-form");
    const searchInput = document.getElementById("experience-search");
    const experienceForm = document.getElementById("experience-form");
    const editForm = document.getElementById("experience-edit-form");
    const editModal = document.getElementById("edit-experience-modal");
    const template = document.getElementById("experience-card-template");
    const placeholderId = "00000000-0000-0000-0000-000000000000";
    const listEndpoint = grid.dataset.endpoint;
    const detailEndpoint = grid.dataset.detailEndpoint;
    const starEndpoint = grid.dataset.starEndpoint;
    const editableFields = ["title", "description", "category", "thumbnail", "ended_at"];
    let experiencesAbortController;
    let searchDebounceTimer;
    let editingId = null;

    function endpointFor(pattern, id) {
        return pattern.replace(placeholderId, encodeURIComponent(id));
    }

    function displayPageSection(section) {
        for (const id of ["loading", "error", "empty", "grid"]) {
            document.getElementById(id).classList.toggle("hide", id !== section);
        }
        grid.setAttribute("aria-busy", String(section === "loading"));
    }

    function buildExperienceCardElement(experience) {
        const card = template.content.firstElementChild.cloneNode(true);
        card.dataset.id = experience.id;
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

        for (const link of card.querySelectorAll("a[data-href]")) {
            link.href = endpointFor(link.dataset.href, experience.id);
        }

        const starButton = card.querySelector(".button-star");
        const count = card.querySelector(".star-count");
        count.textContent = starButton ? experience.star_count : `${experience.star_count} star`;
        if (starButton) {
            starButton.classList.toggle("is-starred", experience.is_starred);
            starButton.setAttribute("aria-pressed", String(experience.is_starred));
            card.querySelector(".star-label").textContent = experience.is_starred ? "Unstar" : "Star";
        }

        const editButton = card.querySelector(".experience-edit");
        if (editButton) {
            editButton.dataset.experience = JSON.stringify(
                Object.fromEntries(editableFields.map(name => [name, experience[name]])),
            );
        }

        const deleteModal = card.querySelector(".experience-delete-modal");
        if (deleteModal) {
            deleteModal.id = `delete-experience-${experience.id}`;
            const heading = deleteModal.querySelector("h2");
            heading.id = `delete-experience-title-${experience.id}`;
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
        const url = new URL(listEndpoint, window.location.origin);
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

    function apiErrorMessage(data, status) {
        if (typeof data === "string") return data;
        const messages = Object.values(data ?? {})
            .flat()
            .filter(value => typeof value === "string");
        return messages.join(" ") || `Permintaan gagal (status ${status}).`;
    }

    async function callApi(url, method, payload) {
        const response = await fetch(url, {
            method,
            headers: {
                Accept: "application/json",
                ...(payload === undefined ? {} : { "Content-Type": "application/json" }),
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: payload === undefined ? undefined : JSON.stringify(payload),
        });
        if (response.status === 204) return null;
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(apiErrorMessage(data, response.status));
        return data;
    }

    function readFormPayload(form) {
        const fields = new FormData(form);
        const payload = {};
        for (const name of editableFields) {
            const value = (fields.get(name) ?? "").toString().trim();
            if (name === "ended_at" || name === "thumbnail") {
                payload[name] = value === "" ? null : value;
            } else {
                payload[name] = value;
            }
        }
        return payload;
    }

    async function submitExperienceForm(event, { url, method, modalId, successMessage, errorTitle }) {
        event.preventDefault();
        const form = event.currentTarget;
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton.disabled) return;
        submitButton.disabled = true;
        try {
            await callApi(url, method, readFormPayload(form));
            document.getElementById(modalId).hidePopover();
            if (method === "POST") form.reset();
            showToast("Berhasil", successMessage, "success");
            searchExperiences();
        } catch (error) {
            showToast(errorTitle, error.message, "error");
        } finally {
            submitButton.disabled = false;
        }
    }

    function openEditModal(button) {
        const card = button.closest("[data-id]");
        editingId = card.dataset.id;
        const values = JSON.parse(button.dataset.experience);
        for (const name of editableFields) {
            const field = editForm.elements[name];
            if (!field) continue;
            if (name === "ended_at" && values[name]) {
                field.value = values[name].slice(0, 16);
            } else {
                field.value = values[name] ?? "";
            }
        }
        editModal.showPopover();
    }

    async function deleteExperience(form) {
        const card = form.closest("[data-id]");
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton.disabled) return;
        submitButton.disabled = true;
        try {
            await callApi(endpointFor(detailEndpoint, card.dataset.id), "DELETE");
            card.querySelector(".experience-delete-modal")?.hidePopover();
            showToast("Berhasil", "Experience berhasil dihapus.", "success");
            searchExperiences();
        } catch (error) {
            showToast("Gagal menghapus Experience", error.message, "error");
        } finally {
            submitButton.disabled = false;
        }
    }

    async function toggleStar(form) {
        const card = form.closest("[data-id]");
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton.disabled) return;
        submitButton.disabled = true;
        try {
            await callApi(endpointFor(starEndpoint, card.dataset.id), "POST");
            searchExperiences();
        } catch (error) {
            showToast("Gagal memperbarui star", error.message, "error");
        } finally {
            submitButton.disabled = false;
        }
    }

    grid.addEventListener("submit", event => {
        const form = event.target;
        if (form.classList.contains("star-form")) {
            event.preventDefault();
            toggleStar(form);
        } else if (form.classList.contains("experience-delete")) {
            event.preventDefault();
            deleteExperience(form);
        }
    });

    grid.addEventListener("click", event => {
        const button = event.target.closest(".experience-edit");
        if (button) openEditModal(button);
    });

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

    experienceForm?.addEventListener("submit", event => submitExperienceForm(event, {
        url: listEndpoint,
        method: "POST",
        modalId: "add-experience-modal",
        successMessage: "Experience berhasil ditambahkan.",
        errorTitle: "Gagal menambahkan Experience",
    }));
    editForm?.addEventListener("submit", event => submitExperienceForm(event, {
        url: endpointFor(detailEndpoint, editingId),
        method: "PATCH",
        modalId: "edit-experience-modal",
        successMessage: "Experience berhasil diperbarui.",
        errorTitle: "Gagal memperbarui Experience",
    }));
    document.getElementById("add-experience-modal")?.addEventListener("toggle", event => {
        if (event.newState === "open") experienceForm.elements.title.focus();
    });
    editModal?.addEventListener("toggle", event => {
        if (event.newState === "open") editForm.elements.title.focus();
    });
    searchExperiences();
})();
