(() => {
    const grid = document.getElementById("grid");
    const searchForm = document.getElementById("project-search-form");
    const searchInput = document.getElementById("project-search");
    const projectForm = document.getElementById("project-form");
    const template = document.getElementById("project-card-template");
    const placeholderId = "00000000-0000-0000-0000-000000000000";
    let projectsAbortController;
    let searchDebounceTimer;

    function displayPageSection(section) {
        for (const id of ["loading", "error", "empty", "grid"]) {
            document.getElementById(id).classList.toggle("hide", id !== section);
        }
        grid.setAttribute("aria-busy", String(section === "loading"));
    }

    function buildProjectCardElement(item) {
        const project = item.fields;
        const card = template.content.firstElementChild.cloneNode(true);
        card.querySelector("h2").textContent = project.title;
        card.querySelector(".feature-category").textContent = project.tech_stack;
        card.querySelector(".feature-description").textContent = project.description;

        const link = card.querySelector(".project-link");
        try {
            const url = new URL(project.project_url);
            if (!["http:", "https:", "ftp:", "ftps:"].includes(url.protocol)) {
                throw new Error("Invalid project URL");
            }
            link.href = url.href;
        } catch {
            link.remove();
        }

        for (const form of card.querySelectorAll("form[data-action]")) {
            form.action = form.dataset.action.replace(placeholderId, encodeURIComponent(item.pk));
        }
        const editLink = card.querySelector(".project-edit");
        if (editLink) {
            editLink.href = editLink.dataset.href.replace(placeholderId, encodeURIComponent(item.pk));
        }
        const starButton = card.querySelector(".button-star");
        const count = card.querySelector(".star-count");
        count.textContent = starButton ? project.star_count : `${project.star_count} star`;
        if (starButton) {
            starButton.classList.toggle("is-starred", project.is_starred);
            starButton.setAttribute("aria-pressed", String(project.is_starred));
            card.querySelector(".star-label").textContent = project.is_starred ? "Unstar" : "Star";
        }
        const deleteForm = card.querySelector(".project-delete");
        if (deleteForm) {
            deleteForm.addEventListener("submit", event => {
                if (!window.confirm(`Hapus proyek "${project.title}"?`)) event.preventDefault();
            });
        }
        return card;
    }

    async function fetchProjects(searchQuery = "") {
        projectsAbortController?.abort();
        const controller = new AbortController();
        projectsAbortController = controller;
        displayPageSection("loading");
        const url = new URL(grid.dataset.endpoint, window.location.origin);
        if (searchQuery) url.searchParams.set("title", searchQuery);
        try {
            const response = await fetch(url, {
                headers: { Accept: "application/json" },
                signal: controller.signal,
            });
            if (!response.ok) throw new Error("Failed to load projects");
            const projects = await response.json();
            if (controller.signal.aborted) return;
            grid.replaceChildren(...projects.map(buildProjectCardElement));
            document.getElementById("empty").textContent = searchQuery
                ? `Tidak ada proyek dengan nama "${searchQuery}".`
                : "Belum ada proyek yang ditambahkan.";
            displayPageSection(projects.length ? "grid" : "empty");
        } catch (error) {
            if (error.name !== "AbortError" && !controller.signal.aborted) {
                displayPageSection("error");
            }
        }
    }

    function searchProjects() {
        clearTimeout(searchDebounceTimer);
        fetchProjects(searchInput.value.trim());
    }

    function getCookie(name) {
        const cookie = document.cookie.split(";").find(value => value.trim().startsWith(`${name}=`));
        return cookie ? decodeURIComponent(cookie.trim().slice(name.length + 1)) : "";
    }

    async function addProject(event) {
        event.preventDefault();
        const submitButton = projectForm.querySelector('button[type="submit"]');
        if (submitButton.disabled) return;
        submitButton.disabled = true;
        try {
            const response = await fetch(projectForm.dataset.ajaxUrl, {
                method: "POST",
                headers: { "X-CSRFToken": getCookie("csrftoken") },
                body: new FormData(projectForm),
            });
            const result = await response.json().catch(() => ({}));
            if (response.ok) {
                projectForm.reset();
                document.getElementById("add-project-modal").hidePopover();
                showToast("Berhasil", "Proyek berhasil ditambahkan.", "success");
                searchProjects();
            } else {
                const errors = result.errors
                    ? Object.values(result.errors).flat().map(error => error.message)
                    : [result.message || `Permintaan gagal (status ${response.status}).`];
                showToast("Gagal menambahkan proyek", errors.join(" "), "error");
            }
        } catch {
            showToast("Gagal menambahkan proyek", "Tidak dapat menghubungi server. Silakan coba lagi.", "error");
        } finally {
            submitButton.disabled = false;
        }
    }

    searchInput.addEventListener("input", () => {
        clearTimeout(searchDebounceTimer);
        projectsAbortController?.abort();
        searchDebounceTimer = setTimeout(searchProjects, 300);
    });
    searchForm.addEventListener("submit", event => {
        event.preventDefault();
        searchProjects();
    });
    searchForm.addEventListener("reset", event => {
        event.preventDefault();
        searchInput.value = "";
        searchProjects();
    });
    document.getElementById("retry-projects").addEventListener("click", searchProjects);
    projectForm?.addEventListener("submit", addProject);
    searchProjects();
})();
