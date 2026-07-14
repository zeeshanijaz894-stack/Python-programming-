// Dashboard main script

class Dashboard {
    constructor() {
        this.currentPage = 'dashboard';
        this.initializeEventListeners();
        this.loadDashboard();
        this.checkAuth();
    }
    
    checkAuth() {
        const user = localStorage.getItem('user');
        if (!user) {
            window.location.href = 'login.html';
            return;
        }
        
        const userData = JSON.parse(user);
        document.getElementById('userName').textContent = userData.email.split('@')[0];
    }
    
    initializeEventListeners() {
        // Sidebar menu items
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => this.switchPage(e));
        });
        
        // Logout button
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
        
        // Sidebar toggle
        document.getElementById('sidebarToggle').addEventListener('click', () => {
            document.querySelector('.sidebar').classList.toggle('show');
        });
        
        // Quick action buttons
        document.querySelectorAll('.btn-action').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleQuickAction(e));
        });
    }
    
    switchPage(e) {
        const page = e.target.closest('.menu-item').dataset.page;
        if (!page) return;
        
        // Remove active class from all menu items
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to clicked item
        e.target.closest('.menu-item').classList.add('active');
        
        // Hide all pages
        document.querySelectorAll('.page-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show selected page
        const pageElement = document.getElementById(`${page}-page`);
        if (pageElement) {
            pageElement.classList.add('active');
            document.getElementById('pageTitle').textContent = this.getPageTitle(page);
        }
        
        // Close sidebar on mobile
        if (window.innerWidth <= 480) {
            document.querySelector('.sidebar').classList.remove('show');
        }
    }
    
    getPageTitle(page) {
        const titles = {
            'dashboard': 'Dashboard',
            'students': 'Student Management',
            'attendance': 'Attendance',
            'results': 'Results',
            'classes': 'Classes',
            'fees': 'Fee Management',
            'payments': 'Payments',
            'reports': 'Reports',
            'templates': 'Templates',
            'settings': 'Settings',
            'users': 'User Management'
        };
        return titles[page] || 'Dashboard';
    }
    
    handleQuickAction(e) {
        const action = e.target.closest('.btn-action').dataset.action;
        console.log('Action:', action);
        
        switch(action) {
            case 'add-student':
                this.openStudentModal();
                break;
            case 'mark-attendance':
                this.switchToAttendance();
                break;
            case 'create-fee':
                this.openFeeModal();
                break;
            case 'generate-result':
                this.generateResult();
                break;
        }
    }
    
    loadDashboard() {
        // Load statistics
        this.loadStats();
        
        // Load recent activities
        this.loadRecentActivities();
    }
    
    loadStats() {
        // Placeholder data - will be replaced with API calls
        const stats = {
            totalStudents: 450,
            totalTeachers: 35,
            pendingFees: 15,
            activeClasses: 12
        };
        
        document.getElementById('totalStudents').textContent = stats.totalStudents;
        document.getElementById('totalTeachers').textContent = stats.totalTeachers;
        document.getElementById('pendingFees').textContent = stats.pendingFees;
        document.getElementById('activeClasses').textContent = stats.activeClasses;
    }
    
    loadRecentActivities() {
        const activities = [
            { time: '2 hours ago', desc: 'New student enrolled: Ali Ahmed' },
            { time: '5 hours ago', desc: 'Fee paid by: Muhammad Hassan' },
            { time: 'Yesterday', desc: 'Result uploaded for Class 10' },
            { time: '2 days ago', desc: 'Teacher attendance: 98%' }
        ];
        
        const container = document.getElementById('recentActivities');
        container.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-time">${activity.time}</div>
                <div class="activity-desc">${activity.desc}</div>
            </div>
        `).join('');
    }
    
    openStudentModal() {
        document.getElementById('studentModal').classList.add('show');
    }
    
    switchToAttendance() {
        const attendanceLink = document.querySelector('[data-page="attendance"]');
        if (attendanceLink) {
            attendanceLink.click();
        }
    }
    
    openFeeModal() {
        // Open fee modal
        console.log('Opening fee modal');
    }
    
    generateResult() {
        console.log('Generating result');
    }
    
    logout() {
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    }
}

// Modal handling
document.querySelectorAll('.close').forEach(closeBtn => {
    closeBtn.addEventListener('click', (e) => {
        e.target.closest('.modal').classList.remove('show');
    });
});

window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('show');
    }
});

// Student form handling
const studentForm = document.getElementById('studentForm');
if (studentForm) {
    studentForm.addEventListener('submit', (e) => {
        e.preventDefault();
        console.log('Student form submitted');
        document.getElementById('studentModal').classList.remove('show');
    });
}

// Initialize dashboard when DOM is loaded
let dashboard;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        dashboard = new Dashboard();
    });
} else {
    dashboard = new Dashboard();
}