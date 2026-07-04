import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../states/authState.js";

import Login from "../components/login.vue";
import Register from "../components/register.vue";

import AdminDashboard from "../components/adminDashboard.vue";
import AdminCompanies from "../components/admin/AdminCompanies.vue";
import AdminStudents from "../components/admin/AdminStudents.vue";
import AdminDrives from "../components/admin/AdminDrives.vue";
import AdminApplications from "../components/admin/AdminApplications.vue";
import AdminPlacements from "../components/admin/AdminPlacements.vue";

import CompanyDashboard from "../components/companyDashboard.vue";
import CompanyProfile from "../components/company/companyProfile.vue";
import CompanyDrives from "../components/company/companyDrives.vue";
import NewDrive from "../components/company/companyNewDrive.vue";
import EditDrive from "../components/company/companyEditDrive.vue";
import CompanyApplications from "../components/company/companyApplications.vue";
import CompanyMakePlacement from "../components/company/companyMakePlacement.vue";
import companyPlacements from "../components/company/companyPlacements.vue";

import StudentDashboard from "../components/studentDashboard.vue";
import StudentProfile from "../components/student/studentProfile.vue";
import StudentCompanies from "../components/student/studentCompany.vue";
import StudentDrives from "../components/student/studentDrives.vue";
import StudentApplications from "../components/student/studentApplications.vue";
import studentPlacements from "../components/student/studentPlacements.vue";
import CompanyPlacements from "../components/company/companyPlacements.vue";


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      redirect: "/login",
    },
    {
      path: "/login",
      name: "login",
      component: Login,
    },
    {
      path: "/register",
      name: "register",
      component: Register,
    },
    {
      path: "/logout",
      name: "logout",
      beforeEnter: (to, from, next) => {
        const authStore = useAuthStore();
        authStore.logout();
        next({ name: "login" });
      },
    },
    {
      path: "/admin",
      name: "admin-dashboard",
      component: AdminDashboard,
      meta: { requiresAuth: true, role: "ADMIN" },
      redirect: "/admin/companies",
      children: [
        {
          path: "companies",
          name: "admin-companies",
          component: AdminCompanies,
        },
        { path: "students", name: "admin-students", component: AdminStudents },
        { path: "drives", name: "admin-drives", component: AdminDrives },
        {
          path: "applications",
          name: "admin-applications",
          component: AdminApplications,
        },
        {
          path: "placements",
          name: "admin-placements",
          component: AdminPlacements,
        },
      ],
    },
    {
      path: "/company",
      name: "company-dashboard",
      component: CompanyDashboard,
      meta: { requiresAuth: true, role: "COMPANY" },
      redirect: "/company/drives",
      children: [
        {
          path: "profile",
          name: "company-profile",
          component: CompanyProfile,
        },
        {
          path: "drives",
          name: "company-drives",
          component: CompanyDrives,
        },
        {
          path: "newdrive",
          name: "company-newdrive",
          component: NewDrive,
        },
        {
          path: "editdrive/:id",
          name: "company-editdrive",
          component: EditDrive,
        },
        {
          path: "applications",
          name: "company-applications",
          component: CompanyApplications,
        },
        {
          path: "makeplacement/:applicationId",
          name: "company-makePlacement",
          component: CompanyMakePlacement,
        },
        {
          path: "placements",
          name: "company-placements",
          component: CompanyPlacements,
        },
      ],
    },
    {
      path: "/student",
      name: "student-dashboard",
      component: StudentDashboard,
      meta: { requiresAuth: true, role: "STUDENT" },
      redirect: "/student/drives",
      children: [
        {
          path: "profile",
          name: "student-profile",
          component: StudentProfile,
        },
        {
          path: "companies",
          name: "student-companies",
          component: StudentCompanies,
        },
        {
          path: "drives",
          name: "student-drives",
          component: StudentDrives,
        },
        {
          path: "applications",
          name: "student-applications",
          component: StudentApplications,
        },
        {
          path: "placements",
          name: "student-placements",
          component : studentPlacements
        }
      ],
    },
  ],
});

router.beforeEach((to, from) => {
  const authStore = useAuthStore();
  const isAuthenticated = !!authStore.token;

  if (to.name === "login" && isAuthenticated) {
    if (authStore.role === "ADMIN") return { name: "admin-dashboard" };
    if (authStore.role === "COMPANY") return { name: "company-dashboard" };
    if (authStore.role === "STUDENT") return { name: "student-dashboard" };
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: "login" };
  }

  if (to.meta.requiresAuth && to.meta.role !== authStore.role) {
    if (authStore.role === "ADMIN") return { name: "admin-dashboard" };
    if (authStore.role === "COMPANY") return { name: "company-dashboard" };
    if (authStore.role === "STUDENT") return { name: "student-dashboard" };
    return { name: "login" };
  }

  return true;
});

export default router;
