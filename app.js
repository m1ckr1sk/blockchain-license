const state = {
  chain: [],
  licenses: [],
  audit: [],
};

const ui = {
  chainStatus: document.getElementById('chain-status'),
  ledgerBadge: document.getElementById('ledger-badge'),
  activeLicenseCount: document.getElementById('active-license-count'),
  lastAccessState: document.getElementById('last-access-state'),
  licenseForm: document.getElementById('license-form'),
  licenseResult: document.getElementById('license-result'),
  contentAccess: document.getElementById('content-access'),
  contentResult: document.getElementById('content-result'),
  contentPreview: document.getElementById('content-preview'),
  validateChain: document.getElementById('validate-chain'),
  revokeLicense: document.getElementById('revoke-license'),
  tamperChain: document.getElementById('tamper-chain'),
  registerPeer: document.getElementById('register-peer'),
  syncPeer: document.getElementById('sync-peer'),
  peerNameInput: document.getElementById('peer-name-input'),
  chainList: document.getElementById('chain-list'),
  auditList: document.getElementById('audit-list'),
  licenseIdInput: document.getElementById('license-id-input'),
  licensesTableBody: document.getElementById('licenses-table-body'),
};

async function apiFetch(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};

  if (!response.ok) {
    throw new Error(payload.detail || 'Request failed.');
  }

  return payload;
}

function setResult(element, kind, message) {
  element.className = `result-box ${kind}`;
  element.textContent = message;
}

function addAuditEntry(message) {
  state.audit.unshift({
    id: `${Date.now()}-${Math.random()}`,
    message,
    timestamp: new Date().toISOString(),
  });
  renderAudit();
}

function renderAudit() {
  ui.auditList.innerHTML = state.audit
    .map(
      (entry) => `
        <li class="audit-item">
          <strong>${entry.message}</strong>
          <small>${entry.timestamp}</small>
        </li>
      `,
    )
    .join('');
}

function renderLedger() {
  ui.chainList.innerHTML = (state.chain || [])
    .map(
      (block) => `
        <li class="ledger-item">
          <strong>Block #${block.index}: ${block.event?.type}</strong>
          <small>${block.hash?.slice(0, 12) || 'n/a'}...</small>
        </li>
      `,
    )
    .join('');
}

function toDate(value) {
  if (!value) {
    return null;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }

  return parsed;
}

function deriveLicenseState(license) {
  const explicit = String(license.status || '').toUpperCase();
  if (explicit === 'REVOKED' || explicit === 'EXPIRED' || explicit === 'ACTIVE') {
    return explicit;
  }

  if (license.revoked === true || license.isRevoked === true || license.revokedAt) {
    return 'REVOKED';
  }

  const expiresAt = toDate(license.expiresAt || license.expires_at);
  if (expiresAt && expiresAt.getTime() <= Date.now()) {
    return 'EXPIRED';
  }

  return 'ACTIVE';
}

function formatDate(dateLike) {
  const date = toDate(dateLike);
  if (!date) {
    return 'n/a';
  }

  return date.toLocaleString();
}

function renderLicenses() {
  const licenses = [...(state.licenses || [])].sort((a, b) => {
    const left = toDate(a.issuedAt || a.issued_at)?.getTime() || 0;
    const right = toDate(b.issuedAt || b.issued_at)?.getTime() || 0;
    return right - left;
  });

  if (!licenses.length) {
    ui.licensesTableBody.innerHTML = `
      <tr>
        <td colspan="6" class="licenses-empty">No licenses have been issued yet.</td>
      </tr>
    `;
    return;
  }

  ui.licensesTableBody.innerHTML = licenses
    .map((license) => {
      const status = deriveLicenseState(license);
      const badgeClass = status === 'ACTIVE' ? 'status-active' : status === 'REVOKED' ? 'status-revoked' : 'status-expired';
      return `
        <tr>
          <td>${license.licenseId || 'n/a'}</td>
          <td>${license.userId || 'n/a'}</td>
          <td>${license.contentId || license.content_id || 'n/a'}</td>
          <td>${formatDate(license.issuedAt || license.issued_at)}</td>
          <td>${formatDate(license.expiresAt || license.expires_at)}</td>
          <td><span class="license-state ${badgeClass}">${status}</span></td>
        </tr>
      `;
    })
    .join('');
}

