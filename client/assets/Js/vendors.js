(() => {
  const addVendorToggle = document.querySelector("#add-vendor-toggle");
  const addVendorCard = document.querySelector("#add-vendor-card");
  const closeAddVendor = document.querySelector("#close-add-vendor");
  const addVendorForm = document.querySelector("#add-vendor-form");
  const editVendorCard = document.querySelector("#edit-vendor-card");
  const closeEditVendor = document.querySelector("#close-edit-vendor");
  const cancelEditVendor = document.querySelector("#cancel-edit-vendor");
  const editVendorForm = document.querySelector("#edit-vendor-form");
  const vendorsGrid = document.querySelector("#vendors-grid");
  const vendorCount = document.querySelector("#vendor-count");

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

  let vendorsCache = [];
  let currentEditingVendorId = null;

  if (
    !addVendorToggle ||
    !addVendorCard ||
    !closeAddVendor ||
    !addVendorForm ||
    !editVendorCard ||
    !closeEditVendor ||
    !cancelEditVendor ||
    !editVendorForm ||
    !vendorsGrid ||
    !vendorCount
  ) {
    return;
  }

  const updateVendorCount = () => {
    vendorCount.textContent = `${vendorsCache.length} vendors total`;
  };

  const resolveEndpointBase = () => {
    if (window.location.protocol !== "file:") {
      return "";
    }
    return "http://localhost:3000";
  };

  const requestVendors = async (path, options = {}) => {
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
            const errorPayload = await response.json();
            if (errorPayload?.message) {
              errorMessage = errorPayload.message;
            }
          } catch (_) {
            // Keep default message when response body is not JSON.
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

  const getVendors = async () => {
    const response = await requestVendors("/vendors");
    const payload = await response.json();

    if (Array.isArray(payload)) return payload;
    if (payload?.success && Array.isArray(payload.data)) return payload.data;
    if (Array.isArray(payload?.data)) return payload.data;

    throw new Error("Unexpected vendors response format");
  };

  const createVendor = async (vendorPayload) => {
    const response = await requestVendors("/vendors", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(vendorPayload),
    });
    const payload = await response.json();

    if (!payload?.success) {
      throw new Error(payload?.message || "Create vendor failed");
    }

    return payload.data;
  };

  const deleteVendor = async (id) => {
    const response = await requestVendors(`/vendors/${id}`, {
      method: "DELETE",
    });
    const payload = await response.json();
    if (!payload?.success) {
      throw new Error(payload?.message || "Delete vendor failed");
    }
  };

  const updateVendor = async (id, vendorPayload) => {
    const response = await requestVendors(`/vendors/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(vendorPayload),
    });
    const payload = await response.json();
    if (!payload?.success) {
      throw new Error(payload?.message || "Update vendor failed");
    }
    return payload.data;
  };

  const renderError = () => {
    vendorsGrid.innerHTML = `
      <article class="vendor-card vendor-card--message">
        <p>Failed to load vendors. Make sure server runs on http://localhost:3000.</p>
      </article>
    `;
    vendorsCache = [];
    updateVendorCount();
  };

  const renderVendors = (vendors) => {
    if (!vendors.length) {
      vendorsGrid.innerHTML = `
        <article class="vendor-card vendor-card--message">
          <p>No vendors found.</p>
        </article>
      `;
      return;
    }

    vendorsGrid.innerHTML = vendors
      .map(
        (vendor) => `
        <article class="vendor-card" data-id="${vendor.id}">
          <div class="vendor-top">
            <h3>${vendor.name}</h3>
            <div class="card-actions">
              <button class="action-btn js-edit-vendor" type="button" data-id="${vendor.id}" aria-label="Edit vendor">
                ${editIcon}
              </button>
              <button class="action-btn danger js-delete-vendor" type="button" data-id="${vendor.id}" aria-label="Delete vendor">
                ${deleteIcon}
              </button>
            </div>
          </div>
          <p>${vendor.email}</p>
          <p>${vendor.phone_number}</p>
          <div class="vendor-bottom">
            <span class="vendor-id">Vendor #${vendor.id}</span>
            <span class="trips-count">0 trips</span>
          </div>
        </article>
      `,
      )
      .join("");
  };

  const loadVendors = async () => {
    const vendors = await getVendors();
    vendorsCache = vendors;
    renderVendors(vendorsCache);
    updateVendorCount();
  };

  const openAddCard = () => {
    editVendorCard.classList.add("hidden");
    addVendorCard.classList.remove("hidden");
  };
  const closeAddCard = () => addVendorCard.classList.add("hidden");
  const openEditCard = () => {
    addVendorCard.classList.add("hidden");
    editVendorCard.classList.remove("hidden");
  };
  const closeEditCard = () => {
    editVendorCard.classList.add("hidden");
    currentEditingVendorId = null;
  };

  addVendorToggle.addEventListener("click", openAddCard);
  closeAddVendor.addEventListener("click", closeAddCard);
  closeEditVendor.addEventListener("click", closeEditCard);
  cancelEditVendor.addEventListener("click", closeEditCard);

  addVendorForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(addVendorForm);

    const name = String(formData.get("name") || "").trim();
    const email = String(formData.get("email") || "").trim();
    const phone = String(formData.get("phone") || "").trim();

    if (!name || !email || !phone) {
      return;
    }

    try {
      await createVendor({
        name,
        email,
        phone_number: phone,
      });
      addVendorForm.reset();
      closeAddCard();
      await loadVendors();
    } catch (error) {
      console.error("Failed to create vendor:", error);
      window.alert(error.message || "Failed to create vendor.");
    }
  });

  const prefillEditVendorForm = (vendor) => {
    const nameInput = editVendorForm.querySelector("input[name='name']");
    const emailInput = editVendorForm.querySelector("input[name='email']");
    const phoneInput = editVendorForm.querySelector("input[name='phone']");

    if (nameInput) nameInput.value = vendor.name || "";
    if (emailInput) emailInput.value = vendor.email || "";
    if (phoneInput) phoneInput.value = vendor.phone_number || "";
  };

  editVendorForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (currentEditingVendorId == null) {
      window.alert("No vendor selected for edit.");
      return;
    }

    const formData = new FormData(editVendorForm);
    const name = String(formData.get("name") || "").trim();
    const email = String(formData.get("email") || "").trim();
    const phone = String(formData.get("phone") || "").trim();

    if (!name || !email || !phone) {
      window.alert("Please fill in all required fields.");
      return;
    }

    try {
      await updateVendor(currentEditingVendorId, {
        name,
        email,
        phone_number: phone,
      });
      closeEditCard();
      await loadVendors();
    } catch (error) {
      console.error("Failed to update vendor:", error);
      window.alert(error.message || "Failed to update vendor.");
    }
  });

  vendorsGrid.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;

    const deleteButton = target.closest(".js-delete-vendor");
    if (deleteButton) {
      const id = Number(deleteButton.dataset.id);
      if (Number.isNaN(id)) return;

      const confirmed = window.confirm("Delete this vendor?");
      if (!confirmed) return;

      deleteVendor(id)
        .then(() => loadVendors())
        .catch((error) => {
          console.error("Failed to delete vendor:", error);
          window.alert(error.message || "Failed to delete vendor.");
        });
      return;
    }

    const editButton = target.closest(".js-edit-vendor");
    if (editButton) {
      const id = Number(editButton.dataset.id);
      if (Number.isNaN(id)) return;

      const vendor = vendorsCache.find((item) => Number(item.id) === id);
      if (!vendor) {
        window.alert("Vendor not found.");
        return;
      }

      currentEditingVendorId = id;
      prefillEditVendorForm(vendor);
      openEditCard();
    }
  });

  const init = async () => {
    try {
      await loadVendors();
    } catch (error) {
      console.error("Failed to fetch vendors:", error);
      renderError();
    }
  };

  init();
})();
