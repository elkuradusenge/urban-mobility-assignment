(() => {
  const addLocationToggle = document.querySelector("#add-location-toggle");
  const addLocationCard = document.querySelector("#add-location-card");
  const closeAddLocation = document.querySelector("#close-add-location");
  const addLocationForm = document.querySelector("#add-location-form");
  const locationsGrid = document.querySelector("#locations-grid");
  const locationCount = document.querySelector("#location-count");

  if (
    !addLocationToggle ||
    !addLocationCard ||
    !closeAddLocation ||
    !addLocationForm ||
    !locationsGrid ||
    !locationCount
  ) {
    return;
  }

  const updateLocationCount = () => {
    locationCount.textContent = `${locationsGrid.children.length} locations`;
  };

  const openCard = () => addLocationCard.classList.remove("hidden");
  const closeCard = () => addLocationCard.classList.add("hidden");

  addLocationToggle.addEventListener("click", openCard);
  closeAddLocation.addEventListener("click", closeCard);

  addLocationForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(addLocationForm);

    const name = String(formData.get("name") || "").trim();
    const region = String(formData.get("region") || "").trim();

    if (!name || !region) {
      return;
    }

    const card = document.createElement("article");
    card.className = "location-card";
    card.innerHTML = `
      <div class="location-left">
        <div class="location-icon">L</div>
        <div>
          <h3>${name}</h3>
          <p>${region}</p>
        </div>
      </div>
      <button class="action-btn danger js-delete-location" type="button">Delete</button>
    `;

    locationsGrid.appendChild(card);
    addLocationForm.reset();
    closeCard();
    updateLocationCount();
  });

  locationsGrid.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }

    const deleteButton = target.closest(".js-delete-location");
    if (!deleteButton) {
      return;
    }

    const card = deleteButton.closest(".location-card");
    if (card) {
      card.remove();
      updateLocationCount();
    }
  });

  updateLocationCount();
})();
