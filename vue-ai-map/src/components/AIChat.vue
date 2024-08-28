<script lang="ts" setup>
import { ref, reactive, onBeforeMount, onMounted, onUpdated, computed, defineComponent, nextTick, watch, onUnmounted } from 'vue';
import { RouterLink, RouterView } from 'vue-router'
import type { ChatMessage } from "@/types";
import { postZhiPuAiChat } from '@/api';

// import { md } from "@/libs/markdown";

const isButtonVisible = ref(true);
const isChatBoxVisible = ref(false);

let isTalking = ref(false);

let messageContent = ref("");
const chatListDom = ref<HTMLDivElement>();
const decoder = new TextDecoder("utf-8");
const roleAlias = {
    user: "Me",
    assistant: "Ai",
    system: "System"
};
const messageList = ref<ChatMessage[]>([
    {
        role: "system",
        content: "你是一个聪明且富有灵魂的导航助手，尽可能详细回答地图导航相关的问题。",
    },
    {
        role: "assistant",
        content: '你好，我是地图导航助手AI模型，我可以回答与地图导航相关的问题。'
    },
]);

function toggleChat() {
    isButtonVisible.value = !isButtonVisible.value;
    isChatBoxVisible.value = !isChatBoxVisible.value;
}

const sendOrSave = () => {
    if (!messageContent.value.length) return;
    // console.log(messageContent.value)
    sendChatMessage()
};

const sendChatMessage = async (content: string = messageContent.value) => {
    try {
        isTalking.value = true;
        if (messageList.value.length === 2) {
            messageList.value.pop();
        }
        messageList.value.push({ role: "user", content }); // 用户
        clearMessageContent();
        messageList.value.push({ role: "assistant", content: "" }); // 客户端

        const resp = await postZhiPuAiChat(messageList.value)
        const reader = resp.body.getReader();
        await readStream(reader);

    } catch (error: any) {
        appendLastMessageContent(error);
    } finally {
        isTalking.value = false;
    }
};

const appendLastMessageContent = (content: string) =>
    (messageList.value[messageList.value.length - 1].content += content);

const readStream = async (
    reader: ReadableStreamDefaultReader<Uint8Array>,
    // status: number
) => {

    let partialLine = "";

    while (true) {
        // eslint-disable-next-line no-await-in-loop
        const { value, done } = await reader.read();
        if (done) break;

        const decodedText = decoder.decode(value, { stream: true });

        // if (status !== 200) {
        //     const json = JSON.parse(decodedText); // start with "data: "
        //     const content = json.error.message ?? decodedText;
        //     appendLastMessageContent(content);
        //     return;
        // }

        const chunk = partialLine + decodedText;
        const newLines = chunk.split(/\r?\n/);
        // partialLine = newLines.pop() ?? "";
        for (const line of newLines) {
            if (line.length === 0) continue; // ignore empty message
            if (line.startsWith(":")) continue; // ignore sse comment message
            if (line === "data: [DONE]") return; //

            // const json = JSON.parse(line.substring(6)); // start with "data: "
            // let content =
            //     status === 200
            //         ? json.choices[0].delta.content ?? ""
            //         : json.error.message;
            let content = line

            if (content.startsWith("？")) content = content.slice(1);; // ignore sse comment message
            if (content.startsWith("?")) content = content.slice(1);; // ignore sse comment message
            if (content.startsWith("。")) content = content.slice(1);; // ignore sse comment message
            if (content.startsWith(".")) content = content.slice(1);; // ignore sse comment message
            if (content.startsWith(":")) content = content.slice(1);; // ignore sse comment message
            if (content.startsWith("：")) content = content.slice(1);; // ignore sse comment message
            appendLastMessageContent(content);
        }
    }
};

const clearMessageContent = () => (messageContent.value = "");

watch(messageList.value, () => nextTick(() => {
    if (chatListDom.value) {
        chatListDom.value.scrollTop = chatListDom.value.scrollHeight;
    }
}));

const activeIndex = ref(null); // 用于跟踪当前鼠标悬停的链接索引
function handleMouseOver(index) {
    activeIndex.value = index;
}
function handleMouseLeave(index) {
    activeIndex.value = null;
}

