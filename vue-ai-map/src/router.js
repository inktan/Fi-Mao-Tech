import { createRouter, createWebHistory } from 'vue-router'
import LngLatInfo from '@/views/LngLatInfo.vue'
import GdMap from '@/views/GdMap.vue'
import Layout from '@/components/Layout.vue'

const routes = [{
        name: 'Home',
        path: '/',
        component: Layout,
        redirect: '/index',
        children: [{
            name: 'Index',
            path: 'index',
            meta: { title: '主页', showInMenu: false, icon: 'el-icon-wind-power' },
            component: () =>
                import ('./views/Index.vue')
        }, ]
    },
    {
        name: 'about',
        path: '/about',
        // route level code-splitting
        // this generates a separate chunk (About.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () =>
            import ('@/views/LngLatInfo.vue')
    }
]

const router = createRouter({
    history: createWebHistory(
        import.meta.env.BASE_URL),
    routes: routes
})

export {
    router,
    routes
}