// Client-only implementation using localStorage so no server/Node required.
const laneCountInput = document.getElementById('lane-count');
const setLanesBtn = document.getElementById('set-lanes');
const laneSelect = document.getElementById('lane');
const reservationsContainer = document.getElementById('reservations');
const form = document.getElementById('reserve-form');
const messageEl = document.getElementById('message');

const STORAGE_KEY = 'bowling_reservations_v1';

function loadReservations() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    console.error('loadReservations error', e);
    return {};
  }
}

function saveReservations(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (e) {
    console.error('saveReservations error', e);
  }
}

function setLanes(n) {
  laneSelect.innerHTML = '';
  for (let i = 1; i <= n; i++) {
    const opt = document.createElement('option');
    opt.value = String(i);
    opt.textContent = 'Baan ' + i;
    laneSelect.appendChild(opt);
  }
}

function renderReservations(data, lanes) {
  reservationsContainer.innerHTML = '';
  for (let i = 1; i <= lanes; i++) {
    const lane = String(i);
    const box = document.createElement('div');
    box.className = 'lane-box';
    const title = document.createElement('h3');
    title.textContent = 'Baan ' + lane;
    box.appendChild(title);
    const list = document.createElement('div');
    const items = (data[lane] || []);
    if (items.length === 0) {
      const p = document.createElement('p');
      p.textContent = 'Geen reserveringen';
      list.appendChild(p);
    } else {
      items.forEach((r, idx) => {
        const row = document.createElement('div');
        row.className = 'lane-row';
        const info = document.createElement('div');
        info.className = 'reservation';
        const start = new Date(r.start).toLocaleString();
        info.innerHTML = `<strong>${r.name}</strong><br><small>${start} — ${r.duration} min</small>`;
        const btn = document.createElement('button');
        btn.textContent = 'Verwijder';
        btn.onclick = () => {
          const data = loadReservations();
          if (Array.isArray(data[lane])) {
            data[lane].splice(idx, 1);
            saveReservations(data);
            messageEl.textContent = 'Reservering verwijderd.';
            renderReservations(data, lanes);
          }
        };
        row.appendChild(info);
        row.appendChild(btn);
        list.appendChild(row);
      });
    }
    box.appendChild(list);
    reservationsContainer.appendChild(box);
  }
}

function refresh() {
  const lanes = Number(laneCountInput.value) || 4;
  setLanes(lanes);
  const data = loadReservations();
  renderReservations(data, lanes);
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  messageEl.textContent = '';
  const lane = laneSelect.value;
  const name = document.getElementById('name').value.trim();
  const start = document.getElementById('start').value;
  const duration = Number(document.getElementById('duration').value);
  if (!name || !start) {
    messageEl.textContent = 'Vul naam en starttijd in.';
    return;
  }
  const data = loadReservations();
  data[lane] = data[lane] || [];
  // simple overlap check
  const overlap = data[lane].some(r => {
    const a1 = new Date(r.start).getTime();
    const a2 = a1 + r.duration * 60000;
    const b1 = new Date(start).getTime();
    const b2 = b1 + duration * 60000;
    return a1 < b2 && b1 < a2;
  });
  if (overlap) {
    messageEl.textContent = 'Conflict: baan al gereserveerd in die tijd';
    return;
  }
  data[lane].push({ start, duration, name });
  saveReservations(data);
  messageEl.textContent = 'Gereserveerd!';
  form.reset();
  refresh();
});

setLanes(Number(laneCountInput.value));
setLanesBtn.addEventListener('click', () => refresh());
refresh();