</script>

<template>
    <div class="aichat-container">
        <el-button class="open-btn" :class="{ 'moving-button': isButtonVisible }" @click="toggleChat" size="large"
            type="primary">
            <el-icon>
                <ChatDotRound />
            </el-icon>AI助理
        </el-button>

        <div class="chat-box" :class="{ visible: isChatBoxVisible }">
            <div class="header-content">
                AI导航助理
            </div>
            <div class="chat-content" ref="chatListDom">
                <div class="messageItem" v-for="(item, index)  in messageList.filter((v) => v.role !== 'system')"
                    @mouseover="handleMouseOver(index)" @mouseleave="handleMouseLeave(index)"
                    :class="{ 'with-overlay': activeIndex === index }">
                    <div class="ai-role">
                        <div class="role">{{ roleAlias[item.role] }}：</div>
                        <Copy v-if="activeIndex === index" class="role-copy" :content="item.content" />
                    </div>
                    <div class="ai-content">
                        <div class="content" v-if="item.content" v-html="item.content"></div>
                        <!-- <Loding v-else /> -->
                    </div>
                </div>
            </div>
            <div class="input-btn-container">
                <div class="input-btn">
                    <el-input @keyup.enter="sendOrSave" type="textarea" resize="none" v-model="messageContent"
                        placeholder="请输入……" size="large" :maxlength="200" show-word-limit
                        :autosize="{ minRows: 2, maxRows: 4 }">
                    </el-input>
                    <el-button class="btnSearch" type="primary" @click="sendOrSave()">发送</el-button>
                </div>
            </div>
            <el-button class="close-btn" type="primary" @click="toggleChat">
                <el-icon>
                    <Right />
                </el-icon>
            </el-button>
        </div>

    </div>
</template>

<style lang="less" scoped>
@import "@/styles/var.less";

.aichat-container {
    position: fixed;
    right: -600px;
    bottom: 10px;
    z-index: 10000;

    .open-btn {
        position: fixed;
        padding-left: 10px;
        justify-content: flex-start;
        width: 120px;
        border-radius: 30px;
        right: -50px;
        bottom: 200px;
        transition: all 0.5s ease;
        transform: translateX(100px);

        @keyframes moveLeftRight {
            0% {
                transform: translateX(0);
            }

            50% {
                transform: translateX(20px);
            }

            100% {
                transform: translateX(0);
            }
        }

        &.moving-button {
            animation: moveLeftRight 2s infinite alternate ease-in-out;
        }
    }

    .chat-box {
        position: relative;
        border: 1px solid #b1b3b8;
        border-radius: 20px;
        // padding: 20px;
        box-shadow: 5px 5px 10px 0 rgba(0, 0, 0, 0.15);
        background-color: #f4f4f5;
        transition: all 0.5s ease;

        width: 520px;
        height: 600px;
        // 保证AI聊天位于最上层
        overflow: hidden;

        &.visible {
            transform: translateX(-610px);
        }

        .header-content {
            display: flex;
            align-items: center;
            background-color: #e9e9eb;
            height: 30px;
            padding-left: 15px;
        }

        .chat-content {
            background-color: #f4f4f5;
            padding: 2px;
            width: 100%;
            height: 500px;
            overflow-y: auto;
            transition: all 0.5s ease;

            .messageItem {
                border-radius: 5px;
                padding: 8px;
                line-height: 16px;

                &.with-overlay {
                    background-color: #d9ecff;
                }

                .ai-role {
                    display: flex;
                    justify-content: space-between;

                    .role {
                        font-weight: bold;
                    }

                    .role-copy {
                        font-size: 12px;

                    }
                }

                .ai-content {
                    margin: 5px 0;

                    .content {
                        font-size: 12px;
                    }
                }
            }
        }

        .input-btn-container {
            background-color: #e9e9eb;

            .input-btn {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 70px;
                margin: 0 5px;

                .el-button {
                    margin-left: 5px;
                }
            }
        }

        .close-btn {
            position: absolute;
            right: 0;
            top: 0;
            transform: translate(-20px, 3px);
            width: 10px;
        }
    }
}
</style>
