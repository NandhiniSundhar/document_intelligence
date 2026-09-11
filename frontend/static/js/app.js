async function loadDocuments() {
  const tbody = document.getElementById("documents");
  tbody.innerHTML = "<tr><td colspan='5'>Loading...</td></tr>";
  try {
    const r = await fetch("/api/v1/documents");
    const d = await r.json();
    tbody.innerHTML = (d.documents || []).map(x => `
      <tr>
        <td>${escapeHtml(x.document_name)}</td>
        <td>${escapeHtml(x.document_type)}</td>
        <td class="${x.processing_status === 'PASS' ? 'pass':'fail'}">${escapeHtml(x.processing_status)}</td>
        <td>${escapeHtml(x.processed_at)}</td>
        <td><a href="/documents/${encodeURIComponent(x.document_name)}">View</a></td>
      </tr>`).join("") || "<tr><td colspan='5'>No documents processed yet.</td></tr>";
  } catch (e) {
    tbody.innerHTML = "<tr><td colspan='5'>Unable to load dashboard.</td></tr>";
  }
}

function escapeHtml(v) {
  return String(v ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[c]));
}

document.getElementById("uploadForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = document.getElementById("message");
  const file = document.getElementById("file").files[0];
  const type = document.getElementById("documentType").value;
  if (!file) return;

  const fd = new FormData();
  fd.append("file", file);
  fd.append("document_type", type);

  msg.textContent = "Processing...";
  try {
    const r = await fetch("/api/v1/documents/process", { method:"POST", body:fd });
    const d = await r.json();
    if (!r.ok) {
      msg.textContent = JSON.stringify(d, null, 2);
      return;
    }
    msg.textContent = "Processed successfully.";
    loadDocuments();
    window.location.href = "/documents/" + encodeURIComponent(d.document_name);
  } catch (err) {
    msg.textContent = "Request failed. Check the API/server.";
  }
});

loadDocuments();
