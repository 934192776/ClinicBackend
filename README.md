# ClinicApp - Backend API (Django REST Framework)
ClinicApp System. It provides a secure, role-based RESTful API for managing doctors, patients, and appointments.

## Technologies Used
*   **Framework:** Django & Django REST Framework (DRF)
*   **Database:** SQLite (Development)
*   **Authentication:** Token Authentication
*   **Security:** Django-CORS-Headers, Custom Permissions

## How to Run Locally

1. **Clone the repository**
   git clone <your-repo-url>
   cd ClinicApp/backend
   
2. **Create and activate a virtual environment**
   python -m venv .venv
    # Windows:
      .\.venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
3. **Install dependencies**
   pip install -r requirements.txt
4. **Apply database migrations**
   python manage.py migrate
5. **Create a superuser (Admin)**
   python manage.py createsuperuser
6. **Run the server**
   python manage.py runserver

** The API will be available at http://127.0.0.1:8000/api/ **

** Test Credentials**
Admin (Superuser): admin / Clinic@2026

Doctor (Staff): doctor1 / Clinic@2026

Patient: patient1 / Clinic@2026

** Automated Testing**
This project includes both Postman collections and Pytest scripts for API automation.
GitHub Actions is configured to run pytest automatically on every push to the main branch.