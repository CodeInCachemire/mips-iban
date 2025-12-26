let mode = "IBAN";

function setLoading(isLoading) {
  document.getElementById("spinner").classList.toggle("hidden", !isLoading);

  document.getElementById("value1").disabled = isLoading;
  document.getElementById("value2").disabled = isLoading;

  document.querySelectorAll("button").forEach(btn => {
    btn.disabled = isLoading;
  });
}

function fetchWithTimeout(url, options, timeoutMs) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  return fetch(url, {
    ...options,
    signal: controller.signal
  }).finally(() => clearTimeout(id));
}




function selectMode(newMode) {
  mode = newMode;

  const btnIban = document.getElementById("btn-iban");
  const btnKnr = document.getElementById("btn-knrblz");
  const value2 = document.getElementById("value2");
  const label1 = document.getElementById("label-value1");
  const label2 = document.getElementById("label-value2");

  if (mode === "IBAN") {
    btnIban.classList.add("active");
    btnKnr.classList.remove("active");

    value2.disabled = true;
    value2.value = "";
    label2.classList.add("disabled");

    label1.textContent = "IBAN";
    document.getElementById("value1").placeholder =
      "DE02120300000000202051";
  } else {
    btnKnr.classList.add("active");
    btnIban.classList.remove("active");

    value2.disabled = false;
    label2.classList.remove("disabled");

    label1.textContent = "KNR (10 digits)";
    document.getElementById("value1").placeholder =
      "0000202051";
  }

  document.getElementById("output").textContent = "";
}

function isDigits(str) {
  return /^\d+$/.test(str);
}

function isAlphanumeric(str) {
  return /^[A-Za-z0-9]+$/.test(str);
}

function isLetters(str) {
  return /^[A-Za-z]+$/.test(str);
}

async function run() {
  const value1 = document.getElementById("value1").value.trim();
  const value2 = document.getElementById("value2").value.trim();
  const output = document.getElementById("output");

  // validate iban prevalidate before sending to backend
  if (mode === "IBAN") {
  if (value1.length !== 22) {
    output.textContent = "Error: IBAN must be exactly 22 characters long.";
    return;
  }

  const countryCode = value1.slice(0, 2);
  const rest = value1.slice(2);

  if (!isLetters(countryCode)) {
    output.textContent =
      "Error: The first two characters of an IBAN must be letters.";
    return;
  }

  if (!isDigits(rest)) {
    output.textContent =
      "Error: Characters 3–22 of an IBAN must be digits.";
    return;
  }
}

  if (mode === "KNRBLZ") {
    if (value1.length !== 10 || !isDigits(value1)) {
      output.textContent = "Error: KNR must be exactly 10 digits.";
      return;
    }

    if (value2.length !== 8 || !isDigits(value2)) {
      output.textContent = "Error: BLZ must be exactly 8 digits.";
      return;
    }
  }

  //end validation
  const body = {
    mode: mode,
    value1: value1
  };

  if (mode === "KNRBLZ") {
    body.value2 = value2;
  }
  setLoading(true)
  output.textContent = "Running...";

  try {
    const response = await fetchWithTimeout("/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    },8000);

    const data = await response.json();

    if (!response.ok) {
      output.textContent = "Error:\n" + data.detail;
      return;
    }

    output.textContent = JSON.stringify(data, null, 2);
    if (typeof loadHistory === "function") {
      loadHistory();
    }
  } catch (err) {
    output.textContent = "Network error: backend not reachable";
  } finally {
    setLoading(false)
  }
}
