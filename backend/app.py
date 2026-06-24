from datetime import timedelta
from os import makedirs, path

from database.models import (
    Role,
    User,
    db,
)

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash

DB_PATH = path.join(
    path.abspath(path.dirname(__file__)), "./database/db_dir/placement.db"
)

if not path.exists(path.dirname(DB_PATH)):
    makedirs(path.dirname(DB_PATH))


def createApp():

    app = Flask(
        __name__,
        template_folder="../frontend/dist",
        static_folder="../frontend/dist/assets",
        static_url_path="/assets",
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SECRET_KEY"] = "sectet_key_to_sign_jwt_tokens_and_other_cookies"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(weeks=4)

    db.init_app(app)
    jwt = JWTManager(app)

    with app.app_context():
        db.create_all()

        roles = ["ADMIN", "COMPANY", "STUDENT"]

        for r in roles:
            role_exists = db.session.execute(db.select(Role).filter_by(name=r)).scalar()

            if not role_exists:
                role = Role(name=r, description=f"The {r} role.")
                db.session.add(role)
                print(f"Created Role: {r}")
        db.session.commit()

        admin_email = "admin@email.com"
        admin_exists = db.session.execute(
            db.select(User).filter_by(email=admin_email)
        ).scalar()

        if not admin_exists:
            admin_role = db.session.execute(
                db.select(Role).filter_by(name="ADMIN")
            ).scalar()

            hashed_password = generate_password_hash("123")

            admin = User(
                email=admin_email,
                password=hashed_password,
                roleid=admin_role.id,
                isActive=True,
            )

            db.session.add(admin)
            db.session.commit()
            print(f"Created Admin User: {admin_email}")
        else:
            print("Admin already Exists")

    app.app_context().push()
    CORS(app)

    return app


if __name__ == "__main__":
    app = createApp()
    import controllers.adminController
    import controllers.authController
    import controllers.companyController
    import controllers.mainController
    import controllers.studentController

    app.run(debug=True, host="0.0.0.0", port=80)
