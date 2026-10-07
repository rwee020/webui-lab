const sidebarNav = document.getElementById('sidebarNav');
const sectionTitle = document.getElementById('sectionTitle');
const cardsGrid = document.getElementById('cardsGrid');

let data = null;
let activeSection = 'dashboard';

function renderSidebar(menu) {
  sidebarNav.innerHTML = menu
    .map(
      (item) => `
        <button
          type="button"
          class="sidebar-link ${item.id === activeSection ? 'is-active' : ''}"
          data-section-id="${item.id}"
          aria-label="${item.label}"
        >
          <span class="sidebar-icon">${item.icon}</span>
          <span>${item.label}</span>
        </button>
      `
    )
    .join('');

  sidebarNav.querySelectorAll('.sidebar-link').forEach((button) => {
    button.addEventListener('click', () => {
      activeSection = button.dataset.sectionId;
      render();
    });
  });
}

function renderCards() {
  const section = data.sections[activeSection];

  if (!section) {
    cardsGrid.innerHTML = '<div class="empty-state">目前沒有可顯示的資料。</div>';
    return;
  }

  sectionTitle.textContent = section.title;

  cardsGrid.innerHTML = section.cards
    .map(
      (card) => `
        <article class="stat-card">
          <div class="card-top">
            <span class="card-label">${card.label}</span>
            <span class="card-tag ${card.trend || 'neutral'}">${card.meta}</span>
          </div>
          <h3>${card.value}</h3>
          <p>${card.description}</p>
          <div class="card-footer">
            <span>${card.meta}</span>
            <strong>${card.change}</strong>
          </div>
        </article>
      `
    )
    .join('');
}

function render() {
  if (!data) return;
  renderSidebar(data.menu);
  renderCards();
}

async function loadData() {
  try {
    const response = await fetch('./json/teacher_ops.json');
    if (!response.ok) {
      throw new Error('JSON data load failed');
    }
    data = await response.json();
    if (data.defaultSection) {
      activeSection = data.defaultSection;
    }
    render();
  } catch (error) {
    sectionTitle.textContent = '資料載入失敗';
    cardsGrid.innerHTML = '<div class="empty-state">無法載入 sidebar JSON 資料，請確認 json/teacher_ops.json 是否存在。</div>';
    console.error(error);
  }
}

loadData();
