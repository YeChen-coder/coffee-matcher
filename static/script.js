const API_BASE = "/api/v1";

const DATE_RANGE_DAYS = 7;
const TIME_CHOICES = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
    "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
];

const state = {
    currentUser: null,
    users: [],
    venues: [],
    targetSlots: [],
    receivedMatches: [],
    sentMatches: [],
    selectedDay: null,
    selectedTime: null,
    matchFilter: "all",
    pendingInviteTarget: null,
};

const dom = {};

document.addEventListener("DOMContentLoaded", () => {
    cacheDom();
    bindEvents();
    renderDayChips();
});

function cacheDom() {
    dom.status = document.getElementById("status");

    dom.authView = document.getElementById("auth-view");
    dom.appView = document.getElementById("app-view");

    dom.loginForm = document.getElementById("login-form");
    dom.loginEmail = document.getElementById("login-email");

    dom.registerForm = document.getElementById("register-form");
    dom.registerName = document.getElementById("register-name");
    dom.registerEmail = document.getElementById("register-email");
    dom.registerLocation = document.getElementById("register-location");
    dom.registerBio = document.getElementById("register-bio");

    dom.profileName = document.getElementById("profile-name");
    dom.profileEmail = document.getElementById("profile-email");
    dom.profileLocation = document.getElementById("profile-location");
    dom.logoutButton = document.getElementById("logout-button");

    dom.profileForm = document.getElementById("profile-form");
    dom.profileNameInput = document.getElementById("profile-name-input");
    dom.profileEmailInput = document.getElementById("profile-email-input");
    dom.profileLocationInput = document.getElementById("profile-location-input");
    dom.profileBioInput = document.getElementById("profile-bio-input");

    dom.availabilityDays = document.getElementById("availability-days");
    dom.availabilityTimes = document.getElementById("availability-times");
    dom.availabilityConfirm = document.getElementById("availability-confirm");
    dom.timeslotsList = document.getElementById("timeslots-list");

    dom.refreshDirectory = document.getElementById("refresh-directory");
    dom.usersList = document.getElementById("users-list");

    dom.matchesReceived = document.getElementById("matches-received");
    dom.matchesSent = document.getElementById("matches-sent");
    dom.matchFilterButtons = Array.from(document.querySelectorAll("[data-match-filter]"));

    dom.venuesList = document.getElementById("venues-list");
    dom.venueModalOpen = document.getElementById("venue-modal-open");
    dom.venueModal = document.getElementById("venue-modal");
    dom.venueClose = document.getElementById("venue-close");
    dom.venueForm = document.getElementById("venue-form");
    dom.venueName = document.getElementById("venue-name");
    dom.venueType = document.getElementById("venue-type");
    dom.venuePrice = document.getElementById("venue-price");
    dom.venueLocation = document.getElementById("venue-location");
    dom.venueDescription = document.getElementById("venue-description");

    dom.modal = document.getElementById("invite-modal");
    dom.modalClose = document.getElementById("invite-close");
    dom.inviteForm = document.getElementById("invite-form");
    dom.inviteSlot = document.getElementById("invite-slot");
    dom.inviteVenue = document.getElementById("invite-venue");
    dom.inviteMessage = document.getElementById("invite-message");
    dom.inviteMeta = document.getElementById("invite-target-meta");
    dom.inviteNoSlots = document.getElementById("invite-no-slots");
}

function bindEvents() {
    dom.loginForm.addEventListener("submit", handleLogin);
    dom.registerForm.addEventListener("submit", handleRegister);
    dom.logoutButton.addEventListener("click", handleLogout);

    dom.profileForm.addEventListener("submit", handleProfileUpdate);
    dom.refreshDirectory.addEventListener("click", bootstrapDirectory);

    dom.availabilityDays.addEventListener("click", handleDayClick);
    dom.availabilityTimes.addEventListener("click", handleTimeClick);
    dom.availabilityConfirm.addEventListener("click", handleConfirmAvailability);

    dom.inviteForm.addEventListener("submit", handleSendInvite);
    dom.modalClose.addEventListener("click", closeInviteModal);
    dom.modal.addEventListener("click", (event) => {
        if (event.target === dom.modal) {
            closeInviteModal();
        }
    });

    dom.matchFilterButtons.forEach((button) => {
        button.addEventListener("click", handleMatchFilter);
    });

    dom.venueModalOpen.addEventListener("click", openVenueModal);
    dom.venueClose.addEventListener("click", closeVenueModal);
    dom.venueModal.addEventListener("click", (event) => {
        if (event.target === dom.venueModal) {
            closeVenueModal();
        }
    });
    dom.venueForm.addEventListener("submit", handleCreateVenue);
}

