<template>
    <div class="copyright">
        <dl>
            <dt>更新：</dt>
            <dd>{{ packageInfo['date-update'] }}</dd>
        </dl>
        <dl>
            <dt>版本：</dt>
            <dd>v{{ packageInfo['version'] }}</dd>
        </dl>
    </div>
</template>

<script lang="ts" setup>
import { ref, reactive, toRefs } from 'vue'
import packageInfo from "@/../package.json"

</script>

<style lang="less">
.copyright{
    border-top: 1px solid;
    display: flex;
    flex-flow: column nowrap;
    justify-content: flex-end;
    padding: 30px 20px;
    dl{
        font-size: 0.7rem;
        line-height: 1.5;
        // color: $text-subtitle;
        display: flex;
        justify-content: space-between;
    }
}
</style>