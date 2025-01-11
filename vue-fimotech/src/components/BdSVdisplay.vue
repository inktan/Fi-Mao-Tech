<script setup>
const streetViews = [
  // { imgUrl: new URL('@/assets/img/960x720.jpg', import.meta.url).href, description: '960x720', time: '0.5' },
  { imgUrl: new URL('@/assets/img/1024x768.jpg', import.meta.url).href, description: '1024x768', time: '0.0' },
  { imgUrl: new URL('@/assets/img/1024x768.jpg', import.meta.url).href, description: '1024x768', time: '0.0' },
  { imgUrl: new URL('@/assets/img/2048x1536.jpg', import.meta.url).href, description: '2048x1536', time: '0.0' },
]

</script>

<template>
  <div class="row border-bottom pb-5 mt-3">
    <div v-for="(item, index) in streetViews" :key="item.imgUrl" class="col-md-4 col-sm-12 xs-padding wow fadeInUp"
      data-wow-delay="0ms" data-wow-duration="1000ms"
      style="visibility: visible; animation-duration: 1000ms; animation-delay: 0ms; animation-name: fadeInUp;">
      <div class="team-box text-center">
        <div class="team-thumb">
          <el-tooltip placement="top" effect="light" content="鼠标右键点击，在新标签中打开，查看图片真实清晰度">
            <!-- <template #content>
              <el-image :src="item.imgUrl" lazy />
            </template> -->
            <el-image :src="item.imgUrl" lazy />
          </el-tooltip>
          <!-- <img src="@\assets\img03.png" alt="img"> -->
        </div>
        <div class="team-content">
          <h5>分辨率：{{ item.description }}</h5>
          <span>耗时：{{ item.time }}s</span>
        </div>
      </div>
    </div>
  </div><!-- Team-1 -->
  <!-- <p class="text-center p-3 border-bottom fw-bold">鼠标右键点击，在新标签中打开图片,查看真实清晰度</p> -->
  <!-- <div class="b-example-divider"></div> -->
</template>

<style lang="less">
.b-example-divider {
  width: 100%;
  height: 0rem;
  background-color: rgba(0, 0, 0, .1);
  border: solid rgba(0, 0, 0, .15);
  border-width: 1px 0;
  box-shadow: inset 0 .5em 1.5em rgba(0, 0, 0, .1), inset 0 .125em .5em rgba(0, 0, 0, .15);
}

.team-thumb {
  margin-bottom: 30px;
  position: relative;

  // img {
  //   border: 10px solid #dd3b5b;
  //   border: 10px solid transparent;
  //   border-image: linear-gradient(to top, #33a9ee 0%, #141533 100%);
  //   border-image-slice: 1;
  //   box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.1);
  //   width: 150px;
  //   height: 150px;
  //   border-radius: 0;
  //   text-align: center;
  // }
}
</style>