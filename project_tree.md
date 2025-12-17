# Project tree: Cohai_Stretching

```text
Cohai_Stretching
├── alembic
│   ├── versions
│   │   ├── 2b06bc1fb6c1_add_attendances_table_fixed.py
│   │   ├── 4954ef89053d_add_users_table.py
│   │   ├── 5151f9ecbb5e_add_user_id_to_trainers.py
│   │   ├── 5b2a7884f027_sync_models_with_orm.py
│   │   ├── 6cbb6e1faef6_add_message_column_to_leads.py
│   │   ├── 76d7baddc94f_add_memberships_table.py
│   │   ├── 91ee455cead4_add_attendances_table.py
│   │   ├── b9a6b29d0915_add_lead_status_and_trainer_admin_.py
│   │   ├── d7f7e7bf6898_baseline.py
│   │   └── deec30786f53_add_user_id_to_leads.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── app
│   ├── api
│   │   └── v1
│   │       ├── admin
│   │       │   ├── __init__.py
│   │       │   ├── admin_class_sessions.py
│   │       │   ├── admin_leads.py
│   │       │   ├── admin_locations.py
│   │       │   └── admin_memberships.py
│   │       ├── me
│   │       │   ├── __init__.py
│   │       │   ├── booking.py
│   │       │   ├── calendar.py
│   │       │   ├── classes.py
│   │       │   ├── leads.py
│   │       │   ├── memberships.py
│   │       │   └── profile.py
│   │       ├── public
│   │       │   ├── __init__.py
│   │       │   ├── leads.py
│   │       │   ├── locations.py
│   │       │   ├── memberships.py
│   │       │   ├── program_types.py
│   │       │   └── schedule.py
│   │       ├── trainer
│   │       │   ├── __init__.py
│   │       │   └── trainer_leads.py
│   │       ├── __init__.py
│   │       ├── admin_class_sessions.py
│   │       ├── admin_leads.py
│   │       ├── admin_locations.py
│   │       ├── admin_memberships.py
│   │       ├── auth.py
│   │       ├── deps.py
│   │       ├── deps_auth.py
│   │       └── trainer_leads.py
│   ├── core
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── db
│   │   ├── base.py
│   │   └── session.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── attendance.py
│   │   ├── class_session.py
│   │   ├── lead.py
│   │   ├── location.py
│   │   ├── location_area.py
│   │   ├── membership.py
│   │   ├── program_type.py
│   │   ├── trainer.py
│   │   └── user.py
│   ├── repositories
│   │   ├── class_session_repo.py
│   │   ├── lead_repo.py
│   │   ├── location_repo.py
│   │   ├── membership_repo.py
│   │   ├── program_type_repo.py
│   │   ├── user_membership_repo.py
│   │   └── user_repo.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── attendance.py
│   │   ├── calendar.py
│   │   ├── class_session.py
│   │   ├── lead.py
│   │   ├── location.py
│   │   ├── membership.py
│   │   ├── program_type.py
│   │   ├── trainer.py
│   │   └── user_auth.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── attendance_service.py
│   │   ├── auth_service.py
│   │   ├── class_session_service.py
│   │   ├── lead_service.py
│   │   ├── location_service.py
│   │   ├── membership_service.py
│   │   ├── schedule_service.py
│   │   ├── user_membership_service.py
│   │   └── user_service.py
│   ├── tools
│   │   ├── logs
│   │   ├── bootstrap_db.py
│   │   ├── check_bootstrap.py
│   │   ├── check_sqlalchemy.py
│   │   ├── create_superadmin.py
│   │   ├── debug_imports.py
│   │   ├── dump_schema.py
│   │   ├── plan_tracker.py
│   │   └── show_env.py
│   ├── __init__.py
│   └── main.py
├── docs
│   ├── db_schema_v0.md
│   ├── db_schema_v1_draft.md
│   └── schema_2025-11-24.sql
├── frontend
│   └── frontend
│       └── index.html
├── frontend-react
│   ├── public
│   │   ├── images
│   │   └── vite.svg
│   ├── src
│   │   ├── api
│   │   │   └── adminRequest.js
│   │   ├── assets
│   │   │   └── react.svg
│   │   ├── components
│   │   │   ├── auth
│   │   │   │   ├── RequireAuth.jsx
│   │   │   │   └── RequireRole.jsx
│   │   │   ├── domain
│   │   │   │   ├── LeadForm.jsx
│   │   │   │   ├── LocationSelect.jsx
│   │   │   │   ├── MembershipList.jsx
│   │   │   │   └── ScheduleList.jsx
│   │   │   ├── layout
│   │   │   │   ├── Footer.jsx
│   │   │   │   ├── Header.jsx
│   │   │   │   └── Layout.jsx
│   │   │   └── ui
│   │   │       └── Card.jsx
│   │   ├── context
│   │   │   └── AuthContext.jsx
│   │   ├── pages
│   │   │   ├── admin
│   │   │   │   ├── AdminDashboardLayout.jsx
│   │   │   │   ├── ClassSessionsPage.jsx
│   │   │   │   ├── DashboardHome.jsx
│   │   │   │   ├── LeadsPage.jsx
│   │   │   │   ├── LocationsPage.jsx
│   │   │   │   └── MembershipsPage.jsx
│   │   │   ├── client
│   │   │   │   ├── client-dashboard
│   │   │   │   │   ├── calendar.css
│   │   │   │   │   ├── classes.css
│   │   │   │   │   ├── common.css
│   │   │   │   │   ├── layout.css
│   │   │   │   │   ├── leads.css
│   │   │   │   │   └── memberships.css
│   │   │   │   ├── ClassesPage.jsx
│   │   │   │   ├── ClientDashboardLayout.jsx
│   │   │   │   ├── DashboardHome.jsx
│   │   │   │   ├── LeadsPage.jsx
│   │   │   │   ├── MembershipsPage.jsx
│   │   │   │   ├── ProfilePage.jsx
│   │   │   │   └── SchedulePage.jsx
│   │   │   ├── CabinetRedirect.jsx
│   │   │   ├── ContactsPage.jsx
│   │   │   ├── FormatsPage.jsx
│   │   │   ├── HomePage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── NewbieGuidePage.jsx
│   │   │   ├── PricesPage.jsx
│   │   │   ├── SchedulePage.jsx
│   │   │   └── TrainersPage.jsx
│   │   ├── api.js
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── README.md
│   ├── tailwind.config.js
│   └── vite.config.js
├── logs
├── tests
│   ├── conftest.py
│   ├── test_admin_access.py
│   ├── test_admin_class_sessions.py
│   ├── test_admin_leads.py
│   ├── test_admin_locations.py
│   ├── test_admin_memberships.py
│   ├── test_auth.py
│   ├── test_me_booking.py
│   ├── test_me_calendar.py
│   ├── test_me_classes.py
│   ├── test_me_leads.py
│   ├── test_me_memberships.py
│   ├── test_me_profile.py
│   ├── test_public_leads.py
│   ├── test_public_locations.py
│   ├── test_public_memberships.py
│   ├── test_public_program_types.py
│   └── test_public_schedule.py
├── alembic.ini
├── backend_locations_api_v1.txt
├── cohai_backend_plan.md
├── cohai_site_master_plan.md
├── cohai_stretching.db
├── collect_files.py
├── dump_project.py
├── dump_tree.py
├── frontend_admin_pages_v1.txt
├── plan_backend_refactor.md
├── plan_frontend_refactor.md
├── project_architecture.md
├── project_tree.md
├── requirements.txt
├── search_in_project.py
├── snapshot_admin_lk_infra.txt
├── snapshot_admin_lk_plan.txt
└── snapshot_admin_lk_schemas_services.txt
```
