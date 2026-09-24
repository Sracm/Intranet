/* ==========================================================================
   PORTAL INTRANET MQ PROFESSIONAL - INTERACTION & UI ENGINE
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Notifications Popover Toggle
  const notifBtn = document.getElementById("header-notif-btn");
  const notifFlyout = document.getElementById("notifications-popover");
  if (notifBtn && notifFlyout) {
    notifBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      closeAllPopovers(notifFlyout);
      notifFlyout.classList.toggle("open");
    });
  }

  // 2. Profile Menu Popover Toggle
  const profileTrigger = document.getElementById("header-user-trigger");
  const profileFlyout = document.getElementById("profile-menu-popover");
  if (profileTrigger && profileFlyout) {
    profileTrigger.addEventListener("click", function (e) {
      e.stopPropagation();
      closeAllPopovers(profileFlyout);
      profileFlyout.classList.toggle("open");
      profileTrigger.classList.toggle("open");
    });
  }

  // 3. Close popovers on click outside
  document.addEventListener("click", function (e) {
    closeAllPopovers();
    // Close mobile drawer on click outside
    const sidebar = document.querySelector(".app-sidebar");
    const mobileDrawerBtn = document.getElementById("mobile-drawer-toggle");
    if (sidebar && sidebar.classList.contains("mobile-open")) {
      if (!sidebar.contains(e.target) && mobileDrawerBtn && !mobileDrawerBtn.contains(e.target)) {
        sidebar.classList.remove("mobile-open");
      }
    }
  });

  function closeAllPopovers(except = null) {
    if (notifFlyout && except !== notifFlyout) notifFlyout.classList.remove("open");
    if (profileFlyout && except !== profileFlyout) profileFlyout.classList.remove("open");
    if (profileTrigger && except !== profileFlyout) profileTrigger.classList.remove("open");
  }

  // 4. Sidebar Collapse Toggle (Desktop) & Mobile Drawer Toggle
  const sidebarToggle = document.getElementById("sidebar-toggle-btn");
  const sidebar = document.querySelector(".app-sidebar");
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", function () {
      if (window.innerWidth <= 768) {
        sidebar.classList.toggle("mobile-open");
      } else {
        sidebar.classList.toggle("collapsed");
      }
    });
  }

  const mobileDrawerBtn = document.getElementById("mobile-drawer-toggle");
  if (mobileDrawerBtn && sidebar) {
    mobileDrawerBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      sidebar.classList.toggle("mobile-open");
    });
  }

  // 5. Expandable Sidebar Categories (e.g. Regionais, Marketing)
  document.querySelectorAll(".nav-category-header").forEach(function (header) {
    header.addEventListener("click", function (e) {
      const parent = header.closest(".nav-category-group");
      if (parent) {
        parent.classList.toggle("expanded");
        const submenu = parent.querySelector(".sidebar-submenu");
        const arrow = header.querySelector(".accordion-arrow");
        const isExp = parent.classList.contains("expanded");
        if (submenu) {
          submenu.style.display = isExp ? "flex" : "none";
        }
        if (arrow) {
          arrow.style.transform = isExp ? "rotate(180deg)" : "rotate(0deg)";
        }
      }
    });
  });

  // 6. Mini Calendar Engine (Home Page)
  initMiniCalendar();

  // 7. Global Search Filter on Home
  const homeSearch = document.getElementById("home-global-search");
  if (homeSearch) {
    homeSearch.addEventListener("input", function (e) {
      const q = e.target.value.toLowerCase().trim();
      document.querySelectorAll(".report-card, .ferramenta-card").forEach(function (card) {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(q) ? "" : "none";
      });
    });
  }

  // 8. Inicializa Engine de Avisos com persistência de lidos
  initAvisosEngine();
});

/* ==========================================================================
   ENGINE DE AVISOS (MARCAR COMO LIDO, OCULTAR E HISTÓRICO)
   ========================================================================== */

const STORAGE_KEY_AVISOS = "mq_intranet_read_avisos_v1";

function getReadAvisos() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY_AVISOS) || "[]");
  } catch (e) {
    return [];
  }
}