async function handleLogin(event) {
    event.preventDefault();
    const email = dom.loginEmail.value.trim();
    if (!email) {
        showStatus("Enter your email to log in.", true);
        return;
    }

    try {
        const user = await request("/auth/login", {
            method: "POST",
            body: JSON.stringify({ email }),
        });
        await enterApp(user);
        dom.loginForm.reset();
        showStatus(`Welcome back, ${user.name}!`);
    } catch (error) {
        showStatus(error.message, true);
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const payload = {
        name: dom.registerName.value.trim(),
        email: dom.registerEmail.value.trim(),
        location: dom.registerLocation.value.trim() || null,
        bio: dom.registerBio.value.trim() || null,
    };

    if (!payload.name || !payload.email) {
        showStatus("Name and email are required to register.", true);
        return;
    }

    try {
        const user = await request("/users/", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        dom.registerForm.reset();
        await enterApp(user);
        showStatus(`Account created. Welcome, ${user.name}!`);
    } catch (error) {
        showStatus(error.message, true);
    }
}

async function enterApp(user) {
    state.currentUser = user;
    state.selectedTime = null;
    state.matchFilter = "all";
    toggleAppView(true);
    renderDayChips();
    await Promise.all([bootstrapDirectory(), loadVenues()]);
    await loadTimeslots();
    await loadMatches();
    renderProfile();
    renderVenues();
    updateMatchFilterButtons();
}

function handleLogout() {
    state.currentUser = null;
    state.targetSlots = [];
    state.receivedMatches = [];
    state.sentMatches = [];
    state.selectedTime = null;
    dom.usersList.innerHTML = "";
    dom.venuesList.innerHTML = "";
    dom.matchesReceived.innerHTML = "";
    dom.matchesSent.innerHTML = "";
    dom.timeslotsList.innerHTML = "";
    closeInviteModal();
    closeVenueModal();
    toggleAppView(false);
    renderDayChips();
    showStatus("Logged out.");
}

function toggleAppView(isAuthenticated) {
    dom.authView.style.display = isAuthenticated ? "none" : "grid";
    dom.appView.classList.toggle("hidden", !isAuthenticated);
}

function renderDayChips() {
    const today = new Date();
    dom.availabilityDays.innerHTML = "";

    for (let i = 0; i < DATE_RANGE_DAYS; i += 1) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        const iso = date.toISOString().slice(0, 10);
        const label = date.toLocaleDateString(undefined, {
            weekday: "short",
            month: "short",
            day: "numeric",
        });
        const button = document.createElement("button");
        button.type = "button";
        button.className = "chip";
        button.dataset.date = iso;
        button.textContent = label;
        if (state.selectedDay === iso || (i === 0 && !state.selectedDay)) {
            button.classList.add("chip--selected");
            state.selectedDay = iso;
        }
        dom.availabilityDays.appendChild(button);
    }

    renderTimeChips();
}

function handleDayClick(event) {
    const target = event.target.closest("button[data-date]");
    if (!target) {
        return;
    }
    state.selectedDay = target.dataset.date;
    state.selectedTime = null;
    dom.availabilityDays.querySelectorAll(".chip").forEach((chip) => chip.classList.remove("chip--selected"));
    target.classList.add("chip--selected");
    renderTimeChips();
    updateAvailabilityConfirm();
}

function renderTimeChips() {
    dom.availabilityTimes.innerHTML = "";
    TIME_CHOICES.forEach((time) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "chip";
        button.dataset.time = time;
        button.textContent = time;
        if (time === state.selectedTime) {
            button.classList.add("chip--selected");
        }
        dom.availabilityTimes.appendChild(button);
    });
    updateAvailabilityConfirm();
}

