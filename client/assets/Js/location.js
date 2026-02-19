(() => {
  const addLocationToggle = document.querySelector("#add-location-toggle");
  const addLocationCard = document.querySelector("#add-location-card");
  const closeAddLocation = document.querySelector("#close-add-location");
  const addLocationForm = document.querySelector("#add-location-form");
  const editLocationCard = document.querySelector("#edit-location-card");
  const closeEditLocation = document.querySelector("#close-edit-location");
  const cancelEditLocation = document.querySelector("#cancel-edit-location");
  const editLocationForm = document.querySelector("#edit-location-form");
  const locationsGrid = document.querySelector("#locations-grid");
  const locationCount = document.querySelector("#location-count");

  const editIcon = `
    <svg class="edit-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M4 20l4.5-1 10-10a1.8 1.8 0 0 0 0-2.5l-1-1a1.8 1.8 0 0 0-2.5 0l-10 10L4 20z"></path>
      <path d="M13.5 6.5l4 4"></path>
    </svg>
  `;

  const deleteIcon = `
    <svg class="trash-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M4 7h16"></path>
      <path d="M9 7V4h6v3"></path>
      <path d="M7 7v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V7"></path>
      <path d="M10 11v6"></path>
      <path d="M14 11v6"></path>
    </svg>
  `;

  let locationsCache = [];
  let currentEditingLocationId = null;

  if (
    !addLocationToggle ||
    !addLocationCard ||
    !closeAddLocation ||
    !addLocationForm ||
    !editLocationCard ||
    !closeEditLocation ||
    !cancelEditLocation ||
    !editLocationForm ||
    !locationsGrid ||
    !locationCount
  ) {
    return;
  }

  const updateLocationCount = () => {
    locationCount.textContent = `${locationsCache.length} locations`;
  };

  const resolveEndpointBase = () => {
    if (window.location.protocol !== "file:") return "";
    return "http://localhost:3000";
  };

  const requestLocations = async (path, options = {}) => {
    const endpoints = [];
    const primary = `${resolveEndpointBase()}${path}`;
    endpoints.push(primary);
    if (primary !== `http://localhost:3000${path}`) {
      endpoints.push(`http://localhost:3000${path}`);
    }

    let lastError;
    for (const url of endpoints) {
      try {
        const response = await fetch(url, options);
        if (!response.ok) {
          let errorMessage = `Request failed with status ${response.status}`;
          try {
            const payload = await response.json();
            if (payload?.message) errorMessage = payload.message;
          } catch (_) {
            // Ignore JSON parse errors on failed response.
          }
          throw new Error(errorMessage);
        }
        return response;
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError || new Error("Unable to reach server");
  };

  const parseDataArray = (payload) => {
    if (Array.isArray(payload)) return payload;
    if (payload?.success && Array.isArray(payload.data)) return payload.data;
    if (Array.isArray(payload?.data)) return payload.data;
    throw new Error("Unexpected response format");
  };

  const getLocations = async () => {
    const response = await requestLocations("/locations");
    const payload = await response.json();
    return parseDataArray(payload);
  };

  const createLocation = async (payload) => {
    const response = await requestLocations("/locations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!result?.success) throw new Error(result?.message || "Create failed");
  };

  const updateLocation = async (id, payload) => {
    const response = await requestLocations(`/locations/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!result?.success) throw new Error(result?.message || "Update failed");
  };

  const deleteLocation = async (id) => {
    const response = await requestLocations(`/locations/${id}`, { method: "DELETE" });
    const result = await response.json();
    if (!result?.success) throw new Error(result?.message || "Delete failed");
  };

  const toApiPayload = (name, region) => ({
    zone: name,
    borough: region,
    service_zone: region,
  });

  const renderError = () => {
    locationsGrid.innerHTML = `
      <article class="location-card location-card--message">
        <p>Failed to load locations. Make sure server runs on http://localhost:3000.</p>
      </article>
    `;
    locationsCache = [];
    updateLocationCount();
  };

  const renderLocations = () => {
    if (!locationsCache.length) {
      locationsGrid.innerHTML = `
        <article class="location-card location-card--message">
          <p>No locations found.</p>
        </article>
      `;
      return;
    }

    locationsGrid.innerHTML = locationsCache
      .map(
        (location) => `
        <article class="location-card" data-id="${location.location_id}">
          <div class="location-left">
            <div class="location-icon">L</div>
            <div>
              <h3>${location.zone}</h3>
              <p>${location.borough}</p>
            </div>
          </div>
          <div class="card-actions">
            <button class="action-btn js-edit-location" type="button" data-id="${location.location_id}" aria-label="Edit location">
              ${editIcon}
            </button>
            <button class="action-btn danger js-delete-location" type="button" data-id="${location.location_id}" aria-label="Delete location">
              ${deleteIcon}
            </button>
          </div>
        </article>
      `,
      )
      .join("");
  };

  const reloadLocations = async () => {
    locationsCache = await getLocations();
    renderLocations();
    updateLocationCount();
  };

  const openAddCard = () => {
    editLocationCard.classList.add("hidden");
    addLocationCard.classList.remove("hidden");
  };
  const closeAddCard = () => addLocationCard.classList.add("hidden");
  const openEditCard = () => {
    addLocationCard.classList.add("hidden");
    editLocationCard.classList.remove("hidden");
  };
  const closeEditCard = () => {
    editLocationCard.classList.add("hidden");
    currentEditingLocationId = null;
  };

  addLocationToggle.addEventListener("click", openAddCard);
  closeAddLocation.addEventListener("click", closeAddCard);
  closeEditLocation.addEventListener("click", closeEditCard);
  cancelEditLocation.addEventListener("click", closeEditCard);

  addLocationForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(addLocationForm);

    const name = String(formData.get("name") || "").trim();
    const region = String(formData.get("region") || "").trim();
    if (!name || !region) return;

    try {
      await createLocation(toApiPayload(name, region));
      addLocationForm.reset();
      closeAddCard();
      await reloadLocations();
    } catch (error) {
      console.error("Failed to create location:", error);
      window.alert(error.message || "Failed to create location.");
    }
  });

  const prefillEditForm = (location) => {
    const nameInput = editLocationForm.querySelector("input[name='name']");
    const regionInput = editLocationForm.querySelector("input[name='region']");
    if (nameInput) nameInput.value = location.zone || "";
    if (regionInput) regionInput.value = location.borough || "";
  };

  editLocationForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (currentEditingLocationId == null) {
      window.alert("No location selected for edit.");
      return;
    }

    const formData = new FormData(editLocationForm);
    const name = String(formData.get("name") || "").trim();
    const region = String(formData.get("region") || "").trim();
    if (!name || !region) {
      window.alert("Please fill in all required fields.");
      return;
    }

    try {
      await updateLocation(currentEditingLocationId, toApiPayload(name, region));
      closeEditCard();
      await reloadLocations();
    } catch (error) {
      console.error("Failed to update location:", error);
      window.alert(error.message || "Failed to update location.");
    }
  });

  locationsGrid.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;

    const deleteButton = target.closest(".js-delete-location");
    if (deleteButton) {
      const id = Number(deleteButton.dataset.id);
      if (Number.isNaN(id)) return;

      const confirmed = window.confirm("Delete this location?");
      if (!confirmed) return;

      deleteLocation(id)
        .then(() => reloadLocations())
        .catch((error) => {
          console.error("Failed to delete location:", error);
          window.alert(error.message || "Failed to delete location.");
        });
      return;
    }

    const editButton = target.closest(".js-edit-location");
    if (editButton) {
      const id = Number(editButton.dataset.id);
      if (Number.isNaN(id)) return;

      const location = locationsCache.find((item) => Number(item.location_id) === id);
      if (!location) {
        window.alert("Location not found.");
        return;
      }

      currentEditingLocationId = id;
      prefillEditForm(location);
      openEditCard();
    }
  });

  const init = async () => {
    try {
      await reloadLocations();
    } catch (error) {
      console.error("Failed to fetch locations:", error);
      renderError();
    }
  };

  init();
})();
