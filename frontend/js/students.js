// Students management

class StudentManager {
    constructor() {
        this.students = [];
        this.loadStudents();
    }
    
    loadStudents() {
        // Mock data - will be replaced with API calls
        this.students = [
            { id: 1, roll_number: '001', name: 'Ali Ahmed', class: '10-A', email: 'ali@school.com', phone: '03001234567', status: 'Active' },
            { id: 2, roll_number: '002', name: 'Fatima Khan', class: '10-A', email: 'fatima@school.com', phone: '03009876543', status: 'Active' },
            { id: 3, roll_number: '003', name: 'Hassan Muhammad', class: '10-B', email: 'hassan@school.com', phone: '03005555555', status: 'Active' },
        ];
        this.displayStudents();
    }
    
    displayStudents() {
        const table = document.getElementById('studentsTable');
        if (!table) return;
        
        table.innerHTML = this.students.map(student => `
            <tr>
                <td>${student.roll_number}</td>
                <td>${student.name}</td>
                <td>${student.class}</td>
                <td>${student.email}</td>
                <td>${student.phone}</td>
                <td><span class="badge-${student.status.toLowerCase()}">${student.status}</span></td>
                <td>
                    <button class="btn-small" onclick="studentManager.editStudent(${student.id})">Edit</button>
                    <button class="btn-small" onclick="studentManager.deleteStudent(${student.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    }
    
    editStudent(id) {
        console.log('Editing student:', id);
        document.getElementById('studentModal').classList.add('show');
    }
    
    deleteStudent(id) {
        if (confirm('Are you sure?')) {
            this.students = this.students.filter(s => s.id !== id);
            this.displayStudents();
        }
    }
}

const studentManager = new StudentManager();