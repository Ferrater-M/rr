document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        userProfile: document.getElementById('userProfile'),
        dropdown: document.getElementById('profileDropdown'),
        logoutBtn: document.getElementById('btnLogout')
    };

    const setupEventListeners = () => {

        elements.userProfile.addEventListener('click', (e) => {
            e.stopPropagation();
            elements.dropdown.classList.toggle('show');
        });

        document.addEventListener('click', (e) => {
            if (!elements.dropdown.contains(e.target) && 
                !elements.userProfile.contains(e.target)) {
                elements.dropdown.classList.remove('show');
            }
        });

        elements.dropdown.addEventListener('click', (e) => e.stopPropagation());

        elements.logoutBtn.addEventListener('click', handleLogout);
    };

    const handleLogout = () => {
        window.MessageBox.showConfirm('Are you sure you want to logout?', () => {
            window.ApiCaller.auth.signOut(() => window.MessageBox.hide());
        });
    };

    setupEventListeners();
});
