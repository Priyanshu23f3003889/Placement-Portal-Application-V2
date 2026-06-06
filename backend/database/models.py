import enum
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import CheckConstraint, ForeignKey
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class DriveStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    CLOSED = "CLOSED"


class ApplicationStatus(str, enum.Enum):
    APPLIED = "APPLIED"
    SHORTLISTED = "SHORTLISTED"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"


class Branch(str, enum.Enum):
    CSE = "Computer Science and Engineering"
    ECE = "Electronics and Communication"
    MECH = "Mechanical Engineering"
    CIVIL = "Civil Engineering"
    EE = "Electrical Engineering"


class Role(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str]

    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)  # bcrypt
    roleid: Mapped[int] = mapped_column(ForeignKey("role.id"), nullable=False)
    isActive: Mapped[bool] = mapped_column(nullable=False, default=True)

    role: Mapped["Role"] = relationship(back_populates="users")


class Student(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    userId: Mapped[int] = mapped_column(ForeignKey("user.id"))
    name: Mapped[str] = mapped_column(nullable=False)
    branch: Mapped[Branch] = mapped_column(Enum(Branch), nullable=False)
    cgpa: Mapped[float] = mapped_column(
        CheckConstraint("cgpa <= 10.0 AND cgpa >= 0.0"), nullable=False
    )
    resumeUrl: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship()
    applications: Mapped[list["Application"]] = relationship(back_populates="student")
    placements: Mapped[list["Placement"]] = relationship(back_populates="student")


class Company(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    userId: Mapped[int] = mapped_column(ForeignKey("user.id"))
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    hrContact: Mapped[str] = mapped_column(unique=True, nullable=False)
    website: Mapped[str] = mapped_column(unique=True, nullable=False)
    isApproved: Mapped[bool] = mapped_column(nullable=False, default=False)

    user: Mapped["User"] = relationship()
    drives: Mapped[list["PlacementDrive"]] = relationship(back_populates="company")
    placements: Mapped[list["Placement"]] = relationship(back_populates="company")


class PlacementDrive(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    companyId: Mapped[int] = mapped_column(ForeignKey("company.id"))
    jobTitle: Mapped[str] = mapped_column(nullable=False)
    jobDescription: Mapped[str] = mapped_column(nullable=False)
    deadline: Mapped[datetime] = mapped_column(nullable=False)
    branch: Mapped[Branch] = mapped_column(Enum(Branch), nullable=False)
    cgpa: Mapped[float] = mapped_column(
        CheckConstraint("cgpa <= 10.0 AND cgpa >= 0.0"), nullable=False
    )
    year: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[DriveStatus] = mapped_column(
        Enum(DriveStatus), nullable=False, default=DriveStatus.PENDING
    )

    company: Mapped["Company"] = relationship(back_populates="drives")
    applications: Mapped[list["Application"]] = relationship(back_populates="drive")
    placements: Mapped[list["Placement"]] = relationship(back_populates="drive")


class Application(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    studentId: Mapped[int] = mapped_column(ForeignKey("student.id"))
    driveId: Mapped[int] = mapped_column(ForeignKey("placement_drive.id"))
    applicationDate: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.APPLIED, nullable=False
    )

    student: Mapped["Student"] = relationship(back_populates="applications")
    drive: Mapped["PlacementDrive"] = relationship(back_populates="applications")


class Placement(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    studentId: Mapped[int] = mapped_column(ForeignKey("student.id"))
    driveId: Mapped[int] = mapped_column(
        ForeignKey("placement_drive.id"), nullable=True
    )
    companyId: Mapped[int] = mapped_column(ForeignKey("company.id"))
    position: Mapped[str] = mapped_column(nullable=False)
    salary: Mapped[float] = mapped_column(nullable=True)

    student: Mapped["Student"] = relationship(back_populates="placements")
    drive: Mapped["PlacementDrive"] = relationship(back_populates="placements")
    company: Mapped["Company"] = relationship(back_populates="placements")
