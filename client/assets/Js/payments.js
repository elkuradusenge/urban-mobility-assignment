(() => {
  const paymentTableBody = document.querySelector("#payment-table-body");
  const paymentCount = document.querySelector("#payment-count");
  const addPaymentToggle = document.querySelector("#add-payment-toggle");
  const addPaymentCard = document.querySelector("#add-payment-card");
  const closeAddPayment = document.querySelector("#close-add-payment");
  const addPaymentForm = document.querySelector("#add-payment-form");
  const editPaymentCard = document.querySelector("#edit-payment-card");
  const closeEditPayment = document.querySelector("#close-edit-payment");
  const cancelEditPayment = document.querySelector("#cancel-edit-payment");
  const editPaymentForm = document.querySelector("#edit-payment-form");

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

  let paymentsCache = [];
  let currentEditingPaymentId = null;

  const searchPayment = document.querySelector("#search-payment");
  const sortPaymentsSelect = document.querySelector("#sort-payments");
  const resetPaymentFilters = document.querySelector("#reset-payment-filters");

  const filters = {
    search: "",
    sort: "name-asc"
  };

  if (
    !paymentTableBody ||
    !paymentCount ||
    !addPaymentToggle ||
    !addPaymentCard ||
    !closeAddPayment ||
    !addPaymentForm ||
    !editPaymentCard ||
    !closeEditPayment ||
    !cancelEditPayment ||
    !editPaymentForm ||
    !searchPayment ||
    !sortPaymentsSelect ||
    !resetPaymentFilters
  ) {
    return;
  }

  const resolveEndpointBase = () => {
    if (window.location.protocol !== "file:") return "";
    return "http://localhost:3000";
  };

  const requestPayments = async (path, options = {}) => {
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
            // Keep default error message.
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

  const getPayments = async () => {
    const response = await requestPayments("/payments");
    const payload = await response.json();
    return parseDataArray(payload);
  };

  const createPayment = async (payment) => {
    const response = await requestPayments("/payments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payment),
    });
    const payload = await response.json();
    if (!payload?.success) throw new Error(payload?.message || "Create failed");
  };

  const updatePayment = async (id, payment) => {
    const response = await requestPayments(`/payments/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payment),
    });
    const payload = await response.json();
    if (!payload?.success) throw new Error(payload?.message || "Update failed");
  };

  const deletePayment = async (id) => {
    const response = await requestPayments(`/payments/${id}`, { method: "DELETE" });
    const payload = await response.json();
    if (!payload?.success) throw new Error(payload?.message || "Delete failed");
  };

  const renderError = () => {
    paymentTableBody.innerHTML = `
      <tr>
        <td colspan="3">Failed to load payment methods. Make sure server runs on http://localhost:3000.</td>
      </tr>
    `;
    paymentCount.textContent = "0 payment methods total";
  };

  const matchesFilters = (payment) => {
    const searchTerm = filters.search.toLowerCase().trim();
    if (searchTerm && !payment.name.toLowerCase().includes(searchTerm)) {
      return false;
    }
    return true;
  };

  const sortPaymentsArray = (payments) => {
    const sorted = [...payments];
    const sortBy = filters.sort;

    if (sortBy === "name-asc") {
      sorted.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortBy === "name-desc") {
      sorted.sort((a, b) => b.name.localeCompare(a.name));
    } else if (sortBy === "id-asc") {
      sorted.sort((a, b) => a.id - b.id);
    } else if (sortBy === "id-desc") {
      sorted.sort((a, b) => b.id - a.id);
    }

    return sorted;
  };

  const applyFiltersAndSort = () => {
    const filtered = paymentsCache.filter(matchesFilters);
    const sorted = sortPaymentsArray(filtered);
    renderPayments(sorted);
  };

  const renderPayments = (payments) => {
    paymentCount.textContent = `${paymentsCache.length} payment methods total`;

    if (!payments.length) {
      paymentTableBody.innerHTML = `
        <tr>
          <td colspan="3">No payment methods found.</td>
        </tr>
      `;
      return;
    }

    paymentTableBody.innerHTML = payments
      .map(
        (payment) => `
          <tr>
            <td>#${payment.id}</td>
            <td>${payment.name}</td>
            <td>
              <div class="row-actions">
                <button class="icon-btn js-edit-payment" type="button" data-id="${payment.id}" aria-label="Edit payment">
                  ${editIcon}
                </button>
                <button class="icon-btn danger js-delete-payment" type="button" data-id="${payment.id}" aria-label="Delete payment">
                  ${deleteIcon}
                </button>
              </div>
            </td>
          </tr>
        `,
      )
      .join("");
  };

  const reloadPayments = async () => {
    paymentsCache = await getPayments();
    applyFiltersAndSort();
  };

  const openAddCard = () => {
    editPaymentCard.classList.add("hidden");
    addPaymentCard.classList.remove("hidden");
  };
  const closeAddCard = () => addPaymentCard.classList.add("hidden");
  const openEditCard = () => {
    addPaymentCard.classList.add("hidden");
    editPaymentCard.classList.remove("hidden");
  };
  const closeEditCard = () => {
    editPaymentCard.classList.add("hidden");
    currentEditingPaymentId = null;
  };

  addPaymentToggle.addEventListener("click", openAddCard);
  closeAddPayment.addEventListener("click", closeAddCard);
  closeEditPayment.addEventListener("click", closeEditCard);
  cancelEditPayment.addEventListener("click", closeEditCard);

  addPaymentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(addPaymentForm);
    const name = String(formData.get("name") || "").trim();
    if (!name) return;

    try {
      await createPayment({ name });
      addPaymentForm.reset();
      closeAddCard();
      await reloadPayments();
    } catch (error) {
      console.error("Failed to create payment:", error);
      window.alert(error.message || "Failed to create payment");
    }
  });

  editPaymentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (currentEditingPaymentId == null) {
      window.alert("No payment selected for edit.");
      return;
    }

    const formData = new FormData(editPaymentForm);
    const name = String(formData.get("name") || "").trim();
    if (!name) return;

    try {
      await updatePayment(currentEditingPaymentId, { name });
      closeEditCard();
      await reloadPayments();
    } catch (error) {
      console.error("Failed to update payment:", error);
      window.alert(error.message || "Failed to update payment");
    }
  });

  paymentTableBody.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;

    const deleteButton = target.closest(".js-delete-payment");
    if (deleteButton) {
      const id = Number(deleteButton.dataset.id);
      if (Number.isNaN(id)) return;

      const confirmed = window.confirm("Delete this payment method?");
      if (!confirmed) return;

      deletePayment(id)
        .then(() => reloadPayments())
        .catch((error) => {
          console.error("Failed to delete payment:", error);
          window.alert(error.message || "Failed to delete payment");
        });
      return;
    }

    const editButton = target.closest(".js-edit-payment");
    if (editButton) {
      const id = Number(editButton.dataset.id);
      if (Number.isNaN(id)) return;

      const payment = paymentsCache.find((item) => Number(item.id) === id);
      if (!payment) {
        window.alert("Payment not found.");
        return;
      }

      currentEditingPaymentId = id;
      const editNameInput = editPaymentForm.querySelector("input[name='name']");
      if (editNameInput) editNameInput.value = payment.name || "";
      openEditCard();
    }
  });

  searchPayment.addEventListener("input", () => {
    filters.search = searchPayment.value;
    applyFiltersAndSort();
  });

  sortPaymentsSelect.addEventListener("change", () => {
    filters.sort = sortPaymentsSelect.value;
    applyFiltersAndSort();
  });

  resetPaymentFilters.addEventListener("click", () => {
    filters.search = "";
    filters.sort = "name-asc";
    searchPayment.value = "";
    sortPaymentsSelect.value = "name-asc";
    applyFiltersAndSort();
  });

  const init = async () => {
    try {
      await reloadPayments();
    } catch (error) {
      console.error("Failed to fetch payments:", error);
      renderError();
    }
  };

  init();
})();
