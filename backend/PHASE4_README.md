# Authentication & PDF Generation Features

## Authentication

### Login Endpoint
```bash
POST /api/auth/login
Body: {
    "email": "user@school.com",
    "password": "password123",
    "school_code": "SCHOOL001"
}

Response: {
    "success": true,
    "token": "eyJhbGc...",
    "user": {...}
}
```

### School Registration
```bash
POST /api/auth/register-school
Body: {
    "school_name": "ABC School",
    "school_code": "ABC001",
    "admin_email": "admin@abcschool.com",
    "admin_password": "securepass123"
}

Response: {
    "success": true,
    "school_id": 1
}
```

## PDF Generation

### Generate Result Card
```bash
GET /api/generate-result-card/<student_id>
Headers: Authorization: Bearer <token>

Response: PDF file (ResultCard_001.pdf)
```

### Generate Fee Voucher
```bash
GET /api/generate-fee-voucher/<fee_id>
Headers: Authorization: Bearer <token>

Response: PDF file (FeeVoucher_001.pdf)
```

## Features

✅ JWT Token Authentication
✅ Multi-tenant System (school isolation)
✅ Secure Password Handling
✅ Result Card PDF Generation
✅ Fee Voucher PDF Generation
✅ Custom Templates Support
✅ Dark Green Theme (color-coded PDFs)
✅ Responsive PDF Layouts

## Next Phases

- Phase 5: Student Management APIs
- Phase 6: Attendance System
- Phase 7: Fee Management APIs
- Phase 8: Results Management APIs
- Phase 9: Reports & Export
- Phase 10: Frontend Integration