function getLatestLicense() {
  if (!state.licenses.length) {
    return null;
  }

  return [...state.licenses].sort((a, b) => (a.licenseId > b.licenseId ? 1 : -1)).at(-1) || state.licenses.at(-1);
}

async function refreshDashboard() {
  try {
    const [chainData, licenseData, validationData, peersData] = await Promise.all([
      apiFetch('/blockchain'),
      apiFetch('/licenses'),
      apiFetch('/blockchain/validate'),
      apiFetch('/peers'),
    ]);

    state.chain = chainData.blocks || [];
    state.licenses = licenseData.licenses || [];
    const peerNames = Object.keys(peersData.peers || {});

    const activeCount = state.licenses.filter((license) => deriveLicenseState(license) === 'ACTIVE').length;
    ui.activeLicenseCount.textContent = String(activeCount);

    if (validationData.valid) {
      ui.chainStatus.textContent = 'Valid';
      ui.chainStatus.style.color = '#34d399';
      ui.ledgerBadge.textContent = 'Valid';
      ui.ledgerBadge.className = 'status-good';
    } else {
      ui.chainStatus.textContent = 'Invalid';
      ui.chainStatus.style.color = '#f87171';
      ui.ledgerBadge.textContent = 'Invalid';
      ui.ledgerBadge.className = 'status-bad';
    }

    renderLedger();
    renderLicenses();
    if (peerNames.length) {
      addAuditEntry(`Known peers: ${peerNames.join(', ')}.`);
    }
  } catch (error) {
    setResult(ui.licenseResult, 'error', `Unable to reach backend: ${error.message}`);
    setResult(ui.contentResult, 'error', `Unable to reach backend: ${error.message}`);
  }
}

async function handleLicenseCreate(event) {
  event.preventDefault();

  const formData = new FormData(event.currentTarget);
  const userId = formData.get('userId')?.toString().trim();
  const contentId = formData.get('contentId')?.toString().trim();
  const days = Number(formData.get('days') || 30);

  if (!userId || !contentId) {
    setResult(ui.licenseResult, 'error', 'User ID and content ID are required.');
    return;
  }

  try {
    const expiresAt = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString();
    const license = await apiFetch('/licenses', {
      method: 'POST',
      body: JSON.stringify({ userId, contentId, expiresAt }),
    });

    ui.licenseIdInput.value = license.licenseId;
    const latest = getLatestLicense();
    setResult(ui.licenseResult, 'success', `License ${license.licenseId} created successfully.`);
    addAuditEntry(`License ${license.licenseId} created for ${contentId}.`);
    await refreshDashboard();
    if (latest) {
      ui.licenseIdInput.value = latest.licenseId;
    }
  } catch (error) {
    setResult(ui.licenseResult, 'error', error.message);
  }
}

async function handleContentAccess() {
  const licenseId = ui.licenseIdInput.value.trim();
  const contentId = document.getElementById('content-id').value.trim() || 'content-001';

  if (!licenseId) {
    setResult(ui.contentResult, 'error', 'Enter a license ID before requesting content.');
    return;
  }

  try {
    const content = await apiFetch(`/content/${encodeURIComponent(contentId)}?licenseId=${encodeURIComponent(licenseId)}`);
    ui.lastAccessState.textContent = 'Granted';
    ui.lastAccessState.style.color = '#34d399';
    ui.contentPreview.textContent = JSON.stringify(content, null, 2);
    setResult(ui.contentResult, 'success', `Access granted for license ${licenseId}.`);
    addAuditEntry(`Protected content access granted to ${licenseId}.`);
    await refreshDashboard();
  } catch (error) {
    ui.lastAccessState.textContent = 'Denied';
    ui.lastAccessState.style.color = '#f87171';
    ui.contentPreview.textContent = 'Protected content is blocked by the backend validation rules.';
    setResult(ui.contentResult, 'error', error.message);
    addAuditEntry(`Content access denied: ${error.message}`);
  }
}