function handleTimeClick(event) {
    const target = event.target.closest("button[data-time]");
    if (!target || !state.currentUser) {
        return;
    }
    state.selectedTime = target.dataset.time;
    dom.availabilityTimes.querySelectorAll(".chip").forEach((chip) => chip.classList.remove("chip--selected"));
    target.classList.add("chip--selected");
    updateAvailabilityConfirm();
}

function updateAvailabilityConfirm() {
    const ready = Boolean(state.currentUser && state.selectedDay && state.selectedTime);
    dom.availabilityConfirm.disabled = !ready;
}

async function handleConfirmAvailability() {
    if (!state.currentUser || !state.selectedDay || !state.selectedTime) {
        return;
    }

    const startISO = new Date(`${state.selectedDay}T${state.selectedTime}:00`);
    const endISO = new Date(startISO.getTime() + 30 * 60 * 1000);

    if (Number.isNaN(startISO.getTime())) {
        showStatus("Unable to add availability for that time.", true);
        return;
    }

    try {
        await request("/timeslots/", {
            method: "POST",
            body: JSON.stringify({
                user_id: state.currentUser.id,
                start_time: startISO.toISOString(),
                end_time: endISO.toISOString(),
                status: "available",
            }),
        });
        showStatus(`Added availability for ${formatDateTime(startISO.toISOString())}.`);
        state.selectedTime = null;
        renderTimeChips();
        await loadTimeslots();
    } catch (error) {
        showStatus(error.message, true);
    }
}

async function bootstrapDirectory() {
    if (!state.currentUser) {
        return;
    }
    const users = await request("/users/");
    state.users = users;
    const fresh = users.find((item) => item.id === state.currentUser.id);
    if (fresh) {
        state.currentUser = fresh;
        renderProfile();
    }
    renderUsers();
}

async function loadVenues() {
    const venues = await request("/venues/");
    state.venues = venues;
    renderVenues();
}

async function loadTimeslots() {
    if (!state.currentUser) {
        return;
    }
    try {
        const slots = await request(`/timeslots/?user_id=${state.currentUser.id}`);
        renderTimeslots(slots);
    } catch (error) {
        dom.timeslotsList.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
    }
}

async function loadMatches() {
    if (!state.currentUser) {
        return;
    }
    try {
        const [received, sent] = await Promise.all([
            request(`/matches/received/${state.currentUser.id}`),
            request(`/matches/sent/${state.currentUser.id}`),
        ]);
        state.receivedMatches = received;
        state.sentMatches = sent;
        renderMatches();
    } catch (error) {
        dom.matchesReceived.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
        dom.matchesSent.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
    }
}

async function handleProfileUpdate(event) {
    event.preventDefault();
    if (!state.currentUser) {
        return;
    }

    const payload = {
        name: dom.profileNameInput.value.trim(),
        bio: dom.profileBioInput.value.trim() || null,
        location: dom.profileLocationInput.value.trim() || null,
    };

    if (!payload.name) {
        showStatus("Name is required.", true);
        return;
    }

    try {
        const updated = await request(`/users/${state.currentUser.id}`, {
            method: "PUT",
            body: JSON.stringify(payload),
        });
        state.currentUser = updated;
        await bootstrapDirectory();
        showStatus("Profile updated.");
    } catch (error) {
        showStatus(error.message, true);
    }
}

function renderProfile() {
    const user = state.currentUser;
    if (!user) {
        return;
    }

    dom.profileName.textContent = user.name;
    dom.profileEmail.textContent = user.email;
    dom.profileLocation.textContent = user.location || "Location not set";

    dom.profileNameInput.value = user.name;
    dom.profileEmailInput.value = user.email;
    dom.profileLocationInput.value = user.location || "";
    dom.profileBioInput.value = user.bio || "";
}

