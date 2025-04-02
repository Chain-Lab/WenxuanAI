<template>
  <div class="live2d-container" :style="{ visibility: visible ? 'visible' : 'hidden' }">
    <canvas id="myCanvas" />
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from "vue";
import * as PIXI from "pixi.js";
import { Live2DModel } from "pixi-live2d-display/cubism4";

// 定义属性
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
});

// 导出方法供父组件调用
const autoMouthMove = (start) => {
  if (!model || !model.internalModel) {
    console.warn('模型尚未加载完成');
    return;
  }

  if (start) {
    if (!intervalId.value) {
      intervalId.value = setInterval(() => {
        let n = Math.random();
        model.internalModel.coreModel.setParameterValueById("ParamMouthOpenY", n);
      }, 100);
    }
  } else {
    if (intervalId.value) {
      clearInterval(intervalId.value);
      intervalId.value = null;
      model.internalModel.coreModel.setParameterValueById("ParamMouthOpenY", 0);
    }
  }
};

defineExpose({ autoMouthMove });

window.PIXI = PIXI;

// 设置 PIXI 全局选项
PIXI.settings.PRECISION_FRAGMENT = PIXI.PRECISION.HIGH;
PIXI.settings.SPRITE_MAX_TEXTURES = Math.min(PIXI.settings.SPRITE_MAX_TEXTURES, 16);

// 预加载纹理资源
PIXI.Loader.shared.pre((resource) => {
  if (resource.extension === 'png' || resource.extension === 'jpg') {
    resource.loadType = PIXI.LoaderResource.LOAD_TYPE.IMAGE;
  }
});

let app;
let model;
const intervalId = ref(null);
const modelLoaded = ref(false);

// 提前开始模型加载
const modelPromise = preloadModel();

onMounted(() => {
  // 立即初始化模型，不管是否可见
  init();
});

onBeforeUnmount(() => {
  if (intervalId.value) {
    clearInterval(intervalId.value);
  }
  app = null;
  model = null;
});

// 预加载模型资源
async function preloadModel() {
  try {
    return await Live2DModel.from("/haru_greeter_pro_jp/haru_greeter_pro_jp/runtime/haru_greeter_t05.model3.json", {
      autoInteract: false,
      autoUpdate: false, // 减少自动更新
    });
  } catch (error) {
    console.error('模型预加载失败:', error);
    return null;
  }
}

const init = async () => {
  // 创建 PIXI 应用和画布
  app = new PIXI.Application({
    view: document.querySelector("#myCanvas"),
    resizeTo: document.querySelector("#myCanvas"),
    backgroundAlpha: 0,
    width: 300,
    height: 400,
    autoStart: true, // 确保即使不可见也会继续渲染
    resolution: window.devicePixelRatio || 1, // 考虑设备像素比
    antialias: false, // 关闭抗锯齿提高性能
    powerPreference: 'high-performance'
  });

  try {
    console.log('等待模型加载...');
    
    // 使用预加载的模型
    model = await modelPromise;
    
    if (!model) {
      throw new Error('模型加载失败');
    }

    model.scale.set(0.2);
    model.y = 0;
    model.x = -100;
    app.stage.addChild(model);
    
    // 减少更新频率，只有在需要时更新
    app.ticker.remove(app.render, app);
    app.ticker.add(() => {
      if (props.visible || intervalId.value) {
        model.update(app.ticker.deltaMS);
        app.render();
      }
    });
    
    modelLoaded.value = true;
    console.log('模型加载完成');
  } catch (error) {
    console.error('模型初始化失败:', error);
  }
};
</script>

<style scoped>
.live2d-container {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1000;
  /* 使用 visibility 而不是 display，这样模型会一直保持加载状态 */
  visibility: hidden;
}

#myCanvas {
  width: 300px;
  height: 400px;
  background: transparent;
}
</style> 