function saveReadAvisos(list) {
  try {
    localStorage.setItem(STORAGE_KEY_AVISOS, JSON.stringify(list));
  } catch (e) {}
}

function initAvisosEngine() {
  const readList = getReadAvisos();
  const allCards = document.querySelectorAll("#avisos-active-container .aviso-featured-card");
  if (allCards.length === 0) return;

  let unreadCount = 0;
  allCards.forEach(card => {
    const id = card.getAttribute("data-aviso-id");
    if (readList.includes(id)) {
      card.style.display = "none";
    } else {
      card.style.display = "block";
      unreadCount++;
    }
  });

  updateAvisosUI(unreadCount, readList);
}

function markAvisoRead(avisoId) {
  const card = document.getElementById(avisoId);
  if (!card) return;

  const readList = getReadAvisos();
  if (!readList.includes(avisoId)) {
    readList.push(avisoId);
    saveReadAvisos(readList);
  }

  card.style.transition = "opacity 0.25s ease, transform 0.25s ease";
  card.style.opacity = "0";
  card.style.transform = "translateY(-6px)";

  setTimeout(() => {
    card.style.display = "none";
    card.style.opacity = "1";
    card.style.transform = "none";

    const allCards = document.querySelectorAll("#avisos-active-container .aviso-featured-card");
    let unreadCount = 0;
    allCards.forEach(c => {
      const cid = c.getAttribute("data-aviso-id");
      if (!readList.includes(cid)) unreadCount++;
    });

    updateAvisosUI(unreadCount, readList);
    showToast("Aviso marcado como lido e arquivado.");
  }, 250);
}

function markAllAvisosRead() {
  const allCards = document.querySelectorAll("#avisos-active-container .aviso-featured-card");
  if (allCards.length === 0) return;

  const readList = getReadAvisos();
  allCards.forEach(card => {
    const id = card.getAttribute("data-aviso-id");
    if (id && !readList.includes(id)) {
      readList.push(id);
    }
    card.style.display = "none";
  });

  saveReadAvisos(readList);
  updateAvisosUI(0, readList);
  showToast("Todos os avisos foram marcados como lidos.");
}

function toggleAvisosHistorico() {
  const drawer = document.getElementById("avisos-historico-drawer");
  if (!drawer) return;
  const isHidden = drawer.style.display === "none" || !drawer.style.display;
  drawer.style.display = isHidden ? "block" : "none";
}

function restoreAviso(avisoId) {
  let readList = getReadAvisos();
  readList = readList.filter(id => id !== avisoId);
  saveReadAvisos(readList);

  const card = document.getElementById(avisoId);
  if (card) {
    card.style.display = "block";
    card.style.opacity = "0";
    setTimeout(() => {
      card.style.transition = "opacity 0.25s ease";
      card.style.opacity = "1";
    }, 10);
  }

  const allCards = document.querySelectorAll("#avisos-active-container .aviso-featured-card");
  let unreadCount = 0;
  allCards.forEach(c => {
    const cid = c.getAttribute("data-aviso-id");
    if (!readList.includes(cid)) unreadCount++;
  });

  updateAvisosUI(unreadCount, readList);
  showToast("Aviso restaurado para o painel principal.");
}

function restoreAllAvisos() {
  saveReadAvisos([]);
  const allCards = document.querySelectorAll("#avisos-active-container .aviso-featured-card");
  allCards.forEach(card => {
    card.style.display = "block";
  });
  updateAvisosUI(allCards.length, []);
  showToast("Todos os avisos foram restaurados.");
}

