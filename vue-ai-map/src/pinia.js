import { defineStore } from 'pinia'

export const useProjectStore = defineStore('storeProject', {
    state: () => ({
        count: 0,

        navWidth: 200, // 导航宽度
        windowInsets: { // 窗口数据
            height: 0,
            width: 0
        },
        navMenuCollapse: false, // navMenu 是否折叠状态
    }),

    getters: {
        doubleCount: (state) => state.count * 2,
        isInPortraitMode(state) {
            return state.windowInsets.height > state.windowInsets.width
        },
    },

    actions: {
        increment() {
            this.count++
        },
    },
})