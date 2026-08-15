# Phase 5: Student Management - Attendance & Leave System

## Overview
Phase 5 implements a comprehensive Attendance and Leave Management System for the Student Management Platform.

## Features

### 1. **Attendance Management**
- Individual student attendance marking
- Bulk attendance marking for entire classes
- Attendance status tracking (present, absent, late, leave, excused)
- Monthly attendance summaries and reports
- Attendance analytics and statistics
- Percentage-based attendance tracking

### 2. **Leave Management**
- Student leave application workflow
- Leave approval/rejection process
- Multiple leave types (medical, casual, emergency, parental, other)
- Leave balance tracking
- Leave policies management
- Monthly leave statistics

### 3. **Analytics & Reporting**
- Attendance reports by student, class, or date
- Monthly attendance summaries
- Leave statistics and trends
- Performance indicators
- Percentage calculations

## Database Schema

### Tables Created:
1. **attendance** - Individual attendance records
2. **monthly_attendance_summary** - Aggregated monthly summaries
3. **leaves** - Leave applications and history
4. **leave_policies** - School-wide leave policies

## API Endpoints

### Attendance Endpoints
```
POST   /api/attendance/mark              - Mark individual attendance
POST   /api/attendance/bulk-mark         - Bulk mark attendance
GET    /api/attendance/student/:id       - Get student attendance
GET    /api/attendance/class/:id         - Get class attendance
GET    /api/attendance/report/:id        - Get attendance report
GET    /api/attendance/analytics         - Get attendance analytics
GET    /api/attendance/summary/:id       - Get monthly summary
```

### Leave Endpoints
```
POST   /api/leave/apply                  - Apply for leave
GET    /api/leave/student/:id            - Get student leaves
PUT    /api/leave/approve/:id            - Approve leave
PUT    /api/leave/reject/:id             - Reject leave
GET    /api/leave/pending                - Get pending leaves
GET    /api/leave/balance/:id            - Get leave balance
GET    /api/leave/statistics             - Get statistics
POST   /api/leave/policy                 - Create leave policy
GET    /api/leave/policies               - Get leave policies
```

## Usage Examples

### Mark Attendance
```json
POST /api/attendance/mark
{
    "school_id": 1,
    "student_id": 101,
    "class_id": 5,
    "attendance_date": "2024-08-15",
    "status": "present",
    "remarks": "Present"
}
```

### Apply for Leave
```json
POST /api/leave/apply
{
    "school_id": 1,
    "student_id": 101,
    "leave_type": "medical",
    "start_date": "2024-08-20",
    "end_date": "2024-08-22",
    "reason": "Medical appointment"
}
```

### Get Attendance Report
```
GET /api/attendance/report/101?school_id=1&month=8&year=2024
```

### Get Leave Balance
```
GET /api/leave/balance/101?school_id=1
```

## Features Implemented

✅ Attendance marking and tracking
✅ Bulk attendance operations
✅ Monthly summaries and reports
✅ Attendance analytics
✅ Leave application workflow
✅ Leave approval/rejection process
✅ Leave balance management
✅ Leave policies
✅ Statistics and reporting
✅ Data validation
✅ Error handling
✅ RESTful API design

## Technical Details

- **Framework**: Flask
- **Database**: MySQL/MariaDB
- **Authentication**: Token-based (JWT)
- **Error Handling**: Comprehensive try-catch blocks
- **Data Validation**: Input validation on all endpoints
- **Service Layer**: Business logic separation

## Files Structure

```
backend/
├── models/
│   ├── attendance.py       - Attendance model
│   └── leave.py            - Leave model
├── routes/
│   ├── attendance.py       - Attendance routes
│   └── leave.py            - Leave routes
├── services/
│   └── attendance_service.py - Business logic
├── database/
│   └── schema_phase5.py    - Database schema
├── config.py               - Configuration
├── app.py                  - Main application
└── requirements.txt        - Dependencies
```

## Testing

All endpoints are protected with token-based authentication. Include Authorization header:
```
Authorization: Bearer <your-token>
```

## Future Enhancements

- SMS/Email notifications for leave approvals
- Calendar integration
- Automated reports generation
- Mobile app integration
- Biometric attendance support
- QR code-based attendance
- Advanced analytics dashboard

## Notes

- All timestamps are in UTC
- Dates are in YYYY-MM-DD format
- Status codes follow HTTP standards
- All responses are in JSON format
- Database transactions are atomic

---

**Phase 5 Completion**: ✅ All core features implemented and tested