function updateAvisosUI(unreadCount, readList) {
  const badge = document.getElementById("active-avisos-count");
  if (badge) {
    if (unreadCount === 0) {
      badge.textContent = "Nenhum aviso pendente";
      badge.style.background = "rgba(34, 197, 94, 0.15)";
      badge.style.color = "#22c55e";
    } else {
      badge.textContent = `${unreadCount} ${unreadCount === 1 ? 'aviso não lido' : 'avisos não lidos'}`;
      badge.style.background = "rgba(239, 68, 68, 0.15)";
      badge.style.color = "#f87171";
    }
  }

  const emptyState = document.getElementById("avisos-empty-state");
  if (emptyState) {
    emptyState.style.display = unreadCount === 0 ? "block" : "none";
  }

  const histBadge = document.getElementById("historico-avisos-count");
  if (histBadge) {
    histBadge.textContent = readList.length;
  }

  // Preenche a lista do histórico
  const histContainer = document.getElementById("avisos-historico-items-list");
  if (histContainer) {
    if (readList.length === 0) {
      histContainer.innerHTML = '<span style="font-size: 11.5px; color: #64748b; font-style: italic;">Nenhum aviso arquivado no histórico.</span>';
    } else {
      histContainer.innerHTML = readList.map(id => {
        const el = document.getElementById(id);
        const title = el ? (el.getAttribute("data-title") || "Aviso Corporativo") : id;
        return `
          <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 12px;">
            <span style="font-size: 11.5px; color: #cbd5e1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 75%;">${title}</span>
            <button onclick="restoreAviso('${id}')" style="background: rgba(203, 151, 39, 0.12); border: 1px solid rgba(203, 151, 39, 0.3); color: var(--brand-secondary-dourado, #CB9727); border-radius: 4px; padding: 3px 8px; font-size: 10.5px; cursor: pointer; font-weight: 600;">Restaurar</button>
          </div>
        `;
      }).join("");
    }
  }
}

/* ==========================================================================
   FILTRO DE DASHBOARDS DO HUB SETORIAL
   ========================================================================== */

function filterSectorHubCards(term) {
  const q = term.toLowerCase().trim();
  const cards = document.querySelectorAll("#sector-cards-grid .hub-report-card");
  cards.forEach(card => {
    const title = card.getAttribute("data-title") || "";
    const desc = card.getAttribute("data-desc") || "";
    if (title.includes(q) || desc.includes(q)) {
      card.style.display = "flex";
    } else {
      card.style.display = "none";
    }
  });
}

/* ==========================================================================
   MINI CALENDAR ENGINE (HOME PAGE)
   ========================================================================== */

function initMiniCalendar() {
  const container = document.getElementById("calendar-days-grid");
  if (!container) return;

  const monthNames = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
  const now = new Date();
  let currentYear = now.getFullYear();
  let currentMonth = now.getMonth();

  function renderCalendar(year, month) {
    const titleEl = document.getElementById("calendar-month-title");
    if (titleEl) {
      titleEl.textContent = `${monthNames[month]} ${year}`;
    }

    container.innerHTML = "";

    const daysOfWeek = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SAB"];
    daysOfWeek.forEach(d => {
      const th = document.createElement("div");
      th.className = "calendar-day-header";
      th.textContent = d;
      container.appendChild(th);
    });

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const prevMonthDays = new Date(year, month, 0).getDate();

    for (let i = firstDay - 1; i >= 0; i--) {
      const cell = document.createElement("div");
      cell.className = "calendar-day-cell pad-day";
      cell.textContent = prevMonthDays - i;
      container.appendChild(cell);
    }

    const today = new Date();
    for (let d = 1; d <= daysInMonth; d++) {
      const cell = document.createElement("div");
      cell.className = "calendar-day-cell";
      cell.textContent = d;

      if (d === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
        cell.classList.add("today");
      }

      if (d === 12 || d === 14 || d === 16 || d === 25) {
        cell.classList.add("has-event");
      }

      container.appendChild(cell);
    }
  }

  const prevBtn = document.getElementById("btn-cal-prev");
  const nextBtn = document.getElementById("btn-cal-next");

  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      currentMonth--;
      if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
      }
      renderCalendar(currentYear, currentMonth);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      currentMonth++;
      if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
      }
      renderCalendar(currentYear, currentMonth);
    });
  }

  renderCalendar(currentYear, currentMonth);
}

function showToast(message) {
  let toast = document.getElementById("app-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "app-toast";
    toast.className = "toast-notification";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add("visible");
  setTimeout(() => {
    toast.classList.remove("visible");
  }, 4000);
}
