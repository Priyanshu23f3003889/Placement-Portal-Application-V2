import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../states/authState.js";

import Login from "../components/login.vue";
import Register from "../components/register.vue";
import AdminDashboard from "../components/adminDashboard.vue";
import CompanyDashboard from "../components/companyDashboard.vue";
import StudentDashboard from "../components/studentDashboard.vue";
import AdminCompanies from "../components/admin/AdminCompanies.vue";
import AdminStudents from "../components/admin/AdminStudents.vue";
import AdminDrives from "../components/admin/AdminDrives.vue";
import AdminApplications from "../components/admin/AdminApplications.vue";

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
      name : "admin-dashboard",
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
      ],
    },
    {
      path: "/company",
      name: "company-dashboard",
      component: CompanyDashboard,
      meta: { requiresAuth: true, role: "COMPANY" },
    },
    {
      path: "/student",
      name: "student-dashboard",
      component: StudentDashboard,
      meta: { requiresAuth: true, role: "STUDENT" },
    },
  ],
});

router.beforeEach((to, from) => {
  const authStore = useAuthStore();
  const isAuthenticated = !!authStore.token;

  if (to.name === "login" && isAuthenticated) {
    if (authStore.role === "ADMIN") return { path: "/admin/companies" };
    if (authStore.role === "COMPANY") return { name: "company-dashboard" };
    if (authStore.role === "STUDENT") return { name: "student-dashboard" };
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: "login" };
  }

  if (to.meta.requiresAuth && to.meta.role !== authStore.role) {
    if (authStore.role === "ADMIN") return { path: "/admin/companies" };
    if (authStore.role === "COMPANY") return { name: "company-dashboard" };
    if (authStore.role === "STUDENT") return { name: "student-dashboard" };
    return { name: "login" };
  }

  return true;
});

export default router;