function renderTimeslots(slots) {
    if (!slots || slots.length === 0) {
        dom.timeslotsList.innerHTML = '<p class="empty">No availability yet. Use the buttons above to add a slot.</p>';
        return;
    }

    dom.timeslotsList.innerHTML = slots
        .map((slot) => `
            <article class="card">
                <h4>${formatDateTime(slot.start_time)}</h4>
                <p class="muted">Ends at ${formatTime(slot.end_time)} · Status: ${escapeHtml(slot.status)}</p>
            </article>
        `)
        .join("");
}

function renderUsers() {
    if (state.users.length === 0) {
        dom.usersList.innerHTML = '<p class="empty">No users yet.</p>';
        return;
    }

    dom.usersList.innerHTML = state.users
        .map((user) => renderUserCard(user))
        .join("");

    dom.usersList.querySelectorAll(".invite-btn").forEach((button) => {
        button.addEventListener("click", () => {
            const id = Number.parseInt(button.dataset.userId, 10);
            const target = state.users.find((usr) => usr.id === id);
            if (target) {
                openInviteModal(target);
            }
        });
    });
}

function renderUserCard(user) {
    const isCurrent = state.currentUser && user.id === state.currentUser.id;
    const classes = ["card", isCurrent ? "card--highlight" : ""].join(" ");
    const locationBadge = user.location ? `<span class="badge badge--location">${escapeHtml(user.location)}</span>` : "";
    const inviteButton = !isCurrent
        ? `<button type="button" class="invite-btn" data-user-id="${user.id}">Invite for coffee</button>`
        : "";
    return `
        <article class="${classes}">
            <header>
                <h3>${escapeHtml(user.name)}</h3>
                ${locationBadge}
            </header>
            <p class="muted">${escapeHtml(user.email)}</p>
            <p>${escapeHtml(user.bio || "")}</p>
            ${inviteButton}
        </article>
    `;
}

function renderVenues() {
    if (state.venues.length === 0) {
        dom.venuesList.innerHTML = '<p class="empty">No venues available.</p>';
        return;
    }

    dom.venuesList.innerHTML = state.venues
        .map((venue) => renderVenueCard(venue))
        .join("");
}

function renderVenueCard(venue) {
    const isMine = state.currentUser && venue.created_by_id === state.currentUser.id;
    const creator = state.users.find((user) => user.id === venue.created_by_id);
    const badgeLabel = isMine
        ? "Suggested by you"
        : creator
            ? `Suggested by ${escapeHtml(creator.name)}`
            : null;
    const badge = badgeLabel ? `<span class="venue-badge">${badgeLabel}</span>` : "";
    const classes = ["card", isMine ? "card--user-venue" : ""].join(" ");
    return `
        <article class="${classes}">
            <header>
                <h3>${escapeHtml(venue.name)}</h3>
                <span class="badge">${escapeHtml(venue.type)} · ${escapeHtml(venue.price_range || "")}</span>
            </header>
            <p>${escapeHtml(venue.description || "")}</p>
            <p class="muted">${escapeHtml(venue.location || "")}</p>
            ${badge}
        </article>
    `;
}

function renderMatches() {
    const received = filterMatches(state.receivedMatches);
    const sent = filterMatches(state.sentMatches);

    dom.matchesReceived.innerHTML = received.length
        ? received.map((match) => renderMatchCard(match, true)).join("")
        : '<p class="empty">No requests match this filter.</p>';

    dom.matchesSent.innerHTML = sent.length
        ? sent.map((match) => renderMatchCard(match, false)).join("")
        : '<p class="empty">No requests match this filter.</p>';

    dom.matchesReceived.querySelectorAll("[data-action]").forEach((button) => {
        button.addEventListener("click", async () => {
            const matchId = Number.parseInt(button.dataset.matchId, 10);
            const action = button.dataset.action;
            await respondToMatch(matchId, action);
        });
    });
}

function filterMatches(matches) {
    if (state.matchFilter === "all") {
        return matches;
    }
    return matches.filter((match) => (match.status || "").toLowerCase() === state.matchFilter);
}

