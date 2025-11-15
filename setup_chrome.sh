#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------------------------
# setup_chrome.sh
# Installs Google Chrome (stable) and the matching ChromeDriver on Ubuntu.
# - Idempotent: safe to re-run
# - Uses official chrome-for-testing bucket for exact version match
# - Places Chrome at /usr/bin/google-chrome and chromedriver at /usr/local/bin/chromedriver
# ------------------------------------------------------------------------------

log() { printf "\n[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

require_root() {
  if [[ $EUID -ne 0 ]]; then
    log "Please run as root (e.g., sudo bash setup_chrome.sh)"
    exit 1
  fi
}

install_deps() {
  log "Updating apt and installing prerequisites..."
  apt-get update -y
  apt-get install -y wget curl unzip ca-certificates gnupg apt-transport-https \
    xvfb libnss3 libxss1 libxi6 libgconf-2-4 libappindicator1 libindicator7 libgbm-dev
}

install_chrome() {
  if command -v google-chrome >/dev/null 2>&1; then
    log "Google Chrome already installed: $(google-chrome --version)"
    return
  fi

  log "Downloading Google Chrome (stable) .deb..."
  CHROME_DEB="google-chrome-stable_current_amd64.deb"
  rm -f "$CHROME_DEB"
  wget -q https://dl.google.com/linux/direct/${CHROME_DEB}

  log "Installing Google Chrome..."
  apt-get install -y ./${CHROME_DEB}
  rm -f "${CHROME_DEB}"

  log "Installed: $(google-chrome --version)"
  chmod +x /usr/bin/google-chrome || true
}

get_chrome_version() {
  if ! command -v google-chrome >/dev/null 2>&1; then
    log "google-chrome not found after install."
    exit 1
  fi
  google-chrome --version | awk '{print $3}'
}

install_chromedriver() {
  local chrome_version="$1"
  local url_base="https://storage.googleapis.com/chrome-for-testing-public"
  local zfile
  local major minor patch build
  IFS='.' read -r major minor patch build <<< "$chrome_version"

  # We’ll try exact version first; if not found, we’ll fallback to the same-major latest.
  zfile="${chrome_version}/linux64/chromedriver-linux64.zip"
  log "Attempting to download matching ChromeDriver for Chrome ${chrome_version}"
  if ! curl -sI "${url_base}/${zfile}" | head -n1 | grep -q "200"; then
    log "Exact ChromeDriver ${chrome_version} not found. Falling back to latest for major ${major}..."
    # Query the 'LATEST_RELEASE_{major}' endpoint to get a compatible version
    fallback_version=$(curl -fsSL "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${major}" || true)
    if [[ -z "${fallback_version}" ]]; then
      log "Could not determine fallback ChromeDriver version for major ${major}."
      exit 1
    fi
    log "Using fallback ChromeDriver version: ${fallback_version}"
    zfile="${fallback_version}/linux64/chromedriver-linux64.zip"
  else
    log "Found exact ChromeDriver for ${chrome_version}."
  fi

  TMPDIR="$(mktemp -d)"
  pushd "$TMPDIR" >/dev/null

  log "Downloading ${url_base}/${zfile}"
  wget -q "${url_base}/${zfile}"

  log "Unzipping chromedriver..."
  unzip -q chromedriver-linux64.zip

  log "Installing chromedriver to /usr/local/bin/chromedriver"
  install -m 0755 "chromedriver-linux64/chromedriver" /usr/local/bin/chromedriver

  popd >/dev/null
  rm -rf "$TMPDIR"

  log "Installed: $(chromedriver --version)"
}

sanity_test() {
  log "Running headless Chrome sanity test (fetch google.com DOM)..."
  if ! google-chrome --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
      --dump-dom https://www.google.com >/dev/null 2>&1; then
    log "Headless Chrome test failed (this can still be fine in some containerized setups)."
  else
    log "Headless Chrome test OK."
  fi

  log "Paths:"
  command -v google-chrome || true
  command -v chromedriver || true
}

main() {
  require_root
  install_deps
  install_chrome
  CHROME_VER="$(get_chrome_version)"
  log "Detected Chrome version: ${CHROME_VER}"
  install_chromedriver "${CHROME_VER}"
  sanity_test

  log "All done! Summary:"
  log "  Chrome:      $(google-chrome --version)"
  log "  ChromeDriver: $(chromedriver --version)"
  log "  Binary paths:"
  log "    - Chrome:      /usr/bin/google-chrome"
  log "    - ChromeDriver: /usr/local/bin/chromedriver"
}

main "$@"
