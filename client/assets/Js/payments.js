(() => {
  const filterButtons = document.querySelectorAll(".filter-btn");
  const rows = document.querySelectorAll("#payment-table-body tr");

  if (!filterButtons.length || !rows.length) {
    return;
  }

  const applyFilter = (filter) => {
    rows.forEach((row) => {
      const rowStatus = row.dataset.status || "";
      const showRow = filter === "all" || rowStatus === filter;
      row.classList.toggle("hidden", !showRow);
    });
  };

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      filterButtons.forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      applyFilter(button.dataset.filter || "all");
    });
  });
})();