function renderMatchCard(match, isIncoming) {
    const requester = state.users.find((user) => user.id === match.requester_id);
    const target = state.users.find((user) => user.id === match.target_id);
    const venue = state.venues.find((item) => item.id === match.venue_id);
    const normalizedStatus = (match.status || "pending").toLowerCase();
    const statusLabel = normalizedStatus.charAt(0).toUpperCase() + normalizedStatus.slice(1);
    const classes = ["card", `match-card--${normalizedStatus}`];

    const base = `
        <article class="${classes.join(" ")}">
            <header>
                <h4>${formatDateTime(match.proposed_time)}</h4>
                <span class="badge">${escapeHtml(statusLabel)}</span>
            </header>
            <p class="muted">${escapeHtml(requester?.name || "")} → ${escapeHtml(target?.name || "")}</p>
            <p>${escapeHtml(match.message || "")}</p>
            <p class="muted">Venue: ${escapeHtml(venue?.name || "Unknown")}</p>
    `;

    if (!isIncoming || normalizedStatus !== "pending") {
        return `${base}</article>`;
    }

    return `${base}
        <div class="match-actions">
            <button type="button" data-match-id="${match.id}" data-action="accept">Accept</button>
            <button type="button" data-match-id="${match.id}" data-action="reject">Reject</button>
        </div>
    </article>`;
}

async function respondToMatch(matchId, action) {
    try {
        const payload = { status: action === "accept" ? "accepted" : "rejected" };
        await request(`/matches/${matchId}`, {
            method: "PUT",
            body: JSON.stringify(payload),
        });
        showStatus(`Invitation ${action === "accept" ? "accepted" : "rejected"}.`);
        await loadMatches();
    } catch (error) {
        showStatus(error.message, true);
    }
}

function handleMatchFilter(event) {
    const value = event.currentTarget.dataset.matchFilter;
    if (!value || value === state.matchFilter) {
        return;
    }
    state.matchFilter = value;
    updateMatchFilterButtons();
    renderMatches();
}

function updateMatchFilterButtons() {
    dom.matchFilterButtons.forEach((button) => {
        button.classList.toggle("chip--selected", button.dataset.matchFilter === state.matchFilter);
    });
}

function openInviteModal(target) {
    if (!state.currentUser) {
        showStatus("Log in to send invitations.", true);
        return;
    }
    state.pendingInviteTarget = target;
    dom.inviteMeta.textContent = `${target.name} • ${target.email}${target.location ? " • " + target.location : ""}`;
    dom.inviteMessage.value = "";
    populateInviteVenues();
    loadTargetSlots(target.id);
    dom.modal.classList.remove("hidden");
}

function closeInviteModal() {
    dom.modal.classList.add("hidden");
    dom.inviteSlot.innerHTML = '<option value="">Select a time slot…</option>';
    dom.inviteNoSlots.classList.add("hidden");
    dom.inviteSlot.disabled = false;
    state.pendingInviteTarget = null;
}

function populateInviteVenues() {
    dom.inviteVenue.innerHTML = '<option value="">Select a venue…</option>';
    state.venues.forEach((venue) => {
        const option = document.createElement("option");
        option.value = String(venue.id);
        option.textContent = `${venue.name} (${venue.type}, ${venue.price_range || ""})`;
        dom.inviteVenue.appendChild(option);
    });
}

async function loadTargetSlots(userId) {
    try {
        const slots = await request(`/timeslots/?user_id=${userId}`);
        state.targetSlots = slots.filter((slot) => (slot.status || "").toLowerCase() === "available");
        if (state.targetSlots.length === 0) {
            // fall back to showing the raw slots so requester can still choose
            state.targetSlots = slots;
        }
        renderInviteSlots();
    } catch (error) {
        state.targetSlots = [];
        dom.inviteSlot.innerHTML = `<option value="">${escapeHtml(error.message)}</option>`;
        dom.inviteSlot.disabled = true;
    }
}

