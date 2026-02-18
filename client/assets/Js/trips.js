(() => {
  const addTripToggle = document.querySelector("#add-trip-toggle");
  const addTripCard = document.querySelector("#add-trip-card");
  const closeAddTrip = document.querySelector("#close-add-trip");
  const addTripForm = document.querySelector("#add-trip-form");
  const tripTableBody = document.querySelector("#trip-table-body");
  const tripCount = document.querySelector("#trip-count");

  if (
    !addTripToggle ||
    !addTripCard ||
    !closeAddTrip ||
    !addTripForm ||
    !tripTableBody ||
    !tripCount
  ) {
    return;
  }

  const statusClassMap = {
    Completed: "completed",
    Scheduled: "scheduled",
    "In Progress": "progress",
    Cancelled: "cancelled"
  };

  const formatPrice = (value) => `${Number(value).toLocaleString("en-US")} RWF`;

  const updateTripCount = () => {
    tripCount.textContent = `${tripTableBody.rows.length} trips total`;
  };

  const openCard = () => addTripCard.classList.remove("hidden");
  const closeCard = () => addTripCard.classList.add("hidden");

  addTripToggle.addEventListener("click", openCard);
  closeAddTrip.addEventListener("click", closeCard);

  addTripForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(addTripForm);

    const from = String(formData.get("from") || "").trim();
    const to = String(formData.get("to") || "").trim();
    const vendor = String(formData.get("vendor") || "").trim();
    const price = String(formData.get("price") || "").trim();
    const status = String(formData.get("status") || "").trim();

    if (!from || !to || !vendor || !price || !status) {
      return;
    }

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${from}</td>
      <td>${to}</td>
      <td>${vendor}</td>
      <td>${formatPrice(price)}</td>
      <td><span class="status ${statusClassMap[status] || "scheduled"}">${status}</span></td>
      <td class="row-actions">
        <button class="icon-btn" type="button">Edit</button>
        <button class="icon-btn danger js-delete-trip" type="button">Delete</button>
      </td>
    `;

    tripTableBody.appendChild(row);
    addTripForm.reset();
    closeCard();
    updateTripCount();
  });

  tripTableBody.addEventListener("click", (event) => {
    const target = event.target;

    if (!(target instanceof HTMLElement)) {
      return;
    }

    const deleteButton = target.closest(".js-delete-trip");
    if (!deleteButton) {
      return;
    }

    const row = deleteButton.closest("tr");
    if (row) {
      row.remove();
      updateTripCount();
    }
  });

  updateTripCount();
})();
