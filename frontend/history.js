async function loadHistory() {
  const tbody = document.getElementById("history-list");

  try {
    const response = await fetch("/history");
    if (!response.ok) {
      throw new Error("Failed to fetch history");
    }

    const history = await response.json();

    tbody.innerHTML = "";

    if (history.length === 0) {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td colspan="5">No conversions yet.</td>`;
      tbody.appendChild(tr);
      return;
    }

    for (const entry of history) {
      const tr = document.createElement("tr");
      const localTime = new Date(entry.created_at + "Z").toLocaleString();

      tr.innerHTML = `
        <td>${entry.id}</td>
        <td>${entry.direction}</td>
        <td>${formatKeyValue(entry.input)}</td>
        <td>${formatKeyValue(entry.output)}</td>
        <td>${localTime}</td>
      `;

      tbody.appendChild(tr);
    }
  } catch (err) {
    console.error(err);
    tbody.innerHTML = `<tr><td colspan="5">Error loading history.</td></tr>`;
  }
}

function formatKeyValue(obj) {
  if (!obj || Object.keys(obj).length === 0) {
    return "—";
  }

  return Object.entries(obj)
    .map(([key, value]) => `${key}: ${value}`)
    .join(", ");
}

window.addEventListener("DOMContentLoaded", loadHistory);
