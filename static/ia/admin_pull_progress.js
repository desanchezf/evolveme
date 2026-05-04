(function () {
    'use strict';

    var POLL_INTERVAL = 2000;
    var pollTimer = null;

    function getCsrf() {
        var el = document.querySelector('[name=csrfmiddlewaretoken]');
        if (el) return el.value;
        var match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    function updateBar(container, pct) {
        var fill = container.querySelector('.pull-bar-fill');
        var label = container.querySelector('.pull-bar-label');
        if (fill) fill.style.width = pct + '%';
        if (label) label.textContent = pct + '%';
    }

    function pollAll() {
        var bars = document.querySelectorAll('[data-pull-pk]');
        if (!bars.length) {
            clearInterval(pollTimer);
            pollTimer = null;
            return;
        }
        bars.forEach(function (container) {
            var pk = container.getAttribute('data-pull-pk');
            var url = container.getAttribute('data-progress-url');
            fetch(url, {credentials: 'same-origin'})
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (data.progress === null || data.progress === undefined) {
                        // Finished — reload to show final state
                        location.reload();
                    } else {
                        updateBar(container, data.progress);
                    }
                })
                .catch(function () {});
        });
    }

    function startPolling() {
        if (pollTimer) return;
        pollTimer = setInterval(pollAll, POLL_INTERVAL);
    }

    function handlePullClick(e) {
        e.preventDefault();
        var btn = e.currentTarget;
        var startUrl = btn.getAttribute('data-start-url');
        if (!startUrl) return;

        fetch(startUrl, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {'X-CSRFToken': getCsrf(), 'Content-Type': 'application/json'},
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.started) {
                    // Replace button with progress bar in the downloaded column
                    var row = btn.closest('tr');
                    if (row) {
                        var progressUrl = btn.getAttribute('data-progress-url');
                        var pk = btn.getAttribute('data-pk');
                        var dlCell = row.querySelector('.field-downloaded_display');
                        if (dlCell) {
                            dlCell.innerHTML =
                                '<div data-pull-pk="' + pk + '" data-progress-url="' + progressUrl + '" class="pull-bar-container">' +
                                '<div class="pull-bar-track"><div class="pull-bar-fill" style="width:0%"></div></div>' +
                                '<span class="pull-bar-label">0%</span>' +
                                '</div>';
                        }
                    }
                    startPolling();
                } else {
                    startPolling(); // already running, just poll
                }
            })
            .catch(function () {});
    }

    document.addEventListener('DOMContentLoaded', function () {
        // Wire up pull buttons
        document.querySelectorAll('[data-start-url]').forEach(function (btn) {
            btn.addEventListener('click', handlePullClick);
        });

        // If there are already in-progress bars (page reloaded mid-download)
        if (document.querySelector('[data-pull-pk]')) {
            startPolling();
        }
    });
})();
