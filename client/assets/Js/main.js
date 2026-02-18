(() => {
  const pageTitle = document.body.dataset.pageTitle;
  const titleNode = document.querySelector("#page-title");

  if (pageTitle && titleNode) {
    titleNode.textContent = pageTitle;
    document.title = pageTitle;
  }

  const fileName = window.location.pathname.split("/").pop() || "index.html";
  const navLinks = document.querySelectorAll(".sidebar-nav .nav-item");

  navLinks.forEach((link) => {
    const linkFile = link.getAttribute("href")?.replace("./", "");
    if (linkFile === fileName) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
})();
