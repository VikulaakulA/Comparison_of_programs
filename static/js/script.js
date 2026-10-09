const searchInput = document.getElementById('search-input');
  const dropdown = document.getElementById('dropdown');

  function filterDropdown() {
    const filter = searchInput.value.toLowerCase();
    const items = dropdown.getElementsByClassName('dropdown-item');
    let anyVisible = false;

    for (let i = 0; i < items.length; i++) {
      const text = items[i].textContent.toLowerCase();
      if (text.includes(filter)) {
        items[i].style.display = "block";
        anyVisible = true;
      } else {
        items[i].style.display = "none";
      }
    }

    dropdown.style.display = anyVisible ? "block" : "none";
  }

  function showDropdown() {
    dropdown.style.display = "block";
  }

  document.addEventListener("click", function(e) {
    if (!e.target.closest(".search-block")) {
      dropdown.style.display = "none";
    }
  });

  Array.from(document.getElementsByClassName('dropdown-item')).forEach(item => {
    item.addEventListener('click', () => {
      searchInput.value = item.textContent;
      dropdown.style.display = "none";
    });
  });