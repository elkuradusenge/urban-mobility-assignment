(() => {
  const tripTableBody = document.querySelector("#trip-table-body");
  const tripCount = document.querySelector("#trip-count");
  const addTripToggle = document.querySelector("#add-trip-toggle");
  const addTripCard = document.querySelector("#add-trip-card");
  const closeAddTrip = document.querySelector("#close-add-trip");
  const addTripForm = document.querySelector("#add-trip-form");
  const editTripCard = document.querySelector("#edit-trip-card");
  const closeEditTrip = document.querySelector("#close-edit-trip");
  const cancelEditTrip = document.querySelector("#cancel-edit-trip");
  const editTripForm = document.querySelector("#edit-trip-form");
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
  let tripsCache = [];
  let currentEditingTripId = null;

  if (!tripTableBody || !tripCount) {
    return;
  }

  const openAddCard = () => {
    editTripCard?.classList.add("hidden");
    addTripCard?.classList.remove("hidden");
  };
  const closeAddCard = () => addTripCard?.classList.add("hidden");
  const openEditCard = () => {
    addTripCard?.classList.add("hidden");
    editTripCard?.classList.remove("hidden");
  };
  const closeEditCard = () => {
    editTripCard?.classList.add("hidden");
    currentEditingTripId = null;
  };

  addTripToggle?.addEventListener("click", openAddCard);
  closeAddTrip?.addEventListener("click", closeAddCard);
  closeEditTrip?.addEventListener("click", closeEditCard);
  cancelEditTrip?.addEventListener("click", closeEditCard);

  const formatCurrency = (value) => {
    const numeric = Number(value);
    if (Number.isNaN(numeric)) return "N/A";
    return `${numeric.toLocaleString()} RWF`;
  };

  const resolveEndpointBase = () => {
    if (window.location.protocol !== "file:") {
      return "";
    }
    return "http://localhost:3000";
  };

  const resolveStatus = (trip) => {
    if (typeof trip?.status === "string" && trip.status.trim()) {
      return trip.status.trim();
    }
    if (!trip?.dropoff_datetime) return "Completed";
    const dropoffTime = new Date(trip.dropoff_datetime);
    if (Number.isNaN(dropoffTime.getTime())) return "Completed";
    return dropoffTime < new Date() ? "Completed" : "Scheduled";
  };

  const getStatusClass = (status) => {
    const normalized = String(status || "").toLowerCase();
    if (normalized === "completed") return "status-pill completed";
    if (normalized === "scheduled") return "status-pill scheduled";
    if (normalized === "in progress") return "status-pill in-progress";
    if (normalized === "cancelled") return "status-pill cancelled";
    return "status-pill";
  };

  const requestTrips = async (path, options = {}) => {
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
          throw new Error(`Request failed with status ${response.status}`);
        }
        return response;
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError || new Error("Unable to reach server");
  };

  const getTrips = async () => {
    const response = await requestTrips("/trips");
    const payload = await response.json();
    if (Array.isArray(payload)) return payload;
    if (payload?.success && Array.isArray(payload.data)) return payload.data;
    if (Array.isArray(payload?.data)) return payload.data;
    throw new Error("Unexpected response format");
  };

  const getCollection = async (path) => {
    const response = await requestTrips(path);
    const payload = await response.json();
    if (Array.isArray(payload)) return payload;
    if (payload?.success && Array.isArray(payload.data)) return payload.data;
    if (Array.isArray(payload?.data)) return payload.data;
    throw new Error(`Unexpected response format for ${path}`);
  };

  const createTrip = async (tripPayload) => {
    const response = await requestTrips("/trips", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tripPayload),
    });
    const payload = await response.json();
    if (!payload?.success) {
      throw new Error(payload?.message || "Create trip failed");
    }
    return payload.data;
  };

  const deleteTrip = async (id) => {
    await requestTrips(`/trips/${id}`, { method: "DELETE" });
  };

  const updateTrip = async (id, patch) => {
    const response = await requestTrips(`/trips/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(patch),
    });
    const payload = await response.json();
    if (!payload?.success) {
      throw new Error(payload?.message || "Update failed");
    }
    return payload.data;
  };

  const renderTrips = (trips) => {
    tripCount.textContent = `${trips.length} trips total`;

    if (!trips.length) {
      tripTableBody.innerHTML = `
        <tr>
          <td colspan="6">No trips found.</td>
        </tr>
      `;
      return;
    }

    tripTableBody.innerHTML = trips
      .map((trip) => {
        const from = trip.pickup_location?.zone || `Location #${trip.pickup_location_id}`;
        const to = trip.dropoff_location?.zone || `Location #${trip.dropoff_location_id}`;
        const vendor = trip.vendor?.name || `Vendor #${trip.vendor_id}`;
        const price = formatCurrency(trip.total_amount);
        const status = resolveStatus(trip);
        const statusClass = getStatusClass(status);

        return `
          <tr>
            <td>${from}</td>
            <td>${to}</td>
            <td>${vendor}</td>
            <td>${price}</td>
            <td><span class="${statusClass}">${status}</span></td>
            <td>
              <div class="row-actions">
                <button class="icon-btn js-edit-trip" type="button" data-id="${trip.id}" aria-label="Edit trip">
                  ${editIcon}
                </button>
                <button class="icon-btn danger js-delete-trip" type="button" data-id="${trip.id}" aria-label="Delete trip">
                  ${deleteIcon}
                </button>
              </div>
            </td>
          </tr>
        `;
      })
      .join("");
  };

  const renderError = () => {
    tripCount.textContent = "0 trips total";
    tripTableBody.innerHTML = `
      <tr>
        <td colspan="6">Failed to load trips. Make sure server runs on http://localhost:3000.</td>
      </tr>
    `;
  };

  const reloadTrips = async () => {
    const trips = await getTrips();
    tripsCache = trips;
    renderTrips(tripsCache);
  };

  const formatSqlDateTime = (date) => {
    const pad = (n) => String(n).padStart(2, "0");
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(
      date.getDate(),
    )} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(
      date.getSeconds(),
    )}`;
  };

  const buildTripPayload = (formData, existingTrip = null) => {
    const pickupLocationId = Number(formData.get("from"));
    const dropoffLocationId = Number(formData.get("to"));
    const vendorId = Number(formData.get("vendor"));
    const price = Number(formData.get("price"));
    const status = String(formData.get("status") || "Scheduled");

    if (
      Number.isNaN(pickupLocationId) ||
      Number.isNaN(dropoffLocationId) ||
      Number.isNaN(vendorId) ||
      Number.isNaN(price)
    ) {
      throw new Error("Please fill in all required fields.");
    }

    const now = new Date();
    let pickupDate = new Date(now);
    let dropoffDate = new Date(now);

    if (status === "Completed") {
      pickupDate = new Date(now.getTime() - 30 * 60 * 1000);
      dropoffDate = new Date(now.getTime() - 10 * 60 * 1000);
    } else if (status === "In Progress") {
      pickupDate = new Date(now.getTime() - 5 * 60 * 1000);
      dropoffDate = new Date(now.getTime() + 10 * 60 * 1000);
    } else {
      pickupDate = new Date(now.getTime() + 5 * 60 * 1000);
      dropoffDate = new Date(now.getTime() + 25 * 60 * 1000);
    }

    const mtaTax = Number(existingTrip?.mta_tax ?? 0.5);
    const tipAmount = Number(existingTrip?.tip_amount ?? 0);
    const fareAmount = price;
    const totalAmount = fareAmount + mtaTax + tipAmount;

    return {
      vendor_id: vendorId,
      pickup_datetime: formatSqlDateTime(pickupDate),
      dropoff_datetime: formatSqlDateTime(dropoffDate),
      passenger_count: Number(existingTrip?.passenger_count ?? 1),
      trip_distance: Number(existingTrip?.trip_distance ?? 1),
      mta_tax: mtaTax,
      pickup_location_id: pickupLocationId,
      dropoff_location_id: dropoffLocationId,
      tip_amount: tipAmount,
      fare_amount: fareAmount,
      total_amount: Number(totalAmount.toFixed(2)),
    };
  };

  const fillSelect = (selectElement, items, valueKey, labelKey) => {
    if (!selectElement) return;

    const placeholder = selectElement.querySelector("option[value=\"\"]");
    const placeholderText = placeholder?.textContent || "Select option";

    selectElement.innerHTML = `<option value=\"\" selected disabled>${placeholderText}</option>`;

    items.forEach((item) => {
      const option = document.createElement("option");
      option.value = String(item[valueKey]);
      option.textContent = String(item[labelKey]);
      selectElement.appendChild(option);
    });
  };

  const loadFormOptions = async () => {
    if (!addTripForm && !editTripForm) return;

    const [vendors, locations] = await Promise.all([
      getCollection("/vendors"),
      getCollection("/locations"),
    ]);

    const fillAllFormSelects = (form) => {
      if (!form) return;
      const vendorSelect = form.querySelector("select[name='vendor']");
      const fromSelect = form.querySelector("select[name='from']");
      const toSelect = form.querySelector("select[name='to']");
      fillSelect(vendorSelect, vendors, "id", "name");
      fillSelect(fromSelect, locations, "location_id", "zone");
      fillSelect(toSelect, locations, "location_id", "zone");
    };

    fillAllFormSelects(addTripForm);
    fillAllFormSelects(editTripForm);
  };

  const prefillEditForm = (trip) => {
    if (!editTripForm) return;

    const fromSelect = editTripForm.querySelector("select[name='from']");
    const toSelect = editTripForm.querySelector("select[name='to']");
    const vendorSelect = editTripForm.querySelector("select[name='vendor']");
    const priceInput = editTripForm.querySelector("input[name='price']");
    const statusSelect = editTripForm.querySelector("select[name='status']");

    if (fromSelect) fromSelect.value = String(trip.pickup_location_id ?? "");
    if (toSelect) toSelect.value = String(trip.dropoff_location_id ?? "");
    if (vendorSelect) vendorSelect.value = String(trip.vendor_id ?? "");
    if (priceInput) {
      const formPrice = Number(trip.fare_amount ?? trip.total_amount ?? 0);
      priceInput.value = String(Number.isNaN(formPrice) ? 0 : formPrice);
    }
    if (statusSelect) statusSelect.value = resolveStatus(trip);
  };

  addTripForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
      const formData = new FormData(addTripForm);
      const payload = buildTripPayload(formData);
      await createTrip(payload);
      addTripForm.reset();
      closeAddCard();
      await reloadTrips();
    } catch (error) {
      console.error("Failed to create trip:", error);
      window.alert(error.message || "Failed to create trip.");
    }
  });

  editTripForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (currentEditingTripId == null) {
      window.alert("No trip selected for edit.");
      return;
    }

    const currentTrip = tripsCache.find((trip) => trip.id === currentEditingTripId);
    if (!currentTrip) {
      window.alert("Trip not found.");
      return;
    }

    try {
      const formData = new FormData(editTripForm);
      const payload = buildTripPayload(formData, currentTrip);
      await updateTrip(currentEditingTripId, payload);
      closeEditCard();
      await reloadTrips();
    } catch (error) {
      console.error("Failed to update trip:", error);
      window.alert(error.message || "Failed to update trip.");
    }
  });

  tripTableBody.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;

    const deleteButton = target.closest(".js-delete-trip");
    if (deleteButton) {
      const id = Number(deleteButton.dataset.id);
      if (Number.isNaN(id)) return;

      const confirmed = window.confirm("Delete this trip?");
      if (!confirmed) return;

      try {
        await deleteTrip(id);
        tripsCache = tripsCache.filter((trip) => trip.id !== id);
        renderTrips(tripsCache);
      } catch (error) {
        console.error("Failed to delete trip:", error);
        window.alert("Failed to delete trip.");
      }
      return;
    }

    const editButton = target.closest(".js-edit-trip");
    if (editButton) {
      const id = Number(editButton.dataset.id);
      if (Number.isNaN(id)) return;

      const currentTrip = tripsCache.find((trip) => trip.id === id);
      if (!currentTrip) {
        window.alert("Trip not found in view.");
        return;
      }

      currentEditingTripId = id;
      prefillEditForm(currentTrip);
      openEditCard();
    }
  });

  const init = async () => {
    try {
      await loadFormOptions();
      await reloadTrips();
    } catch (error) {
      console.error("Failed to fetch trips:", error);
      renderError();
    }
  };

  init();
})();
