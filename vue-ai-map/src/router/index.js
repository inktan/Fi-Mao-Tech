import { createRouter, createWebHistory } from 'vue-router'
import LngLatInfo from '@/views/LngLatInfo.vue'
import GdMap from '@/views/GdMap.vue'

const router = createRouter({
    history: createWebHistory(
        import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: GdMap
        },
        // {
        //     path: '/',
        //     name: 'home',
        //     component: LngLatInfo
        // },
        {
            path: '/about',
            name: 'about',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () =>
                import('@/views/LngLatInfo.vue')
        }
    ]
})

export default router