let currentRole = 'farmer';

function toggleRole() {
    setRole(currentRole === 'farmer' ? 'sci' : 'farmer');
}

function setRole(role) {
    currentRole = role;
    const body = document.body;
    const farmerBtn = document.getElementById('btn-farmer');
    const sciBtn = document.getElementById('btn-sci');
    const headline = document.getElementById('role-headline');
    const mainBtn = document.getElementById('main-btn');
    const hint = document.getElementById('avatar-hint');
    const farmerImg = document.getElementById('farmer-avatar');
    const sciImg = document.getElementById('sci-avatar');

    if (role === 'sci') {
        body.classList.add('sci');
        sciBtn.classList.add('active');
        farmerBtn.classList.remove('active');
        headline.textContent = 'Advanced Research & Insights';
        mainBtn.textContent = 'Enter Research Lab';
        hint.textContent = 'Switch to Farmer';
        farmerImg.classList.add('hidden');
        sciImg.classList.remove('hidden');
    } else {
        body.classList.remove('sci');
        farmerBtn.classList.add('active');
        sciBtn.classList.remove('active');
        headline.textContent = 'Empowering Growth for Every Farmer';
        mainBtn.textContent = 'Login to Portal';
        hint.textContent = 'Switch to Researcher';
        sciImg.classList.add('hidden');
        farmerImg.classList.remove('hidden');
    }
}

function togglePass() {
    const pf = document.getElementById('pass-field');
    const icon = document.getElementById('eye-icon');
    if (pf.type === 'password') {
        pf.type = 'text';
        icon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
    } else {
        pf.type = 'password';
        icon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
    }
}

function createParticles() {
    const container = document.getElementById('particles');
    const count = 15;
    for (let i = 0; i < count; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = Math.random() * 5 + 2;
        p.style.width = `${size}px`;
        p.style.height = `${size}px`;
        p.style.left = `${Math.random() * 100}vw`;
        p.style.background = Math.random() > 0.5 ? '#6b9e3b' : '#00d4ff';
        p.style.animationDuration = `${Math.random() * 4 + 6}s`;
        p.style.animationDelay = `${Math.random() * 8}s`;
        container.appendChild(p);
    }
}

createParticles();