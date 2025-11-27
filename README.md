# Smart Canteen Menu (Django)

Features:
- Django + REST API (DRF)
- Bootstrap responsive UI
- Login & Registration
- Admin dashboard for orders and items
- Dark / Light mode toggle
- Search & filter menu
- Cart with add / update quantity / remove
- Sample menu seeding command

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # create admin
python manage.py seed_menu       # load sample items
python manage.py runserver
```

Open:

- Menu: http://127.0.0.1:8000/menu/
- Cart: http://127.0.0.1:8000/cart/
- Dashboard (staff only): http://127.0.0.1:8000/dashboard/
- API items: http://127.0.0.1:8000/api/items/
```

---
## Upgraded features added by assistant
Files added under `static/enhancements/` and `templates/enhancements/` and `templates/menu_app/menu_pro.html`.
Included features:
- Modern menu card UI (menu_pro.html)
- CSS: menu_pro.css, dark_mode.css
- JS: menu_pro.js, dark_toggle.js, register_sw.js
- PWA manifest + serviceworker (static/enhancements/pwa/)
- Admin redesign template (templates/enhancements/admin_redesign.html)

### How to view upgraded menu page (locally)
1. Ensure static files are collected/served. For development, run:
   ```bash
   python manage.py runserver
   ```
2. If your menu view is `menu/` or `/menu/`, replace the template used by that view to `menu_app/menu_pro.html` or update view to render it.
   Example (quick test): open Django shell and render via template:
   - Open `menu_app/views.py` and create a new view `menu_pro` that renders `menu_app/menu_pro.html` with `items = MenuItem.objects.all()`.
3. Admin redesign can be accessed by creating a superuser and visiting `/admin/` then mapping a view to the `templates/enhancements/admin_redesign.html` if desired.

### Render deployment notes (summary)
- Create GitHub repo, push project.
- On Render: create Web Service, build command: `pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput`
- Start command: `gunicorn smart_canteen.wsgi:application`
- Set environment variables: DJANGO_SECRET_KEY, ALLOWED_HOSTS, DATABASE_URL (if using Postgres), DEBUG=False