function renderInviteSlots() {
    dom.inviteSlot.innerHTML = '<option value="">Select a time slot…</option>';
    if (state.targetSlots.length === 0) {
        dom.inviteNoSlots.classList.remove("hidden");
        dom.inviteSlot.disabled = true;
        return;
    }
    dom.inviteNoSlots.classList.add("hidden");
    dom.inviteSlot.disabled = false;
    state.targetSlots.forEach((slot) => {
        const option = document.createElement("option");
        option.value = String(slot.id);
        option.textContent = `${formatDateTime(slot.start_time)} → ${formatTime(slot.end_time)}`;
        dom.inviteSlot.appendChild(option);
    });
}

async function handleSendInvite(event) {
    event.preventDefault();
    if (!state.currentUser || !state.pendingInviteTarget) {
        showStatus("Select someone from the directory first.", true);
        return;
    }

    const slotId = Number.parseInt(dom.inviteSlot.value, 10);
    const venueId = Number.parseInt(dom.inviteVenue.value, 10);

    if (Number.isNaN(slotId) || Number.isNaN(venueId)) {
        showStatus("Choose an availability slot and venue.", true);
        return;
    }

    const slot = state.targetSlots.find((item) => item.id === slotId);
    if (!slot) {
        showStatus("Selected slot is no longer available.", true);
        return;
    }

    const payload = {
        requester_id: state.currentUser.id,
        target_id: state.pendingInviteTarget.id,
        time_slot_id: slotId,
        proposed_time: slot.start_time,
        venue_id: venueId,
        message: dom.inviteMessage.value.trim() || "",
    };

    try {
        await request("/matches/", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        showStatus("Invitation sent.");
        closeInviteModal();
        await loadMatches();
    } catch (error) {
        showStatus(error.message, true);
    }
}

function openVenueModal() {
    if (!state.currentUser) {
        showStatus("Log in to add a venue.", true);
        return;
    }
    dom.venueForm.reset();
    dom.venueModal.classList.remove("hidden");
}

function closeVenueModal() {
    dom.venueModal.classList.add("hidden");
}

async function handleCreateVenue(event) {
    event.preventDefault();
    if (!state.currentUser) {
        showStatus("Log in to add a venue.", true);
        return;
    }

    const payload = {
        name: dom.venueName.value.trim(),
        type: dom.venueType.value,
        price_range: dom.venuePrice.value || "",
        location: dom.venueLocation.value.trim() || "",
        description: dom.venueDescription.value.trim() || "",
        created_by_id: state.currentUser.id,
    };

    if (!payload.name || !payload.type) {
        showStatus("Venue name and type are required.", true);
        return;
    }

    try {
        await request("/venues/", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        showStatus("Venue added.");
        closeVenueModal();
        await loadVenues();
    } catch (error) {
        showStatus(error.message, true);
    }
}

async function request(path, options = {}) {
    const config = { ...options };
    config.headers = {
        Accept: "application/json",
        ...(options.headers || {}),
    };
    if (config.body && !config.headers["Content-Type"]) {
        config.headers["Content-Type"] = "application/json";
    }

    const response = await fetch(`${API_BASE}${path}`, config);
    const contentType = response.headers.get("content-type") || "";
    let payload;

    if (response.status === 204) {
        payload = null;
    } else if (contentType.includes("application/json")) {
        payload = await response.json();
    } else {
        payload = await response.text();
    }

    if (!response.ok) {
        const message = payload && typeof payload === "object" && "detail" in payload
            ? payload.detail
            : typeof payload === "string"
                ? payload
                : "Request failed.";
        throw new Error(message || "Request failed.");
    }

    return payload;
}

function showStatus(message, isError = false) {
    dom.status.textContent = message;
    dom.status.classList.toggle("status--error", Boolean(isError));
    dom.status.classList.add("status--visible");
    if (!isError) {
        setTimeout(() => dom.status.classList.remove("status--visible"), 3500);
    }
}

function formatDateTime(isoString) {
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) {
        return isoString;
    }
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

function formatTime(isoString) {
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) {
        return isoString;
    }
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function escapeHtml(value) {
    return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
