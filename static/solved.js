function setLabSolved(labNum, solved) {
    let solvedLabs = JSON.parse(localStorage.getItem('solvedLabs') || '{}');
    solvedLabs[labNum] = solved;
    localStorage.setItem('solvedLabs', JSON.stringify(solvedLabs));
    // Update home page status if on home page
    if (window.location.pathname === '/') {
        updateHomeStatus();
    }
}

function isLabSolved(labNum) {
    let solvedLabs = JSON.parse(localStorage.getItem('solvedLabs') || '{}');
    return solvedLabs[labNum] === true;
}

function updateHomeStatus() {
    let solved = JSON.parse(localStorage.getItem('solvedLabs') || '{}');
    for (let i=1; i<=8; i++) {
        let span = document.getElementById(`status-${i}`);
        if (span) {
            if (solved[i]) {
                span.textContent = '✓ Solved';
                span.className = 'solved-mark';
            } else {
                span.textContent = 'Not solved';
                span.className = 'unsolved-mark';
            }
        }
    }
}

function markCurrentLab(labNum, solved) {
    if (solved) {
        setLabSolved(labNum, true);
        let banner = document.createElement('div');
        banner.className = 'congrats-banner';
        banner.innerHTML = '<strong>🎉 Congratulations, you solved the lab!</strong> <a href="/">Continue learning →</a>';
        banner.style.background = '#e6fffa';
        banner.style.borderLeft = '4px solid #28a745';
        banner.style.padding = '15px';
        banner.style.margin = '20px 0';
        banner.style.borderRadius = '8px';
        let container = document.querySelector('.container');
        if (container && !document.querySelector('.congrats-banner')) {
            container.insertBefore(banner, container.firstChild);
        }
    }
}