async function handleChainValidation() {
  try {
    const result = await apiFetch('/blockchain/validate');
    if (result.valid) {
      ui.chainStatus.textContent = 'Valid';
      ui.chainStatus.style.color = '#34d399';
      ui.ledgerBadge.textContent = 'Valid';
      ui.ledgerBadge.className = 'status-good';
      setResult(ui.contentResult, 'success', 'Blockchain validation passed.');
      addAuditEntry('Blockchain validated successfully.');
    } else {
      ui.chainStatus.textContent = 'Invalid';
      ui.chainStatus.style.color = '#f87171';
      ui.ledgerBadge.textContent = 'Invalid';
      ui.ledgerBadge.className = 'status-bad';
      setResult(ui.contentResult, 'error', `Validation failed: ${result.message}`);
      addAuditEntry(`Blockchain validation failed: ${result.message}`);
    }
    await refreshDashboard();
  } catch (error) {
    setResult(ui.contentResult, 'error', error.message);
  }
}

async function handleRevocation() {
  const latestLicense = getLatestLicense();
  if (!latestLicense) {
    setResult(ui.licenseResult, 'error', 'No license exists to revoke.');
    return;
  }

  try {
    const revoked = await apiFetch(`/licenses/${encodeURIComponent(latestLicense.licenseId)}/revoke`, {
      method: 'POST',
    });
    setResult(ui.licenseResult, 'success', `License ${revoked.licenseId} revoked.`);
    addAuditEntry(`License ${revoked.licenseId} was revoked.`);
    await refreshDashboard();
  } catch (error) {
    setResult(ui.licenseResult, 'error', error.message);
  }
}

async function handleTampering() {
  try {
    const result = await apiFetch('/blockchain/tamper', { method: 'POST' });
    if (result.valid) {
      setResult(ui.contentResult, 'success', 'Tampering was not detected.');
    } else {
      setResult(ui.contentResult, 'error', `Tamper detection succeeded: ${result.message}`);
    }
    addAuditEntry('Tamper simulation executed.');
    await refreshDashboard();
  } catch (error) {
    setResult(ui.contentResult, 'error', error.message);
  }
}

async function handlePeerRegister() {
  const peerName = ui.peerNameInput.value.trim();
  if (!peerName) {
    setResult(ui.licenseResult, 'error', 'Peer name is required.');
    return;
  }

  try {
    const result = await apiFetch('/peers', {
      method: 'POST',
      body: JSON.stringify({ name: peerName }),
    });
    setResult(ui.licenseResult, 'success', `Peer ${result.name} registered with ${result.chain_length} blocks.`);
    addAuditEntry(`Peer ${result.name} registered.`);
    await refreshDashboard();
  } catch (error) {
    setResult(ui.licenseResult, 'error', error.message);
  }
}

async function handlePeerSync() {
  const peerName = ui.peerNameInput.value.trim();
  if (!peerName) {
    setResult(ui.licenseResult, 'error', 'Enter a peer name before syncing.');
    return;
  }

  try {
    const result = await apiFetch(`/peers/${encodeURIComponent(peerName)}/sync`, { method: 'POST' });
    if (result.adopted) {
      setResult(ui.licenseResult, 'success', `Peer ${peerName} chain adopted successfully.`);
      addAuditEntry(`Local chain synced with ${peerName}.`);
    } else {
      setResult(ui.licenseResult, 'error', `Peer ${peerName} was not adopted: ${result.reason}`);
      addAuditEntry(`Peer sync rejected: ${result.reason}`);
    }
    await refreshDashboard();
  } catch (error) {
    setResult(ui.licenseResult, 'error', error.message);
  }
}

ui.licenseForm.addEventListener('submit', handleLicenseCreate);
ui.contentAccess.addEventListener('click', handleContentAccess);
ui.validateChain.addEventListener('click', handleChainValidation);
ui.revokeLicense.addEventListener('click', handleRevocation);
ui.tamperChain.addEventListener('click', handleTampering);
ui.registerPeer.addEventListener('click', handlePeerRegister);
ui.syncPeer.addEventListener('click', handlePeerSync);

refreshDashboard();
renderAudit();
