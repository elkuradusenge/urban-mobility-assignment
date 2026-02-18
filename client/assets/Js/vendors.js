(() => {
  const addVendorToggle = document.querySelector("#add-vendor-toggle");
  const addVendorCard = document.querySelector("#add-vendor-card");
  const closeAddVendor = document.querySelector("#close-add-vendor");
  const addVendorForm = document.querySelector("#add-vendor-form");
  const vendorsGrid = document.querySelector("#vendors-grid");
  const vendorCount = document.querySelector("#vendor-count");

  if (
    !addVendorToggle ||
    !addVendorCard ||
    !closeAddVendor ||
    !addVendorForm ||
    !vendorsGrid ||
    !vendorCount
  ) {
    return;
  }

  const updateVendorCount = () => {
    vendorCount.textContent = `${vendorsGrid.children.length} vendors total`;
  };

  const openCard = () => addVendorCard.classList.remove("hidden");
  const closeCard = () => addVendorCard.classList.add("hidden");

  addVendorToggle.addEventListener("click", openCard);
  closeAddVendor.addEventListener("click", closeCard);

  addVendorForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(addVendorForm);

    const name = String(formData.get("name") || "").trim();
    const email = String(formData.get("email") || "").trim();
    const phone = String(formData.get("phone") || "").trim();
    const ratingValue = Number(formData.get("rating"));

    if (!name || !email || !phone || Number.isNaN(ratingValue)) {
      return;
    }

    const safeRating = Math.min(5, Math.max(1, ratingValue)).toFixed(1);

    const card = document.createElement("article");
    card.className = "vendor-card";
    card.innerHTML = `
      <div class="vendor-top">
        <h3>${name}</h3>
        <div class="card-actions">
          <button class="action-btn" type="button">Edit</button>
          <button class="action-btn danger js-delete-vendor" type="button">Delete</button>
        </div>
      </div>
      <p>${email}</p>
      <p>${phone}</p>
      <div class="vendor-bottom">
        <span class="rating">* ${safeRating}</span>
        <span class="trips-count">0 trips</span>
      </div>
    `;

    vendorsGrid.appendChild(card);
    addVendorForm.reset();
    closeCard();
    updateVendorCount();
  });

  vendorsGrid.addEventListener("click", (event) => {
    const target = event.target;

    if (!(target instanceof HTMLElement)) {
      return;
    }

    const deleteButton = target.closest(".js-delete-vendor");
    if (!deleteButton) {
      return;
    }

    const card = deleteButton.closest(".vendor-card");
    if (card) {
      card.remove();
      updateVendorCount();
    }
  });

  updateVendorCount();
})();
